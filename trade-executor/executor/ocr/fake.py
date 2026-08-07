"""测试用假 OCR 引擎。"""

from __future__ import annotations

from typing import Any

from executor.ocr.base import OcrEngine, ScreenState


class FakeOcrEngine(OcrEngine):
    name = "fake"

    def __init__(self, text: str = ""):
        self.text = text

    def recognize(self, image: Any) -> ScreenState:
        return ScreenState(text=self.text)
