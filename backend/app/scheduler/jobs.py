"""定时任务：收盘后自动分析（数据 -> 策略 -> 计划 -> 落库 -> 报告）。"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings
from app.data.base import DataProvider
from app.data.provider import create_provider
from app.planner.service import build_plan
from app.repository import plans as plans_repo
from app.repository import quotes as quotes_repo
from app.repository import reports as reports_repo
from app.repository import strategy_runs as runs_repo
from app.repository.db import SessionLocal
from app.strategy.base import Candidate, StrategyContext
from app.strategy.registry import discover_plugins, get_strategy
from shared.enums import PlanStatus

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _today() -> date:
    return datetime.now(ZoneInfo(get_settings().timezone)).date()


def _start(plan_date: date) -> date:
    return plan_date - timedelta(days=get_settings().quote_lookback_days)


def _build_report(
    plan_date: date,
    plan,
    candidates: list[Candidate],
    quotes_codes: list[str],
) -> dict:
    return {
        "plan_date": plan_date.isoformat(),
        "candidate_count": len(candidates),
        "top_candidates": [
            {"code": c.code, "score": c.score, "reason": c.reason}
            for c in candidates[:10]
        ],
        "plan_items": len(plan.items),
        "quotes_codes": quotes_codes,
        "generated_at": datetime.now(UTC).isoformat(),
    }


def run_daily_analysis(
    plan_date: date | None = None,
    provider: DataProvider | None = None,
    strategy_name: str | None = None,
) -> dict:
    """收盘后自动分析：拉取行情 -> 运行策略 -> 生成计划 -> 落库 -> 每日报告。

    参数可注入 provider / strategy_name 便于测试；默认读取配置。
    """
    settings = get_settings()
    plan_date = plan_date or _today()
    provider = provider or create_provider()
    strategy_name = strategy_name or settings.strategy_name

    db = SessionLocal()
    try:
        # 1) 股票基础信息（元数据，失败不阻断）
        try:
            basics = provider.fetch_stock_basics()
            added = quotes_repo.upsert_stocks(db, basics)
            logger.info("stocks upserted: added=%d total=%d", added, len(basics))
        except Exception as exc:  # noqa: BLE001
            logger.warning("fetch stock basics failed: %s", exc)

        # 2) 拉取跟踪股票行情
        codes = settings.tracked_code_list or quotes_repo.list_tracked_codes(db)
        bars_by_code: dict[str, list[dict]] = {}
        if not codes:
            logger.warning("no tracked stocks configured (STOCK_AGENT_TRACKED_STOCKS)")
        for code in codes:
            try:
                bars = provider.fetch_daily(code, _start(plan_date), plan_date)
                if not bars:
                    continue
                saved = quotes_repo.save_quotes(db, bars)
                logger.info("quotes %s: saved=%d bars=%d", code, saved, len(bars))
                bars_by_code[code] = [b.__dict__ for b in bars]
            except Exception as exc:  # noqa: BLE001
                logger.warning("fetch daily %s failed: %s", code, exc)

        # 3) 运行策略
        discover_plugins()
        strategy = get_strategy(strategy_name)
        ctx = StrategyContext(plan_date=plan_date, quotes=bars_by_code)
        candidates = strategy.run(ctx)
        logger.info("strategy %s candidates: %d", strategy_name, len(candidates))
        runs_repo.record_run(db, strategy_name, plan_date, candidates)

        # 4) 生成并保存交易计划
        plan = build_plan(plan_date, candidates, total_budget=settings.plan_budget)
        saved_plan = plans_repo.save_plan(
            db,
            plan_date=plan_date,
            status=PlanStatus.PUBLISHED.value,
            total_budget=settings.plan_budget,
            items=[item.model_dump(mode="json", exclude_none=True) for item in plan.items],
        )
        logger.info("plan saved id=%d items=%d", saved_plan.id, len(saved_plan.items))

        # 5) 生成每日报告
        report = _build_report(plan_date, saved_plan, candidates, sorted(bars_by_code))
        reports_repo.save_report(db, report_date=plan_date.isoformat(), summary=report)
        logger.info("daily analysis done: %s", plan_date)
        return report
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    settings = get_settings()
    if not settings.enable_scheduler:
        logger.info("scheduler disabled by config (STOCK_AGENT_ENABLE_SCHEDULER=false)")
        return None
    _scheduler = BackgroundScheduler(timezone=settings.timezone)
    _scheduler.add_job(
        run_daily_analysis,
        "cron",
        hour=15,
        minute=30,
        id="daily_analysis",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("scheduler started: daily_analysis at 15:30 %s", settings.timezone)
    return _scheduler
