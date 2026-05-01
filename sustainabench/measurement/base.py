from abc import ABC, abstractmethod
from typing import Dict, Type

MEASUREMENTS: Dict[str, Type["Measurement"]] = {}

def register_measurement(cls):
    """Macro used by each measurement to register in MEASUREMENTS"""
    MEASUREMENTS[cls.name] = cls
    return cls


class Measurement(ABC):
    """Base Measurement class"""
    name: str
    poll_interval: float | None = None # Seconds
    scope: str

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def sample(self):
        "Called repeatedly if poll_interval is set"
        pass

    @abstractmethod
    def result(self) -> dict:
        pass
