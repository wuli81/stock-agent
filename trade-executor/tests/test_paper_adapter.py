from executor.trader.adapters.base import FillStatus, Order
from executor.trader.adapters.paper import PaperBrokerAdapter, PaperConfig

from shared.enums import Side


def _buy(code="600000", price=10.5, price_min=10.0, price_max=11.0, qty=100):
    return Order(
        code=code,
        side=Side.BUY,
        quantity=qty,
        price=price,
        price_min=price_min,
        price_max=price_max,
    )


def test_paper_fills_within_bounds():
    adapter = PaperBrokerAdapter()
    result = adapter.place_order(_buy())
    assert result.ok
    assert result.status == FillStatus.FILLED
    assert result.price == 10.5
    assert result.filled_quantity == 100
    assert adapter.query_position("600000").quantity == 100
    assert adapter.query_balance().total_asset == 100_000.0


def test_paper_mid_price_when_no_limit():
    adapter = PaperBrokerAdapter()
    order = Order(code="600000", side=Side.BUY, quantity=100, price_min=10.0, price_max=11.0)
    result = adapter.place_order(order)
    assert result.ok
    assert result.price == 10.5


def test_paper_rejects_out_of_bounds():
    adapter = PaperBrokerAdapter()
    result = adapter.place_order(_buy(price=12.0))
    assert not result.ok
    assert result.status == FillStatus.REJECTED


def test_paper_rejects_invalid_bounds():
    adapter = PaperBrokerAdapter()
    order = Order(code="600000", side=Side.BUY, quantity=100, price_min=11.0, price_max=10.0)
    result = adapter.place_order(order)
    assert not result.ok


def test_paper_rejects_blacklisted_code():
    adapter = PaperBrokerAdapter(PaperConfig(reject_codes={"600000"}))
    result = adapter.place_order(_buy())
    assert not result.ok
    assert result.status == FillStatus.REJECTED


def test_paper_partial_fill():
    adapter = PaperBrokerAdapter(PaperConfig(fill_rate=0.5))
    result = adapter.place_order(_buy(qty=100))
    assert result.ok
    assert result.status == FillStatus.PARTIAL
    assert result.filled_quantity == 50


def test_paper_sell_reduces_position():
    adapter = PaperBrokerAdapter()
    adapter.place_order(_buy(qty=100))
    sell = Order(
        code="600000",
        side=Side.SELL,
        quantity=40,
        price=11.0,
        price_min=10.0,
        price_max=12.0,
    )
    result = adapter.place_order(sell)
    assert result.ok
    assert adapter.query_position("600000").quantity == 60
