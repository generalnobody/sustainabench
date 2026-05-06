from .base import ExecutionBackend, register_backend
from ..models import BenchmarkResult, NodeResult
from sustainabench.utils.system_info import get_node_metadata

@register_backend
class LocalBackend(ExecutionBackend):
    """Runs benchmark locally."""
    name = "local"

    def run(self, runner):
        raw_metrics = self._execute_single(runner, None)

        return [NodeResult(
            self.name,
            raw_metrics,
            get_node_metadata()
        )]
