from executor.trader.adapters.base import ExecutionResult, Order
from executor.trader.adapters.demo import DemoAdapter
from executor.trader.engine import TradingEngine

from shared.enums import Side
from shared.models import TradePlanItem


def test_demo_adapter_executes():
    engine = TradingEngine(adapter=DemoAdapter(), retry_max=2, backoff=0)
    item = TradePlanItem(code="600000", side=Side.BUY, quantity=100)
    result = engine.execute_item(item)
    assert result.ok
    assert result.order_no and result.order_no.startswith("DEMO-")
    assert result.price == 10.0


def test_demo_adapter_uses_order_price():
    adapter = DemoAdapter()
    result = adapter.place_order(Order(code="600000", side="buy", quantity=100, price=12.5))
    assert result.price == 12.5


class FlakyAdapter(DemoAdapter):
    def __init__(self, fail_times=2):
        super().__init__()
        self._calls = 0
        self._fail_times = fail_times

    def place_order(self, order: Order) -> ExecutionResult:
        self._calls += 1
        if self._calls <= self._fail_times:
            raise RuntimeError("network error")
        return super().place_order(order)


def test_engine_retries_then_succeeds():
    adapter = FlakyAdapter(fail_times=2)
    engine = TradingEngine(adapter=adapter, retry_max=3, backoff=0)
    result = engine.execute_item(TradePlanItem(code="600000", side=Side.BUY, quantity=100))
    assert result.ok
    assert adapter._calls == 3


def test_engine_gives_up_after_retries():
    adapter = FlakyAdapter(fail_times=99)
    engine = TradingEngine(adapter=adapter, retry_max=3, backoff=0)
    result = engine.execute_item(TradePlanItem(code="600000", side=Side.BUY, quantity=100))
    assert not result.ok
    assert adapter._calls == 3
