from abc import ABC, abstractmethod
from typing import Dict, Type, Any
from sustainabench.schemas.configs.workloads import WorkloadConfig

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
    require_config: bool = False
    def __init__(self, workload_cfg) -> None:
        if self.require_config and not workload_cfg:
            raise ValueError(f"Workload {self.name} requires a config. Please provide it.")
        self.workload_cfg = workload_cfg

class InternalWorkload(Workload):
    "Handles internal workloads (workloads without their own metrics)."
    @abstractmethod
    def run(self, num_processors: int, context=None):
        """Execute workload."""
        pass

class ExternalWorkload(Workload):
    """Handles external workloads (workloads with their own metrics)."""    

    require_wrapping: bool = False

    @abstractmethod
    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        pass

    @abstractmethod
    def process(self, backend_name: str) -> dict[str, Any]:
        # Process the results obtained from the execute() method. Please make sure to turn them into a format that fits what this suite expects.
        pass
