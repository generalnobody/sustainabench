from abc import ABC, abstractmethod
from typing import Dict, Type

INDICATORS: Dict[str, Type["Indicator"]] = {}

def register_indicator(cls):
    INDICATORS[cls.name] = cls
    return cls


class Indicator(ABC):
    name: str

    @abstractmethod
    def compute(self, measurements: dict) -> dict:
        pass
