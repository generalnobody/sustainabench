import multiprocessing as mp
from sustainabench.workloads.base import Workload, register_workload
from pydantic import BaseModel

@register_workload
class CPUMultiWorkload(Workload):
    """Multi-threaded CPU workload. Performs prime checking"""
    name = "cpu-multi"

    class WorkloadParams(BaseModel):
        limit: int = 100

    def _work(self, n):
        count = 0
        for i in range(2, n):
            prime = True
            for j in range(2, int(i**0.5)+1):
                if i % j == 0:
                    prime = False
                    break
            if prime:
                count += 1
        return count

    def run(self, num_processors: int, context=None):

        if self.workload_cfg is None:
            params = self.WorkloadParams()
        else:
            params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)

        with mp.Pool(num_processors) as pool:
            results = pool.map(self._work, [params.limit]*num_processors)

        print(f"[cpu-multi] Found total primes: {sum(results)}")
