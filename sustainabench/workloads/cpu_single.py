from sustainabench.workloads.base import Workload, register_workload
from pydantic import BaseModel

@register_workload
class CPUSingleWorkload(Workload):
    """Single-threaded CPU workload. Performs prime checking"""
    name = "cpu-single"

    class WorkloadParams(BaseModel):
        limit: int = 100

    def _is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0:
                return False
        return True

    def run(self, num_processors: int, context=None):
        if self.workload_cfg is None:
            params = self.WorkloadParams()
        else:
            params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)

        count = 0
        for n in range(2, params.limit):
            if self._is_prime(n):
                count += 1

        print(f"[cpu-single] Found primes: {count}")
