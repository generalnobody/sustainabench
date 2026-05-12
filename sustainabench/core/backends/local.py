from .base import ExecutionBackend, register_backend
from sustainabench.utils.system_info import get_node_metadata
from sustainabench.schemas.results.benchmark import NodeResult
from sustainabench.workloads.base import ExternalWorkload

@register_backend
class LocalBackend(ExecutionBackend):
    """Runs benchmark locally."""
    name = "local"

    def run(self, runner):
        raw_metrics = self._execute_single(runner, None)

        results = [NodeResult(
            node_id=self.name,
            metrics=raw_metrics,
            metadata=get_node_metadata()
        )]

        workload = runner.get_workload()
        if isinstance(workload, ExternalWorkload):
            extra_results = workload.process(self.name)
            results = self.add_result(results, extra_results)
        
        return results
