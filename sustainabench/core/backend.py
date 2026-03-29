from abc import ABC, abstractmethod
from typing import Any

class ExecutionBackend(ABC):
    """Defines how workloads are executed."""

    @abstractmethod
    def run(self, runner) -> tuple[dict[Any, Any], dict[Any, Any]]:
        """
        Execute a configured runner.
        Returns (raw_metrics, indicators)
        """
        pass
