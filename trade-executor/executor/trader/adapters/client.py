"""真实券商客户端自动化适配器（实验性脚手架）。

基于 pywinauto 控制 Windows 券商交易客户端（如同花顺 / 通达信等）。

⚠️ 重要：不同券商客户端布局差异很大，控件选择器（title / automation_id /
class_name）需要针对实际客户端调整；默认 dry_run=True 只记录/OCR 读取，不下单，
避免误操作真实资金。请先在仿真环境验证控件定位后再开启真实下单。
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from typing import Any

from executor.ocr import capture_region, confirm_order
from executor.trader.adapters.base import (
    BrokerAdapter,
    ExecutionResult,
    FillStatus,
    Order,
)

logger = logging.getLogger(__name__)


class ClientAutomationAdapter(BrokerAdapter):
    """通过 GUI 自动化操作真实券商客户端的适配器骨架。"""

    name = "client"

    def __init__(
        self,
        window_title: str = "网上股票交易系统",
        timeout: float = 10.0,
        dry_run: bool = True,
        ocr_engine: Any | None = None,
        ocr_region: tuple[int, int, int, int] | None = None,
        capture: Callable[..., Any] = capture_region,
    ):
        self.window_title = window_title
        self.timeout = timeout
        self.dry_run = dry_run
        self.ocr_engine = ocr_engine
        self.ocr_region = ocr_region
        self.capture = capture
        self._app: Any | None = None

    def _connect(self) -> Any:
        import pywinauto

        if self._app is None:
            self._app = pywinauto.Application(backend="uia").connect(
                title_re=f".*{self.window_title}.*", timeout=self.timeout
            )
        return self._app

    def login(self, credentials: dict) -> None:
        self._connect()
        logger.info("已连接券商客户端: %s", self.window_title)
        # TODO(v0.4): 处理登录窗口、输入账号密码（不同客户端差异大）

    def _ocr_confirmation(self) -> Any:
        if self.ocr_engine is None:
            return None
        confirmation = confirm_order(self.ocr_engine, self.ocr_region, capture=self.capture)
        logger.info(
            "OCR 确认: status=%s qty=%s price=%s",
            confirmation.status.value,
            confirmation.filled_quantity,
            confirmation.price,
        )
        return confirmation

    def place_order(self, order: Order) -> ExecutionResult:
        self._ocr_confirmation()
        if self.dry_run:
            logger.info(
                "[dry-run] 计划下单 %s %s %d股 限价%s",
                order.code,
                order.side.value,
                order.quantity,
                order.price,
            )
            return ExecutionResult(
                ok=False,
                status=FillStatus.PENDING,
                order_no=f"DRYRUN-{uuid.uuid4().hex[:8].upper()}",
                error="dry-run 模式：未执行真实下单",
            )
        self._connect()
        # TODO(v0.4): 定位下单控件 -> 输入代码/价格/数量 -> 点击买入/卖出 -> OCR 确认
        raise NotImplementedError("ClientAutomationAdapter 真实下单尚未实现")
