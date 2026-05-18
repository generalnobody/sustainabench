from .base import ExecutionBackend, register_backend
from sustainabench.utils.system_info import get_node_metadata, get_mpi_ranks
from sustainabench.schemas.results.benchmark import NodeResult
from sustainabench.workloads.base import ExternalWorkload

@register_backend
class LocalBackend(ExecutionBackend):
    """Runs benchmark locally."""
    name = "local"

    def get_wrap_command(self):
        raise RuntimeError(f"Backend {self.name} does not support command wrapping. Please ensure the correct backend is selected for the chosen workload, as it seems to require wrapping.")

    def run(self, runner):
        raw_metrics = self._execute_single(runner, None)

        metadata = get_node_metadata()
        rank, local_rank = get_mpi_ranks()
        node_id = f"{metadata['hostname']}:{rank}:{local_rank}" if local_rank else f"{metadata['hostname']}:{rank}" if rank else self.name

        results = [NodeResult(
            node_id=node_id,
            metrics=raw_metrics,
            metadata=metadata
        )]

        workload = runner.get_workload()
        if isinstance(workload, ExternalWorkload):
            extra_results = workload.process(self.name)
            results = self.add_result(results, extra_results)
        
        return results
