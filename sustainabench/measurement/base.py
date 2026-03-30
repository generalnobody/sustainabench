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

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def result(self) -> dict:
        pass
