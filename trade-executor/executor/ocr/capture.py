"""屏幕区域截图（Windows / PIL ImageGrab）。"""

from __future__ import annotations

from typing import Any


def parse_region(region_str: str) -> tuple[int, int, int, int]:
    """解析 "left,top,width,height" 为元组。"""
    parts = [part.strip() for part in region_str.split(",")]
    if len(parts) != 4:
        raise ValueError(f"region 格式应为 left,top,width,height，收到: {region_str!r}")
    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError as exc:
        raise ValueError(f"region 必须为整数: {region_str!r}") from exc


def capture_region(region: tuple[int, int, int, int] | None = None) -> Any:
    """截取屏幕区域，返回 PIL Image；region=None 截全屏。"""
    from PIL import ImageGrab

    if region is None:
        return ImageGrab.grab()
    left, top, width, height = region
    return ImageGrab.grab(bbox=(left, top, left + width, top + height))
