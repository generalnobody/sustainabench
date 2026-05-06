from abc import ABC, abstractmethod
from typing import Dict, Type
from ..models import BenchmarkResult, NodeResult
from sustainabench.measurement.manager import MeasurementManager

BACKENDS: Dict[str, Type["ExecutionBackend"]] = {}

def register_backend(cls):
    """Macro used by each backend to register in BACKENDS"""
    BACKENDS[cls.name] = cls
    return cls

class ExecutionBackend(ABC):
    """Defines how workloads are executed."""
    name: str

    def __init__(self, num_processors: int = 1) -> None:
        self.num_processors = num_processors

    @abstractmethod
    def run(self, runner) -> list[NodeResult]:
        pass

    # Shared execution unit used by all backends
    def _execute_single(self, runner, context=None):
        workload = runner.get_workload()
        measurements = runner.get_measurements()
        workload_cfg = runner.get_workload_cfg()

        manager = MeasurementManager(measurements)

        if context and context.comm:
            context.comm.Barrier()

        manager.start()

        if context and context.comm:
            context.comm.Barrier()

        workload.run(self.num_processors, workload_cfg, context=context)

        if context and context.comm:
            context.comm.Barrier()

        manager.stop()

        return manager.collect()

    def get_processors(self) -> int | None:
        return self.num_processors
