from abc import ABC, abstractmethod
from typing import Dict, Type

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
    def __init__(self, filename) -> None:
        pass

    @abstractmethod
    def compute(self, measurements: dict, metadata: dict, indicator_config: dict) -> dict:
        pass
