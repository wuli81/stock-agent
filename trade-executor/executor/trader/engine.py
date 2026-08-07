"""下单引擎：调用适配层并处理失败重试。"""

from __future__ import annotations

import logging
import time

from executor.trader.adapters.base import BrokerAdapter, ExecutionResult, Order
from executor.trader.adapters.demo import DemoAdapter
from shared.models import TradePlanItem

logger = logging.getLogger("executor")


class TradingEngine:
    def __init__(
        self,
        adapter: BrokerAdapter | None = None,
        retry_max: int = 3,
        backoff: float = 5.0,
    ):
        self.adapter = adapter or DemoAdapter()
        self.retry_max = max(retry_max, 1)
        self.backoff = backoff

    def execute_item(self, item: TradePlanItem) -> ExecutionResult:
        order = Order(code=item.code, side=item.side.value, quantity=item.quantity)
        last_result = ExecutionResult(ok=False, error="unknown")
        for attempt in range(1, self.retry_max + 1):
            try:
                return self.adapter.place_order(order)
            except Exception as exc:  # noqa: BLE001
                last_result = ExecutionResult(ok=False, error=str(exc))
                logger.warning("下单失败(第 %d 次): %s", attempt, exc)
                if attempt < self.retry_max:
                    time.sleep(self.backoff * attempt)
        return last_result
