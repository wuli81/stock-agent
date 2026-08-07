"""命令行工具：数据获取与手动运行分析。

用法：
    python -m app.cli seed-basics
    python -m app.cli fetch-daily --codes 600000,000001 --days 60
    python -m app.cli run-analysis --date 2026-08-07
"""

from __future__ import annotations

import argparse
import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.data.provider import create_provider
from app.repository import quotes as quotes_repo
from app.repository.db import SessionLocal
from app.scheduler.jobs import run_daily_analysis

logger = logging.getLogger("cli")


def _today() -> date:
    return datetime.now(ZoneInfo(get_settings().timezone)).date()


def _seed_basics(args) -> int:
    provider = create_provider()
    basics = provider.fetch_stock_basics()
    db = SessionLocal()
    try:
        added = quotes_repo.upsert_stocks(db, basics)
    finally:
        db.close()
    print(f"seed-basics: total={len(basics)} added={added}")
    return 0


def _fetch_daily(args) -> int:
    provider = create_provider()
    end = _today()
    start = end - timedelta(days=args.days)
    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    db = SessionLocal()
    saved_total = 0
    try:
        for code in codes:
            bars = provider.fetch_daily(code, start, end)
            saved = quotes_repo.save_quotes(db, bars) if bars else 0
            saved_total += saved
            print(f"fetch-daily {code}: bars={len(bars)} saved={saved}")
    finally:
        db.close()
    print(f"fetch-daily done, saved={saved_total}")
    return 0


def _run_analysis(args) -> int:
    plan_date = date.fromisoformat(args.date) if args.date else None
    report = run_daily_analysis(plan_date=plan_date)
    print(f"run-analysis: {report}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="stock-agent 后端命令行工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_seed = sub.add_parser("seed-basics", help="拉取全部 A 股基础信息并入库")
    p_seed.set_defaults(func=_seed_basics)

    p_fetch = sub.add_parser("fetch-daily", help="拉取指定股票日线行情并入库")
    p_fetch.add_argument("--codes", required=True, help="逗号分隔的股票代码，如 600000,000001")
    p_fetch.add_argument("--days", type=int, default=60, help="回溯天数")
    p_fetch.set_defaults(func=_fetch_daily)

    p_run = sub.add_parser("run-analysis", help="运行一次收盘分析（数据->策略->计划->报告）")
    p_run.add_argument("--date", default=None, help="计划日期 YYYY-MM-DD，默认今天")
    p_run.set_defaults(func=_run_analysis)
    return parser


def main() -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    args = _build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
