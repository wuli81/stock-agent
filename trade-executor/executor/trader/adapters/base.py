"""券商适配层接口与数据结构。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from shared.enums import Side


class FillStatus(StrEnum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    REJECTED = "rejected"


@dataclass
class Order:
    code: str
    side: Side
    quantity: int
    price: float | None = None  # 限价；None 表示市价
    price_min: float | None = None
    price_max: float | None = None


@dataclass
class ExecutionResult:
    ok: bool
    status: FillStatus = FillStatus.REJECTED
    order_no: str | None = None
    price: float | None = None
    filled_quantity: int = 0
    error: str | None = None


@dataclass
class Position:
    code: str
    quantity: int
    cost_price: float
    market_price: float | None = None


@dataclass
class Balance:
    total_asset: float
    available_cash: float
    market_value: float = 0.0


class BrokerAdapter(ABC):
    """对接具体券商交易软件的适配器。新增券商时实现本接口。"""

    name: str = "base"

    @abstractmethod
    def login(self, credentials: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def place_order(self, order: Order) -> ExecutionResult:
        raise NotImplementedError

    def query_position(self, code: str) -> Position | None:
        return None

    def query_balance(self) -> Balance | None:
        return None

    def logout(self) -> None:
        return None
