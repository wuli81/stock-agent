"""trade-executor v0.1 命令行入口。

用法示例（Demo 模式，不连接真实券商）：
    python -m executor.main --config config.toml --date 2026-08-08 --mode manual
"""

from __future__ import annotations

import argparse
import logging
from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from executor.config import ExecutorConfig
from executor.logger.local import LocalLogger
from executor.receiver.client import BackendClient
from executor.trader.engine import TradingEngine
from executor.ui.console import confirm_plan, print_plan
from shared.models import TradeReport

logger = logging.getLogger("executor")


def _today() -> date:
    # 交易日按 Asia/Shanghai 时区计算
    return datetime.now(ZoneInfo("Asia/Shanghai")).date()


def run(config: ExecutorConfig, plan_date: date | None) -> int:
    client = BackendClient(config.backend_base_url, config.api_key)
    log = LocalLogger(config.executor_id)

    target = plan_date or _today()
    logger.info("拉取 %s 交易计划", target)
    plan = client.fetch_plan(target)
    if plan is None or not plan.items:
        logger.info("无交易计划，结束")
        client.send_heartbeat(config.executor_id, "idle", "no plan")
        return 0

    log.record({"event": "plan_fetched", "plan_id": plan.plan_id, "items": len(plan.items)})
    print_plan(plan)

    if config.mode == "manual" and not confirm_plan():
        logger.info("用户取消执行")
        client.send_heartbeat(config.executor_id, "idle", "cancelled by user")
        return 1

    engine = TradingEngine(retry_max=config.retry_max, backoff=config.retry_backoff_seconds)
    client.send_heartbeat(config.executor_id, "running", "executing plan")
    for item in plan.items:
        result = engine.execute_item(item)
        log.record(
            {
                "event": "order_executed",
                "code": item.code,
                "ok": result.ok,
                "order_no": result.order_no,
                "error": result.error,
            }
        )
        if result.ok:
            print(f"[执行] {item.code} 成功 {result.order_no or ''}")
            if item.item_id is not None and result.price:
                report = TradeReport(
                    client_request_id=f"{config.executor_id}-{target.isoformat()}-{item.item_id}",
                    item_id=item.item_id,
                    order_no=result.order_no,
                    code=item.code,
                    side=item.side,
                    quantity=item.quantity,
                    price=result.price,
                    traded_at=datetime.now(UTC),
                )
                client.report_trade(report)
            else:
                log.record(
                    {
                        "event": "trade_report_skipped",
                        "code": item.code,
                        "reason": "missing item_id or fill price",
                    }
                )
        else:
            print(f"[执行] {item.code} 失败 {result.error or ''}")
    client.send_heartbeat(config.executor_id, "idle", "done")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="stock-agent Windows 执行器")
    parser.add_argument("--config", default="config.toml", help="配置文件路径")
    parser.add_argument("--date", default=None, help="计划日期 YYYY-MM-DD，默认今天")
    parser.add_argument(
        "--mode", default=None, choices=["auto", "manual"], help="覆盖配置中的执行模式"
    )
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    args = _parse_args()
    config = ExecutorConfig.load(Path(args.config))
    if args.mode:
        config.mode = args.mode
    plan_date = date.fromisoformat(args.date) if args.date else None
    return run(config, plan_date)


if __name__ == "__main__":
    raise SystemExit(main())
