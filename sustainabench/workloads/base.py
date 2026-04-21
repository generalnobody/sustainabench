from abc import ABC, abstractmethod
from typing import Dict, Type

# global registry
WORKLOADS: Dict[str, Type["Workload"]] = {}


def register_workload(cls):
    """Decorator to register workloads automatically."""
    WORKLOADS[cls.name] = cls
    return cls


class Workload(ABC):
    """Base class for all benchmark workloads."""

    # Every workload must define this
    name: str

    @abstractmethod
    def run(self, num_processors: int, workload_cfg):
        """Execute workload."""
        pass
