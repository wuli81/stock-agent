"""纸面券商适配器：模拟真实撮合，用于开发、测试与回测。

行为：
- 校验价格区间：限价必须在 price_min ~ price_max 内，否则拒单；
- 按 fill_mode 决定成交价：mid / min / max / fixed；
- fill_rate 支持整单或部分成交；
- reject_codes 中的股票直接风控拒单。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from executor.trader.adapters.base import (
    Balance,
    BrokerAdapter,
    ExecutionResult,
    FillStatus,
    Order,
    Position,
)
from shared.enums import Side


@dataclass
class PaperConfig:
    fill_mode: str = "mid"  # mid | min | max | fixed
    fixed_price: float = 10.0
    fill_rate: float = 1.0
    reject_codes: set[str] | None = None


class PaperBrokerAdapter(BrokerAdapter):
    name = "paper"

    def __init__(self, config: PaperConfig | None = None):
        self.config = config or PaperConfig()
        self._positions: dict[str, Position] = {}
        self._cash = 100_000.0

    def login(self, credentials: dict) -> None:
        self._logged_in = True

    def place_order(self, order: Order) -> ExecutionResult:
        if not self._validate(order):
            return ExecutionResult(
                ok=False,
                status=FillStatus.REJECTED,
                error="价格区间校验失败或风控拒绝",
            )

        fill_price = self._resolve_price(order)
        filled = int(order.quantity * self.config.fill_rate)
        if filled <= 0:
            return ExecutionResult(
                ok=False, status=FillStatus.REJECTED, error="成交数量为 0"
            )

        order_no = f"PAPER-{uuid.uuid4().hex[:12].upper()}"
        self._apply_fill(order, fill_price, filled)
        return ExecutionResult(
            ok=True,
            status=FillStatus.FILLED if filled == order.quantity else FillStatus.PARTIAL,
            order_no=order_no,
            price=fill_price,
            filled_quantity=filled,
        )

    def _validate(self, order: Order) -> bool:
        if self.config.reject_codes and order.code in self.config.reject_codes:
            return False
        if order.price_min is not None and order.price_max is not None:
            if order.price_min > order.price_max:
                return False
            if order.price is not None and not (
                order.price_min <= order.price <= order.price_max
            ):
                return False
        return True

    def _resolve_price(self, order: Order) -> float:
        mode = self.config.fill_mode
        if mode == "fixed":
            return self.config.fixed_price
        if order.price is not None:
            return order.price
        if mode == "min" and order.price_min is not None:
            return order.price_min
        if mode == "max" and order.price_max is not None:
            return order.price_max
        if order.price_min is not None and order.price_max is not None:
            return round((order.price_min + order.price_max) / 2, 2)
        return order.price or self.config.fixed_price

    def _apply_fill(self, order: Order, price: float, filled: int) -> None:
        pos = self._positions.get(order.code)
        if order.side == Side.BUY:
            if pos is None:
                pos = Position(code=order.code, quantity=0, cost_price=0.0)
                self._positions[order.code] = pos
            total_cost = pos.cost_price * pos.quantity + price * filled
            pos.quantity += filled
            pos.cost_price = round(total_cost / pos.quantity, 4) if pos.quantity else 0.0
            self._cash -= price * filled
        else:
            if pos is not None:
                pos.quantity = max(pos.quantity - filled, 0)
            self._cash += price * filled

    def query_position(self, code: str) -> Position | None:
        return self._positions.get(code)

    def query_balance(self) -> Balance:
        market_value = sum(
            p.quantity * (p.market_price or p.cost_price)
            for p in self._positions.values()
        )
        return Balance(
            total_asset=round(self._cash + market_value, 2),
            available_cash=round(self._cash, 2),
            market_value=round(market_value, 2),
        )
