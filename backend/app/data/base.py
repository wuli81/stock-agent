"""数据源接口与数据结构。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class Bar:
    code: str
    date: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    pre_close: float | None = None
    volume: int | None = None
    amount: float | None = None
    turn_rate: float | None = None


@dataclass
class StockInfo:
    code: str
    name: str


class DataProvider(ABC):
    """行情数据源接口。新增数据源时实现本接口。"""

    name: str = "base"

    @abstractmethod
    def fetch_stock_basics(self) -> list[StockInfo]:
        raise NotImplementedError

    @abstractmethod
    def fetch_daily(self, code: str, start: date, end: date) -> list[Bar]:
        raise NotImplementedError
