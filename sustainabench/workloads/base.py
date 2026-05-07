from abc import ABC, abstractmethod
from typing import Dict, Type
from sustainabench.schemas.configs.workloads.config import WorkloadConfig

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

    def is_external(self) -> bool:
        return False
    
    def __init__(self, workload_cfg: WorkloadConfig) -> None:
        self.workload_cfg = workload_cfg

    @abstractmethod
    def run(self, num_processors: int, context=None):
        """Execute workload."""
        pass

class ExternalWorkload(Workload):
    """Handles external workloads. External workloads are prioritized, but do not run with the MeasurementManager, instead they are run without any measurements. Then, manual interpretation for the obtained results is needed. 
    Do note, that any measurements that are selected will not be run. As such, it is recommended to use the 'none' measurement (this does nothing)."""
    def is_external(self) -> bool:
        return True
    
    @abstractmethod
    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        pass

    @abstractmethod
    def process(self):
        # Process the results obtained from the execute() method. Please make sure to turn them into a format that fits what this suite expects.
        pass
