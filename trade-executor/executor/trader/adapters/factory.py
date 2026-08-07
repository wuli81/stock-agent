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
        from executor.ocr import create_ocr_engine, parse_region
        from executor.trader.adapters.client import ClientAutomationAdapter

        ocr_engine = create_ocr_engine(config.ocr_engine) if config.ocr_engine else None
        ocr_region = parse_region(config.ocr_region) if config.ocr_region else None
        return ClientAutomationAdapter(ocr_engine=ocr_engine, ocr_region=ocr_region)
    raise ValueError(f"unknown broker: {config.broker}")
