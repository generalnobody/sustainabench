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

    @abstractmethod
    def compute(self, measurements: dict) -> dict:
        pass
