"""本地结构化日志。"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger("executor")


class LocalLogger:
    def __init__(self, executor_id: str):
        self.executor_id = executor_id

    def record(self, event: dict) -> None:
        logger.info(json.dumps({"executor_id": self.executor_id, **event}, ensure_ascii=False))
