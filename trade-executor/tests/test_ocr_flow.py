import pytest
from executor.ocr import confirm_order, create_ocr_engine, parse_region, run_ocr_check
from executor.ocr.fake import FakeOcrEngine
from executor.trader.adapters.base import FillStatus


def test_confirm_order_with_fake_engine():
    engine = FakeOcrEngine("全部成交 100股 价格10.75")
    conf = confirm_order(engine, capture=lambda region: None)
    assert conf.status == FillStatus.FILLED
    assert conf.filled_quantity == 100
    assert conf.price == 10.75


def test_confirm_order_rejected():
    engine = FakeOcrEngine("废单")
    conf = confirm_order(engine, capture=lambda region: None)
    assert conf.status == FillStatus.REJECTED


def test_create_ocr_engine_fake():
    engine = create_ocr_engine("fake", text="x")
    assert engine.name == "fake"
    assert engine.recognize(None).text == "x"


def test_create_ocr_engine_unknown():
    with pytest.raises(ValueError):
        create_ocr_engine("nope")


def test_parse_region():
    assert parse_region("100,200,400,120") == (100, 200, 400, 120)
    with pytest.raises(ValueError):
        parse_region("1,2,3")


def test_run_ocr_check_fake(monkeypatch):
    import executor.ocr as ocr_mod
    from executor.config import ExecutorConfig
    from executor.ocr.parser import parse_trade_confirmation

    config = ExecutorConfig()
    config.ocr_engine = "fake"

    def fake_confirm(engine, region=None, capture=ocr_mod.capture_region):
        state = engine.recognize(None)
        return parse_trade_confirmation(state.text)

    monkeypatch.setattr(ocr_mod, "confirm_order", fake_confirm)
    assert run_ocr_check(config, "0,0,10,10") == 0
