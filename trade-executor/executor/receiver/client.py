"""后端 API 客户端：拉取计划、上报成交、发送心跳。"""

from __future__ import annotations

import logging
from datetime import date

import httpx

from shared.models import TradePlan, TradeReport

logger = logging.getLogger("executor")


class BackendClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self._base = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"}
        self._timeout = timeout

    def fetch_plan(self, plan_date: date) -> TradePlan | None:
        resp = httpx.get(
            f"{self._base}/trade-plans",
            params={"date": plan_date.isoformat()},
            headers=self._headers,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        body = resp.json()
        if body.get("code") != 0:
            raise RuntimeError(f"backend error: {body.get('message')}")
        plans = body["data"]["plans"]
        if not plans:
            return None
        return TradePlan(**plans[0])

    def report_trade(self, report: TradeReport) -> int:
        resp = httpx.post(
            f"{self._base}/trades",
            json=report.model_dump(mode="json"),
            headers=self._headers,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        body = resp.json()
        return body["data"]["trade_id"]

    def send_heartbeat(self, executor_id: str, status: str, message: str = "") -> None:
        try:
            resp = httpx.post(
                f"{self._base}/executor/heartbeat",
                json={"executor_id": executor_id, "status": status, "message": message},
                headers=self._headers,
                timeout=5,
            )
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001  心跳失败不阻断主流程
            logger.warning("heartbeat failed: %s", exc)
