from typing import Tuple
from .base import ExecutionBackend, register_backend
import ray


@ray.remote
def _ray_execute(runner):
    return runner._run_local(num_processors=1)

@register_backend
class RayBackend(ExecutionBackend):
    """Runs benchmark using Ray (used for distributed execution)"""
    name = "ray"

    def __init__(self, num_processors: int = 1, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.num_workers = num_processors
        ray.init(ignore_reinit_error=True)

    def run(self, runner):
        futures = [
            _ray_execute.remote(runner)
            for _ in range(self.num_workers)
        ]

        results = ray.get(futures)

        # raws = [r[0] for r in results]

        # simple aggregation
        aggregated = {}
        for k in raws[0]:
            values = [d.get(k) for d in raws if k in d]
            if all(isinstance(v, (int, float)) for v in values):
                aggregated[k] = sum(values) / len(values)

        return aggregated_raw
