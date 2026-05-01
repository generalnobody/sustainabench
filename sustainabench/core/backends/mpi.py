from .base import ExecutionBackend, register_backend
from ..models import BenchmarkResult, NodeResult
from sustainabench.utils.system_info import get_node_metadata
from ..context import ExecutionContext

@register_backend
class MPIBackend(ExecutionBackend):
    name = "mpi"

    def run(self, runner):
        from mpi4py import MPI

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        context = ExecutionContext(
            backend=self.name,
            rank=rank,
            world_size=size,
            comm=comm
        )

        comm.Barrier()

        local_metrics = self._execute_single(runner, context=context)
        metadata = get_node_metadata()

        comm.Barrier()

        gathered = comm.gather((local_metrics, metadata), root=0)

        node_results = []
        if rank == 0 and gathered:
            node_results = [
                NodeResult(f"rank_{i}", m, meta)
                for i, (m, meta) in enumerate(gathered)
            ]
        elif rank == 0 and not gathered:
            raise ValueError("MPI: gathered benchmarking results not present at root rank")
        
        return BenchmarkResult(
            runner.get_workload().name,
            node_results,
            {
                self.name: {"world_size": size}
            }
        )