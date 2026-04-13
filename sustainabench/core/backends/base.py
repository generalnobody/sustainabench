from abc import ABC, abstractmethod
from typing import Dict, Type, Any
from ..models import BenchmarkResult

BACKENDS: Dict[str, Type["ExecutionBackend"]] = {}

def register_backend(cls):
    """Macro used by each backend to register in BACKENDS"""
    BACKENDS[cls.name] = cls
    return cls

class ExecutionBackend(ABC):
    """Defines how workloads are executed."""
    name: str

    @abstractmethod
    def __init__(self, num_processors: int) -> None:
        pass

    @abstractmethod
    def run(self, runner) -> BenchmarkResult:
        """
        Execute a configured runner.
        Returns raw_metrics
        """
        pass
