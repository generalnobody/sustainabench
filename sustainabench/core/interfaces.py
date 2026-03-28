from abc import ABC, abstractmethod
from typing import Dict, Any


class Workload(ABC):
    name: str

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def teardown(self) -> None:
        pass


class MeasurementSource(ABC):

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> Dict[str, Any]:
        """Return raw measurements"""
        pass


class Indicator(ABC):

    @abstractmethod
    def compute(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        pass
