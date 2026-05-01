from .base import ExecutionBackend, register_backend
from ..models import BenchmarkResult, NodeResult
from sustainabench.utils.system_info import get_node_metadata

@register_backend
class LocalBackend(ExecutionBackend):
    """Runs benchmark locally."""
    name = "local"

    def run(self, runner):
        raw_metrics = runner._run_local(self.num_processors)

        results = BenchmarkResult(
            runner.get_workload().name,
            [NodeResult(self.name, raw_metrics, get_node_metadata())],
            {}
        )
        return results
