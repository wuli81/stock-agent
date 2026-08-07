"""v0.1 屏幕识别占位模块。

后续接入 PaddleOCR / Tesseract，识别券商交易软件界面状态（成交/失败/待确认）。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScreenState:
    text: str = ""
    confidence: float = 0.0


def recognize(region: tuple[int, int, int, int] | None = None) -> ScreenState:
    """识别指定区域文本；v0.1 返回空状态占位。"""
    return ScreenState()
