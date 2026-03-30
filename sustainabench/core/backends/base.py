from abc import ABC, abstractmethod
from typing import Dict, Type, Any

BACKENDS: Dict[str, Type["ExecutionBackend"]] = {}

def register_backend(cls):
    """Macro used by each backend to register in BACKENDS"""
    BACKENDS[cls.name] = cls
    return cls

class ExecutionBackend(ABC):
    """Defines how workloads are executed."""
    name: str

    @abstractmethod
    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    @abstractmethod
    def run(self, runner) -> tuple[dict[Any, Any], dict[Any, Any]]:
        """
        Execute a configured runner.
        Returns (raw_metrics, indicators)
        """
        pass
