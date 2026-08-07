"""OCR 成交确认子系统。

引擎：tesseract | paddle | fake；识别文本经 parser 解析为成交确认。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from executor.ocr.base import OcrEngine, ScreenState, TradeConfirmation
from executor.ocr.capture import capture_region, parse_region
from executor.ocr.fake import FakeOcrEngine
from executor.ocr.paddle import PaddleOcrEngine
from executor.ocr.parser import parse_trade_confirmation
from executor.ocr.tesseract import TesseractOcrEngine

__all__ = [
    "OcrEngine",
    "ScreenState",
    "TradeConfirmation",
    "capture_region",
    "parse_region",
    "parse_trade_confirmation",
    "create_ocr_engine",
    "confirm_order",
    "run_ocr_check",
]


def create_ocr_engine(name: str | None = None, **kwargs) -> OcrEngine:
    """按名称创建 OCR 引擎。"""
    engine = (name or "").strip().lower()
    if engine in ("tesseract", "pytesseract"):
        return TesseractOcrEngine(**kwargs)
    if engine in ("paddle", "paddleocr"):
        return PaddleOcrEngine(**kwargs)
    if engine == "fake":
        return FakeOcrEngine(**kwargs)
    raise ValueError(f"unknown ocr engine: {name!r}")


def confirm_order(
    engine: OcrEngine,
    region: tuple[int, int, int, int] | None = None,
    capture: Callable[..., Any] = capture_region,
) -> TradeConfirmation:
    """截取指定屏幕区域 -> OCR -> 解析成交确认。capture 可注入便于测试。"""
    image = capture(region)
    state = engine.recognize(image)
    return parse_trade_confirmation(state.text)


def run_ocr_check(config, region_str: str | None) -> int:
    """CLI：OCR 试识别（截图 -> 识别 -> 解析并打印）。"""
    engine = create_ocr_engine(config.ocr_engine)
    region = parse_region(region_str) if region_str else None
    confirmation = confirm_order(engine, region)
    print(f"OCR 引擎: {engine.name}")
    print(f"识别文本: {confirmation.raw_text!r}")
    print(f"解析结果: status={confirmation.status.value} "
          f"qty={confirmation.filled_quantity} price={confirmation.price}")
    return 0
