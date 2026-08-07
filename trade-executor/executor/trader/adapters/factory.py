"""券商适配器工厂。"""

from __future__ import annotations

from executor.config import ExecutorConfig
from executor.trader.adapters.base import BrokerAdapter


def create_adapter(config: ExecutorConfig) -> BrokerAdapter:
    name = config.broker.strip().lower()
    if name == "demo":
        from executor.trader.adapters.demo import DemoAdapter

        return DemoAdapter()
    if name == "paper":
        from executor.trader.adapters.paper import PaperBrokerAdapter, PaperConfig

        rejects = {c.strip() for c in config.reject_codes.split(",") if c.strip()}
        return PaperBrokerAdapter(
            PaperConfig(
                fill_mode=config.fill_mode,
                fixed_price=config.fixed_price,
                reject_codes=rejects or None,
            )
        )
    if name in ("client", "pywinauto"):
        from executor.trader.adapters.client import ClientAutomationAdapter

        return ClientAutomationAdapter()
    raise ValueError(f"unknown broker: {config.broker}")
