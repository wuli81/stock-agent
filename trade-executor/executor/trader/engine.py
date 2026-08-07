"""下单引擎：构建订单、校验、调用适配层、失败重试。"""

from __future__ import annotations

import logging
import time

from executor.trader.adapters.base import (
    BrokerAdapter,
    ExecutionResult,
    FillStatus,
    Order,
)
from shared.models import TradePlanItem

logger = logging.getLogger("executor")


class TradingEngine:
    def __init__(
        self,
        adapter: BrokerAdapter | None = None,
        retry_max: int = 3,
        backoff: float = 5.0,
    ):
        self.adapter = adapter
        self.retry_max = max(retry_max, 1)
        self.backoff = backoff

    def execute_item(self, item: TradePlanItem) -> ExecutionResult:
        if self.adapter is None:
            raise RuntimeError("no broker adapter configured")
        order = self._build_order(item)
        if order is None:
            return ExecutionResult(
                ok=False,
                status=FillStatus.REJECTED,
                error="价格区间无效（price_min > price_max）",
            )
        last = ExecutionResult(ok=False, status=FillStatus.REJECTED, error="unknown")
        for attempt in range(1, self.retry_max + 1):
            try:
                return self.adapter.place_order(order)
            except Exception as exc:  # noqa: BLE001
                last = ExecutionResult(ok=False, status=FillStatus.REJECTED, error=str(exc))
                logger.warning("下单失败(第 %d 次): %s", attempt, exc)
                if attempt < self.retry_max:
                    time.sleep(self.backoff * attempt)
        return last

    @staticmethod
    def _build_order(item: TradePlanItem) -> Order | None:
        """计划项 -> 限价单（取价格区间中间价；无区间则为市价单）。"""
        if (
            item.price_min is not None
            and item.price_max is not None
            and item.price_min > item.price_max
        ):
            return None
        price = None
        if item.price_min is not None and item.price_max is not None:
            price = round((item.price_min + item.price_max) / 2, 2)
        return Order(
            code=item.code,
            side=item.side,
            quantity=item.quantity,
            price=price,
            price_min=item.price_min,
            price_max=item.price_max,
        )
