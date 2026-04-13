from .base import ExecutionBackend, register_backend
from ..models import BenchmarkResult, NodeResult
from sustainabench.utils.system_info import get_node_metadata

@register_backend
class LocalBackend(ExecutionBackend):
    """Runs benchmark locally."""
    name = "local"

    def __init__(self, num_processors: int = 1) -> None:
        self.num_processors = num_processors

    def run(self, runner):
        raw_metrics = runner._run_local(self.num_processors)

        results = BenchmarkResult(
            runner.get_workload_name(),
            [NodeResult(self.name, raw_metrics, get_node_metadata())],
            {}
        )
        return results
