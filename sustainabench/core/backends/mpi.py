from .base import ExecutionBackend, register_backend
from sustainabench.utils.system_info import get_node_metadata
from ..context import ExecutionContext
from sustainabench.schemas.results.benchmark import NodeResult
from sustainabench.workloads.base import ExternalWorkload

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

            hostnames = [meta["hostname"] for _, meta in gathered]

            local_rank_map = {}
            local_ranks = []
            for h in hostnames:
                local_rank = local_rank_map.get(h, 0)
                local_ranks.append(local_rank)
                local_rank_map[h] = local_rank + 1

            node_results = [
                NodeResult(node_id=f"{meta['hostname']}:{i}:{local_ranks[i]}", metrics=m, metadata=meta)
                for i, (m, meta) in enumerate(gathered)
            ]

            workload = runner.get_workload()
            if isinstance(workload, ExternalWorkload):
                extra_results = workload.process(self.name)
                node_results = self.add_result(node_results, extra_results)
        elif rank == 0 and not gathered:
            raise ValueError("MPI: gathered benchmarking results not present at root rank")
        
        return node_results