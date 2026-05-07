from sustainabench.workloads.base import Workload, register_workload

@register_workload
class MPIPingPong(Workload):
    name = "mpi-pingpong"

    def run(self, num_processors, context=None):
        if not context:
            raise ValueError(f"Workload {self.name} relies on MPI. Please ensure MPI backend is correctly configured and run again")

        comm = context.comm
        rank = context.rank

        if context.world_size < 2:
            raise RuntimeError("Need at least 2 ranks")

        msg = b"hello"

        for _ in range(5):
            if rank == 0:
                comm.send(msg, dest=1)
                recv = comm.recv(source=1)
                print(f"Rank {rank}: {recv}")
            elif rank == 1:
                data = comm.recv(source=0)
                recv = comm.send(data, dest=0)
                print(f"Rank {rank}: {recv}")
