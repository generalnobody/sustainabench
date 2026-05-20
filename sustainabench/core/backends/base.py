from abc import ABC, abstractmethod
from typing import Dict, Type, Any
from sustainabench.measurement.manager import MeasurementManager
from sustainabench.schemas.results.benchmark import NodeResult
from sustainabench.workloads.base import InternalWorkload, ExternalWorkload
from dataclasses import dataclass
import subprocess
import json
from pydantic import ValidationError

BACKENDS: Dict[str, Type["ExecutionBackend"]] = {}

def register_backend(cls):
    """Macro used by each backend to register in BACKENDS"""
    BACKENDS[cls.name] = cls
    return cls

class ExecutionBackend(ABC):
    """Defines how workloads are executed."""
    name: str

    def __init__(self, num_processors, node_processors, hostfile) -> None:
        self.num_processors = num_processors
        self.node_processors = node_processors
        self.hostfile = hostfile

    def add_result(self, node_results: list[NodeResult], result: dict[str, Any]):
        index = {r.node_id: r for r in node_results}
        for node_id, metrics in result.items():
            if node_id in index:
                index[node_id].metrics.update(NodeResult.normalize_metric_keys(metrics))
            else:
                node_results.append(NodeResult(node_id=node_id, metrics=metrics, metadata={}))

        return node_results

    @abstractmethod
    def run(self, runner) -> list[NodeResult]:
        pass

    @abstractmethod
    def get_wrap_command(self) -> list[str]:
        pass

    # Shared execution unit used by all backends
    def _execute_single(self, runner, context=None):
        workload = runner.get_workload()
        measurements = runner.get_measurements()

        manager = MeasurementManager(measurements)

        if context and context.comm:
            context.comm.Barrier()

        manager.start()

        if context and context.comm:
            context.comm.Barrier()

        if isinstance(workload, InternalWorkload):
            workload.run(self.num_processors, context=context)
        elif isinstance(workload, ExternalWorkload):
            workload.execute()

        if context and context.comm:
            context.comm.Barrier()

        manager.stop()

        return manager.collect()

    def get_processors(self) -> int | None:
        return self.num_processors
