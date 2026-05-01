class ExecutionContext:
    def __init__(self, backend, rank=0, world_size=1, comm=None):
        self.backend = backend
        self.rank = rank
        self.world_size = world_size
        self.comm = comm

    def is_distributed(self):
        return self.world_size > 1
