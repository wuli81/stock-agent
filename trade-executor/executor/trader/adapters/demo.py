"""Demo 适配器：模拟下单，不连接真实券商，用于开发与测试。"""

from __future__ import annotations

import uuid

from executor.trader.adapters.base import BrokerAdapter, ExecutionResult, Order


class DemoAdapter(BrokerAdapter):
    """模拟成交价默认 10.0，可用 default_price 覆盖。"""

    def __init__(self, default_price: float = 10.0):
        self.default_price = default_price

    def login(self, credentials: dict) -> None:
        self._logged_in = True

    def place_order(self, order: Order) -> ExecutionResult:
        order_no = f"DEMO-{uuid.uuid4().hex[:12].upper()}"
        price = order.price if order.price else self.default_price
        return ExecutionResult(ok=True, order_no=order_no, price=price)
