"""Tesseract OCR 引擎（需要系统安装 Tesseract 与 pytesseract 包）。"""

from __future__ import annotations

from typing import Any

from executor.ocr.base import OcrEngine, ScreenState


class TesseractOcrEngine(OcrEngine):
    name = "tesseract"

    def __init__(self, lang: str = "chi_sim+eng", timeout: float = 10.0):
        self.lang = lang
        self.timeout = timeout

    def recognize(self, image: Any) -> ScreenState:
        import pytesseract
        from PIL import Image

        if not isinstance(image, Image.Image):
            image = Image.open(image)
        text = pytesseract.image_to_string(image, lang=self.lang, timeout=self.timeout)
        return ScreenState(text=text.strip())
