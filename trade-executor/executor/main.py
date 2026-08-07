"""trade-executor v0.4 命令行入口。

用法：
    # 命令行模式（拉取并执行计划）
    python -m executor.main --config config.toml --date 2026-08-10 --mode auto
    # 桌面界面（PySide6）
    python -m executor.main --gui
    # OCR 试识别（截图区域 -> 识别 -> 解析成交结果）
    python -m executor.main --ocr-check --region 100,200,400,120
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
from executor.trader.adapters.factory import create_adapter
from executor.trader.engine import TradingEngine
from executor.ui.console import confirm_plan, print_plan
from shared.models import OrderReport, TradeReport

logger = logging.getLogger("executor")


def _today() -> date:
    # 交易日按 Asia/Shanghai 时区计算
    return datetime.now(ZoneInfo("Asia/Shanghai")).date()


def _order_report(config: ExecutorConfig, plan_date: date, item, result) -> OrderReport:
    return OrderReport(
        client_request_id=f"{config.executor_id}-{plan_date.isoformat()}-{item.item_id}",
        item_id=item.item_id,
        order_no=result.order_no,
        code=item.code,
        side=item.side,
        quantity=item.quantity,
        price=result.price,
        status=result.status.value,
        error=result.error,
    )


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

    engine = TradingEngine(
        adapter=create_adapter(config),
        retry_max=config.retry_max,
        backoff=config.retry_backoff_seconds,
    )
    client.send_heartbeat(config.executor_id, "running", "executing plan")
    for item in plan.items:
        result = engine.execute_item(item)
        log.record(
            {
                "event": "order_executed",
                "code": item.code,
                "ok": result.ok,
                "status": result.status.value,
                "order_no": result.order_no,
                "error": result.error,
            }
        )
        order_id = None
        if item.item_id is not None:
            order_id = client.report_order(_order_report(config, target, item, result))
            log.record({"event": "order_reported", "code": item.code, "order_id": order_id})

        if result.ok and result.status.value == "filled":
            print(
                f"[执行] {item.code} 成交 {result.filled_quantity}股 "
                f"@{result.price} {result.order_no or ''}"
            )
            if item.item_id is not None and result.price:
                report = TradeReport(
                    client_request_id=f"{config.executor_id}-{target.isoformat()}-{item.item_id}",
                    item_id=item.item_id,
                    order_id=order_id,
                    order_no=result.order_no,
                    code=item.code,
                    side=item.side,
                    quantity=result.filled_quantity or item.quantity,
                    price=result.price,
                    traded_at=datetime.now(UTC),
                )
                client.report_trade(report)
        else:
            print(f"[执行] {item.code} 失败 {result.error or result.status.value}")
    client.send_heartbeat(config.executor_id, "idle", "done")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="stock-agent Windows 执行器")
    parser.add_argument("--config", default="config.toml", help="配置文件路径")
    parser.add_argument("--date", default=None, help="计划日期 YYYY-MM-DD，默认今天")
    parser.add_argument(
        "--mode", default=None, choices=["auto", "manual"], help="覆盖配置中的执行模式"
    )
    parser.add_argument("--gui", action="store_true", help="启动 PySide6 桌面界面")
    parser.add_argument(
        "--ocr-check", action="store_true", help="OCR 试识别：截取区域并解析成交结果"
    )
    parser.add_argument(
        "--region", default=None, help="截图区域 left,top,width,height（OCR 用）"
    )
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    args = _parse_args()
    config = ExecutorConfig.load(Path(args.config))
    if args.ocr_check:
        from executor.ocr import run_ocr_check

        return run_ocr_check(config, args.region)
    if args.gui:
        from executor.ui.app import run_gui

        return run_gui(args.config)
    if args.mode:
        config.mode = args.mode
    plan_date = date.fromisoformat(args.date) if args.date else None
    return run(config, plan_date)


if __name__ == "__main__":
    raise SystemExit(main())
