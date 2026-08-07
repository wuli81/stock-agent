from executor.ocr.fake import FakeOcrEngine
from executor.trader.adapters.base import FillStatus, Order
from executor.trader.adapters.client import ClientAutomationAdapter

from shared.enums import Side


def _order():
    return Order(code="600000", side=Side.BUY, quantity=100)


def test_client_dry_run_with_ocr():
    adapter = ClientAutomationAdapter(
        dry_run=True,
        ocr_engine=FakeOcrEngine("全部成交 100股 价格10.75"),
        ocr_region=(0, 0, 10, 10),
        capture=lambda region: None,
    )
    result = adapter.place_order(_order())
    assert not result.ok
    assert result.status == FillStatus.PENDING
    assert result.error and "dry-run" in result.error


def test_client_dry_run_without_ocr():
    adapter = ClientAutomationAdapter(dry_run=True, capture=lambda region: None)
    result = adapter.place_order(_order())
    assert not result.ok
    assert result.status == FillStatus.PENDING
