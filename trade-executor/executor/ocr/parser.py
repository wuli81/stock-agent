"""OCR 文本 -> 成交确认解析。"""

from __future__ import annotations

import re

from executor.ocr.base import TradeConfirmation
from executor.trader.adapters.base import FillStatus

_REJECTED_WORDS = ("废单", "委托失败", "失败", "拒单", "已撤", "rejected", "failed", "cancelled")
_PENDING_WORDS = ("未成交", "未成", "待成交", "申报", "已报", "待报")
_PARTIAL_WORDS = ("部分成交", "partial")
_FILLED_WORDS = ("全部成交", "已成", "成交", "filled")

_QTY_PATTERNS = (
    re.compile(r"(\d{1,7})股"),
    re.compile(r"数量[:：]?(\d{1,7})"),
)
_PRICE_PATTERNS = (
    re.compile(r"价格[:：]?(\d+(?:\.\d{1,3})?)"),
    re.compile(r"成交价[:：]?(\d+(?:\.\d{1,3})?)"),
    re.compile(r"(\d+\.\d{2})"),
)


def _extract(patterns: tuple[re.Pattern, ...], compact: str) -> int | float | None:
    for pattern in patterns:
        match = pattern.search(compact)
        if match:
            value = match.group(1)
            try:
                return int(value) if value.isdigit() else float(value)
            except ValueError:
                continue
    return None


def parse_trade_confirmation(text: str) -> TradeConfirmation:
    """解析券商界面 OCR 文本，判断成交状态 / 数量 / 价格。"""
    raw = text or ""
    compact = re.sub(r"\s+", "", raw)
    if not compact:
        return TradeConfirmation(status=FillStatus.PENDING, raw_text=raw)
    haystack = compact.lower()
    if any(word in haystack for word in _REJECTED_WORDS):
        return TradeConfirmation(status=FillStatus.REJECTED, raw_text=raw)
    if any(word in haystack for word in _PENDING_WORDS):
        return TradeConfirmation(status=FillStatus.PENDING, raw_text=raw)
    quantity = _extract(_QTY_PATTERNS, compact) or 0
    price = _extract(_PRICE_PATTERNS, compact)
    if any(word in haystack for word in _PARTIAL_WORDS):
        return TradeConfirmation(
            status=FillStatus.PARTIAL, filled_quantity=quantity, price=price, raw_text=raw
        )
    if any(word in haystack for word in _FILLED_WORDS):
        return TradeConfirmation(
            status=FillStatus.FILLED, filled_quantity=quantity, price=price, raw_text=raw
        )
    return TradeConfirmation(status=FillStatus.PENDING, raw_text=raw)
