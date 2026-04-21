from sustainabench.workloads.base import Workload, register_workload


@register_workload
class CPUSingleWorkload(Workload):
    """Single-threaded CPU workload. Performs prime checking"""
    name = "cpu-single"

    def _is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0:
                return False
        return True

    def run(self, num_processors: int, workload_cfg):
        limit = 100
        if workload_cfg:
            limit = workload_cfg["workload"]["params"]["limit"]

        count = 0
        for n in range(2, limit):
            if self._is_prime(n):
                count += 1

        print(f"[cpu-single] Found primes: {count}")
