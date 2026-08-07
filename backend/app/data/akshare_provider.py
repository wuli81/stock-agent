"""基于 akshare 的数据源实现（需要安装 akshare，见 backend[data] 可选依赖）。"""

from __future__ import annotations

import logging
from datetime import date

from app.data.base import Bar, DataProvider, StockInfo

logger = logging.getLogger(__name__)


def _to_float(value) -> float | None:
    try:
        result = float(value)
        return result if result == result else None  # NaN -> None
    except (TypeError, ValueError):
        return None


def _to_int(value) -> int | None:
    result = _to_float(value)
    return int(result) if result is not None else None


class AkshareDataProvider(DataProvider):
    name = "akshare"

    def fetch_stock_basics(self) -> list[StockInfo]:
        import akshare as ak

        df = ak.stock_info_a_code_name()
        result = [
            StockInfo(code=str(row.code).zfill(6), name=str(row.name))
            for row in df.itertuples(index=False)
        ]
        logger.info("akshare basics fetched: %d", len(result))
        return result

    def fetch_daily(self, code: str, start: date, end: date) -> list[Bar]:
        import akshare as ak

        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start.strftime("%Y%m%d"),
            end_date=end.strftime("%Y%m%d"),
            adjust="qfq",
        )
        if df is None or df.empty:
            return []
        bars = []
        for row in df.itertuples(index=False):
            bars.append(
                Bar(
                    code=code,
                    date=str(row.日期)[:10],
                    open=_to_float(row.开盘),
                    high=_to_float(row.最高),
                    low=_to_float(row.最低),
                    close=_to_float(row.收盘),
                    pre_close=None,
                    volume=_to_int(row.成交量),
                    amount=_to_float(row.成交额),
                    turn_rate=_to_float(row.换手率),
                )
            )
        logger.info("akshare daily %s: %d bars", code, len(bars))
        return bars
