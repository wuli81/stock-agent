"""akshare provider 解析逻辑测试（不依赖网络与真实 akshare，mock 模块与数据帧）。"""

import sys
import types
from datetime import date

import pandas as pd
from app.data.akshare_provider import AkshareDataProvider


def _fake_akshare(hist_df=None, basics_df=None) -> types.ModuleType:
    fake = types.ModuleType("akshare")
    fake.stock_zh_a_hist = lambda **kwargs: hist_df
    fake.stock_info_a_code_name = lambda: basics_df
    return fake


def test_fetch_daily_parses_bars(monkeypatch):
    df = pd.DataFrame(
        {
            "日期": pd.to_datetime(["2026-08-05", "2026-08-06"]),
            "开盘": [10.0, 10.2],
            "最高": [10.5, 10.4],
            "最低": [9.9, 10.1],
            "收盘": [10.3, 10.2],
            "成交量": [10000, 12000],
            "成交额": [1.03e7, 1.22e7],
            "换手率": [0.5, 0.6],
        }
    )
    monkeypatch.setitem(sys.modules, "akshare", _fake_akshare(hist_df=df))

    bars = AkshareDataProvider().fetch_daily(
        "600000", date(2026, 8, 1), date(2026, 8, 7)
    )
    assert len(bars) == 2
    assert bars[0].code == "600000"
    assert bars[0].date == "2026-08-05"
    assert bars[0].close == 10.3
    assert bars[0].volume == 10000
    assert bars[0].turn_rate == 0.5


def test_fetch_stock_basics_parses(monkeypatch):
    df = pd.DataFrame({"code": ["600000", 1], "name": ["浦发银行", "平安银行"]})
    monkeypatch.setitem(sys.modules, "akshare", _fake_akshare(basics_df=df))

    infos = AkshareDataProvider().fetch_stock_basics()
    assert infos[0].code == "600000"
    assert infos[0].name == "浦发银行"
    assert infos[1].code == "000001"  # 数字代码补零
    assert infos[1].name == "平安银行"
