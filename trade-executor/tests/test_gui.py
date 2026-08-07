"""GUI 离屏冒烟测试（需要 PySide6；未安装则跳过）。"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from executor.config import ExecutorConfig
from executor.ui.app import MainWindow


def test_main_window_offscreen():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app is not None
    win = MainWindow(ExecutorConfig())
    win.show()
    assert win.windowTitle() == "stock-agent 执行器 v0.4"
    assert win.table.columnCount() == 5
    assert win.table.rowCount() == 0
    assert win.fetch_btn.text() == "拉取计划"
    assert win.run_btn.text() == "执行"
    win.close()
