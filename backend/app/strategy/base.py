"""策略基类与上下文。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Candidate:
    code: str
    name: str | None = None
    score: float = 0.0
    reason: str = ""


@dataclass
class StrategyContext:
    plan_date: date
    quotes: dict[str, list[dict]] = field(default_factory=dict)  # code -> bar 列表

    def get_quotes(self, code: str) -> list[dict]:
        return self.quotes.get(code, [])


class BaseStrategy(ABC):
    """所有选股策略的基类。新增策略放到 plugins/ 目录并继承本类。"""

    name: str = "base"
    version: str = "0.1.0"

    @abstractmethod
    def run(self, ctx: StrategyContext) -> list[Candidate]:
        """运行策略，返回候选标的（按评分降序）。"""
        raise NotImplementedError
