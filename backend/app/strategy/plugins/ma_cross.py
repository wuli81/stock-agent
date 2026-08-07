"""示例策略：均线多头排列（MA5 上穿 MA20 且收盘价站上 MA20）。"""

from app.strategy.base import BaseStrategy, Candidate, StrategyContext
from app.strategy.registry import register


def _sma(closes: list[float], n: int) -> float | None:
    if len(closes) < n:
        return None
    return sum(closes[-n:]) / n


@register
class MaCrossStrategy(BaseStrategy):
    name = "ma_cross"
    version = "0.1.0"

    def __init__(self, short: int = 5, long: int = 20, min_score: float = 1.0):
        self.short = short
        self.long = long
        self.min_score = min_score

    def run(self, ctx: StrategyContext) -> list[Candidate]:
        candidates: list[Candidate] = []
        for code, bars in ctx.quotes.items():
            closes = [float(b["close"]) for b in bars if b.get("close") is not None]
            short_ma = _sma(closes, self.short)
            long_ma = _sma(closes, self.long)
            if short_ma is None or long_ma is None or long_ma <= 0:
                continue
            if short_ma > long_ma and closes[-1] > long_ma:
                score = round((short_ma / long_ma - 1) * 100, 2)
                if score >= self.min_score:
                    candidates.append(
                        Candidate(
                            code=code,
                            score=score,
                            reason=f"MA{self.short}上穿MA{self.long}",
                        )
                    )
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates
