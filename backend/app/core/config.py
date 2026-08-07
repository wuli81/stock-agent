"""应用配置。环境变量前缀 STOCK_AGENT_，示例见 .env.example。"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "stock-agent-backend"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./data/stock_agent.db"
    api_keys: str = "dev-key"  # 逗号分隔的 API Key
    enable_scheduler: bool = False
    timezone: str = "Asia/Shanghai"
    log_level: str = "INFO"

    # 数据与策略
    data_provider: str = "akshare"  # 数据源实现
    tracked_stocks: str = ""  # 逗号分隔的跟踪股票代码，如 "600000,000001"
    strategy_name: str = "ma_cross"
    plan_budget: float = 100_000.0
    quote_lookback_days: int = 60

    model_config = {
        "env_prefix": "STOCK_AGENT_",
        "env_file": ".env",
        "extra": "ignore",
    }

    @property
    def api_key_list(self) -> list[str]:
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def tracked_code_list(self) -> list[str]:
        return [c.strip() for c in self.tracked_stocks.split(",") if c.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
