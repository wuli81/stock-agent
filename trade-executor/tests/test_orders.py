from executor.trader.adapters.base import FillStatus
from executor.trader.adapters.paper import PaperBrokerAdapter
from executor.trader.engine import TradingEngine

from shared.enums import Side
from shared.models import TradePlanItem


def test_engine_uses_mid_price_limit():
    engine = TradingEngine(adapter=PaperBrokerAdapter(), retry_max=1, backoff=0)
    item = TradePlanItem(
        code="600000", side=Side.BUY, quantity=100, price_min=10.0, price_max=11.0
    )
    result = engine.execute_item(item)
    assert result.ok
    assert result.price == 10.5  # 中间价作为限价


def test_engine_rejects_invalid_bounds():
    engine = TradingEngine(adapter=PaperBrokerAdapter(), retry_max=1, backoff=0)
    item = TradePlanItem(
        code="600000", side=Side.BUY, quantity=100, price_min=11.0, price_max=10.0
    )
    result = engine.execute_item(item)
    assert not result.ok
    assert result.status == FillStatus.REJECTED


def test_engine_requires_adapter():
    engine = TradingEngine(retry_max=1, backoff=0)
    try:
        engine.execute_item(TradePlanItem(code="600000", side=Side.BUY, quantity=100))
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass
