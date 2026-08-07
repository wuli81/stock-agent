"""策略插件注册与发现。"""

import importlib
import pkgutil
from typing import TypeVar

from app.strategy.base import BaseStrategy

T = TypeVar("T", bound=type[BaseStrategy])

_REGISTRY: dict[str, T] = {}


def register(cls: T) -> T:
    """将策略类注册到全局注册表。"""
    if issubclass(cls, BaseStrategy) and cls.name != "base":
        _REGISTRY[cls.name] = cls
    return cls


def discover_plugins() -> list[T]:
    """扫描 plugins 包，导入所有策略模块以触发注册。"""
    from app.strategy import plugins

    for mod in pkgutil.iter_modules(plugins.__path__):
        importlib.import_module(f"{plugins.__name__}.{mod.name}")
    return list(_REGISTRY.values())


def get_strategy(name: str, **params) -> BaseStrategy:
    discover_plugins()
    if name not in _REGISTRY:
        raise KeyError(f"strategy '{name}' not found")
    return _REGISTRY[name](**params)
