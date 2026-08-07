"""券商适配层接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Order:
    code: str
    side: str
    quantity: int
    price: float | None = None


@dataclass
class ExecutionResult:
    ok: bool
    order_no: str | None = None
    price: float | None = None
    error: str | None = None


class BrokerAdapter(ABC):
    """对接具体券商交易软件的适配器。新增券商时实现本接口。"""

    @abstractmethod
    def login(self, credentials: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def place_order(self, order: Order) -> ExecutionResult:
        raise NotImplementedError
