from abc import ABC, abstractmethod
from typing import Dict, Type
from sustainabench.schemas.configs.indicators.config import IndicatorConfig

INDICATORS: Dict[str, Type["Indicator"]] = {}

def register_indicator(cls):
    """Macro used by each indicator to register in INDICATORS"""
    INDICATORS[cls.name] = cls
    return cls


class Indicator(ABC):
    """Base Indicator class"""
    name: str
    require_file: bool # Control whether this indicator should require a file path to be included or not.

    @abstractmethod
    def __init__(self, filename: str) -> None:
        pass

    @abstractmethod
    def setup(self, indicator_config: IndicatorConfig | None) -> None:
        pass

    @abstractmethod
    def compute(self, measurements: dict, metadata: dict) -> dict:
        pass
