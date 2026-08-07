"""执行器配置（config.toml）。"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, fields
from pathlib import Path


@dataclass
class ExecutorConfig:
    backend_base_url: str = "http://localhost:8000/api/v1"
    api_key: str = "dev-key"
    mode: str = "manual"  # auto | manual
    executor_id: str = "win-01"
    retry_max: int = 3
    retry_backoff_seconds: int = 5
    broker: str = "paper"  # demo | paper | client(实验性)
    fill_mode: str = "mid"  # paper 撮合价：mid | min | max | fixed
    fixed_price: float = 10.0
    reject_codes: str = ""  # 逗号分隔的拒单股票代码

    @classmethod
    def load(cls, path: Path) -> ExecutorConfig:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})
