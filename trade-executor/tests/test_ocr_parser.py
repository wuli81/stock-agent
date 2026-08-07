from executor.ocr.parser import parse_trade_confirmation
from executor.trader.adapters.base import FillStatus


def test_parse_filled_with_qty_price():
    conf = parse_trade_confirmation("全部成交 100股 价格10.75")
    assert conf.status == FillStatus.FILLED
    assert conf.filled_quantity == 100
    assert conf.price == 10.75


def test_parse_filled_zh():
    conf = parse_trade_confirmation("买入成交 数量:200 价格:11.25")
    assert conf.status == FillStatus.FILLED
    assert conf.filled_quantity == 200
    assert conf.price == 11.25


def test_parse_partial():
    conf = parse_trade_confirmation("部分成交 50股")
    assert conf.status == FillStatus.PARTIAL
    assert conf.filled_quantity == 50


def test_parse_rejected():
    assert parse_trade_confirmation("废单").status == FillStatus.REJECTED
    assert parse_trade_confirmation("委托失败").status == FillStatus.REJECTED
    assert parse_trade_confirmation("rejected").status == FillStatus.REJECTED


def test_parse_pending():
    assert parse_trade_confirmation("未成交").status == FillStatus.PENDING
    assert parse_trade_confirmation("已报").status == FillStatus.PENDING
    assert parse_trade_confirmation("").status == FillStatus.PENDING


def test_parse_english():
    conf = parse_trade_confirmation("FILLED 100 shares @ 10.75")
    assert conf.status == FillStatus.FILLED
    assert conf.price == 10.75
