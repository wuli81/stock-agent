from datetime import date

from app.strategy.base import StrategyContext
from app.strategy.plugins.ma_cross import MaCrossStrategy
from app.strategy.registry import discover_plugins, get_strategy


def _uptrend_bars(days=30, start=10.0, step=0.1):
    return [{"date": f"2026-06-{i + 1:02d}", "close": start + i * step} for i in range(days)]


def test_ma_cross_uptrend_produces_candidate():
    ctx = StrategyContext(plan_date=date(2026, 8, 7), quotes={"600000": _uptrend_bars()})
    candidates = MaCrossStrategy().run(ctx)
    assert candidates, "上升趋势应产生候选"
    assert candidates[0].code == "600000"
    assert candidates[0].score >= 1.0


def test_ma_cross_downtrend_empty():
    bars = [{"date": f"2026-06-{i + 1:02d}", "close": 20.0 - i * 0.2} for i in range(30)]
    ctx = StrategyContext(plan_date=date(2026, 8, 7), quotes={"600000": bars})
    assert MaCrossStrategy().run(ctx) == []


def test_registry_discovers_plugins():
    names = {c.name for c in discover_plugins()}
    assert "ma_cross" in names
    strat = get_strategy("ma_cross", short=5, long=20)
    assert strat.name == "ma_cross"
    assert strat.version == "0.1.0"
