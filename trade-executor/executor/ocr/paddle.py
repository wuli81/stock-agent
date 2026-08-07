"""PaddleOCR 引擎（需要安装 paddleocr，首次运行会下载模型）。"""

from __future__ import annotations

from typing import Any

from executor.ocr.base import OcrEngine, ScreenState


class PaddleOcrEngine(OcrEngine):
    name = "paddle"

    def __init__(self, lang: str = "ch", use_angle_cls: bool = True):
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self._ocr: Any | None = None

    def _get_ocr(self) -> Any:
        if self._ocr is None:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                use_angle_cls=self.use_angle_cls, lang=self.lang, show_log=False
            )
        return self._ocr

    def recognize(self, image: Any) -> ScreenState:
        import numpy as np
        from PIL import Image

        if not isinstance(image, Image.Image):
            image = Image.open(image)
        result = self._get_ocr().ocr(np.array(image), cls=True)
        lines = []
        for block in result or []:
            for line in block or []:
                if line and len(line) >= 2 and line[1]:
                    lines.append(str(line[1][0]))
        return ScreenState(text="\n".join(lines))
