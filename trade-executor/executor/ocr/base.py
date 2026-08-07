"""OCR 引擎接口与结果数据结构。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from executor.trader.adapters.base import FillStatus


@dataclass
class ScreenState:
    text: str = ""
    confidence: float = 0.0


@dataclass
class TradeConfirmation:
    status: FillStatus
    filled_quantity: int = 0
    price: float | None = None
    raw_text: str = ""
    confidence: float = 0.0


class OcrEngine(ABC):
    """OCR 引擎接口。新增引擎时实现本接口。"""

    name: str = "base"

    @abstractmethod
    def recognize(self, image: Any) -> ScreenState:
        """识别图像（PIL Image 或可被 PIL 打开的路径）中的文本。"""
        raise NotImplementedError
