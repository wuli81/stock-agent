"""PySide6 桌面界面：计划展示、执行控制与运行日志。

启动：python -m executor.ui.app
"""

from __future__ import annotations

import logging
import sys
from datetime import UTC, date, datetime
from pathlib import Path

from PySide6.QtCore import QDate, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from executor.config import ExecutorConfig
from executor.receiver.client import BackendClient
from executor.trader.adapters.base import ExecutionResult
from executor.trader.adapters.factory import create_adapter
from executor.trader.engine import TradingEngine
from shared.models import TradeReport

logger = logging.getLogger("executor.ui")


class PlanWorker(QThread):
    """后台线程：拉取计划并按需执行。"""

    plan_ready = Signal(object)
    log = Signal(str)
    item_done = Signal(str, bool, str)
    done = Signal()

    def __init__(self, config: ExecutorConfig, plan_date: date, execute: bool = False):
        super().__init__()
        self.config = config
        self.plan_date = plan_date
        self.execute = execute
        self._stop = False

    def run(self) -> None:
        client = BackendClient(self.config.backend_base_url, self.config.api_key)
        self.log.emit(f"拉取 {self.plan_date} 交易计划...")
        try:
            plan = client.fetch_plan(self.plan_date)
        except Exception as exc:  # noqa: BLE001
            self.log.emit(f"拉取失败: {exc}")
            self.done.emit()
            return
        self.plan_ready.emit(plan)
        if not self.execute or plan is None or not plan.items:
            self.done.emit()
            return

        engine = TradingEngine(
            adapter=create_adapter(self.config),
            retry_max=self.config.retry_max,
            backoff=self.config.retry_backoff_seconds,
        )
        for item in plan.items:
            if self._stop:
                self.log.emit("已停止")
                break
            result = engine.execute_item(item)
            ok = result.ok and result.status.value == "filled"
            self.item_done.emit(item.code, ok, result.order_no or result.error or "")
            if ok and item.item_id is not None and result.price:
                self._report(client, item, result)
        self.done.emit()

    def _report(self, client: BackendClient, item, result: ExecutionResult) -> None:
        report = TradeReport(
            client_request_id=(
                f"{self.config.executor_id}-{self.plan_date.isoformat()}-{item.item_id}"
            ),
            item_id=item.item_id,
            order_no=result.order_no,
            code=item.code,
            side=item.side,
            quantity=result.filled_quantity or item.quantity,
            price=result.price,
            traded_at=datetime.now(UTC),
        )
        try:
            client.report_trade(report)
            self.log.emit(f"已上报成交 {item.code}")
        except Exception as exc:  # noqa: BLE001
            self.log.emit(f"上报失败 {item.code}: {exc}")

    def stop(self) -> None:
        self._stop = True


class MainWindow(QMainWindow):
    def __init__(self, config: ExecutorConfig | None = None):
        super().__init__()
        self.config = config or ExecutorConfig()
        self._worker: PlanWorker | None = None
        self._build_ui()
        self.setWindowTitle("stock-agent 执行器 v0.2")

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)

        conn = QGroupBox("连接")
        conn_row = QHBoxLayout(conn)
        conn_row.addWidget(QLabel("后端:"))
        self.backend_edit = QLineEdit(self.config.backend_base_url)
        conn_row.addWidget(self.backend_edit, 1)
        conn_row.addWidget(QLabel("日期:"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        conn_row.addWidget(self.date_edit)
        root.addWidget(conn)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["代码", "方向", "数量", "价格区间", "状态"])
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)

        btns = QHBoxLayout()
        self.fetch_btn = QPushButton("拉取计划")
        self.run_btn = QPushButton("执行")
        self.stop_btn = QPushButton("停止")
        for button in (self.fetch_btn, self.run_btn, self.stop_btn):
            btns.addWidget(button)
        btns.addStretch(1)
        root.addLayout(btns)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        root.addWidget(self.log_view)

        self.setCentralWidget(central)
        self.resize(760, 580)

        self.fetch_btn.clicked.connect(self._fetch)
        self.run_btn.clicked.connect(self._execute)
        self.stop_btn.clicked.connect(self._stop)

    def _plan_date(self) -> date:
        return self.date_edit.date().toPython()

    def _start_worker(self, execute: bool) -> None:
        self._shutdown_worker()
        self.config.backend_base_url = self.backend_edit.text().strip()
        worker = PlanWorker(self.config, self._plan_date(), execute=execute)
        worker.plan_ready.connect(self._on_plan)
        worker.item_done.connect(self._on_item)
        worker.log.connect(self._append_log)
        worker.done.connect(self._on_done)
        worker.start()
        self._worker = worker

    def _fetch(self) -> None:
        self._start_worker(execute=False)

    def _execute(self) -> None:
        self._start_worker(execute=True)

    def _stop(self) -> None:
        if self._worker is not None:
            self._worker.stop()

    def _shutdown_worker(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker.wait(2000)
            self._worker = None

    def _on_plan(self, plan) -> None:
        self.table.setRowCount(0)
        if plan is None:
            self._append_log("无交易计划")
            return
        for item in plan.items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item.code))
            self.table.setItem(row, 1, QTableWidgetItem(item.side.value))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            price_range = (
                f"{item.price_min}~{item.price_max}"
                if item.price_min or item.price_max
                else "-"
            )
            self.table.setItem(row, 3, QTableWidgetItem(price_range))
            self.table.setItem(row, 4, QTableWidgetItem(item.status.value))
        self._append_log(f"计划 {plan.plan_date}: {len(plan.items)} 条")

    def _on_item(self, code: str, ok: bool, msg: str) -> None:
        for row in range(self.table.rowCount()):
            item0 = self.table.item(row, 0)
            if item0 is not None and item0.text() == code:
                self.table.setItem(row, 4, QTableWidgetItem("成功" if ok else "失败"))
                break
        self._append_log(f"[{code}] {'成功 ' + msg if ok else '失败 ' + msg}")

    def _on_done(self) -> None:
        self._append_log("完成")
        self._worker = None

    def _append_log(self, text: str) -> None:
        self.log_view.appendPlainText(text)


def run_gui(config_path: str = "config.toml") -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = ExecutorConfig.load(Path(config_path))
    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_gui())
