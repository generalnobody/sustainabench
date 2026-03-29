from typing import Tuple
from sustainabench.core.backend import ExecutionBackend
import ray


@ray.remote
def _ray_execute(runner):
    return runner._run_local()


class RayBackend(ExecutionBackend):

    def __init__(self, num_workers: int = 1):
        self.num_workers = num_workers
        ray.init(ignore_reinit_error=True)

    def run(self, runner):
        futures = [
            _ray_execute.remote(runner)
            for _ in range(self.num_workers)
        ]

        results = ray.get(futures)

        raws = [r[0] for r in results]
        inds = [r[1] for r in results]

        # simple aggregation
        aggregated_raw = {
            k: sum(d[k] for d in raws) / len(raws)
            for k in raws[0]
        }

        aggregated_indicators = {
            k: sum(d[k] for d in inds) / len(inds)
            for k in inds[0]
        }

        return aggregated_raw, aggregated_indicators
