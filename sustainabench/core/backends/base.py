from abc import ABC, abstractmethod
from typing import Dict, Type
from ..models import BenchmarkResult
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
    def run(self, runner) -> BenchmarkResult:
        pass

    # Shared execution unit used by all backends
    def _execute_single(self, runner, context=None):
        workload = runner.get_workload()
        measurements = runner.get_measurements()
        runs = runner.get_runs()
        workload_cfg = runner.get_workload_cfg()

        results = {}

        for i in range(runs):
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

            results[f"run{i}"] = manager.collect()

        return results
