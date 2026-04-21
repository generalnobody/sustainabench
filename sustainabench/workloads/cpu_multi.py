# import multiprocessing as mp
# import time

# def work(n):
#     count = 0
#     for i in range(2, n):
#         prime = True
#         for j in range(2, int(i**0.5)+1):
#             if i % j == 0:
#                 prime = False
#                 break
#         if prime:
#             count += 1
#     return count

# def run(workers=mp.cpu_count(), n=20000):
#     start = time.time()

#     with mp.Pool(workers) as pool:
#         results = pool.map(work, [n]*workers)

#     print(f"[cpu_multi] total primes: {sum(results)} in {time.time()-start:.2f}s")

import multiprocessing as mp
from sustainabench.workloads.base import Workload, register_workload


@register_workload
class CPUMultiWorkload(Workload):
    """Single-threaded CPU workload. Performs prime checking"""
    name = "cpu-multi"

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

    def run(self, num_processors: int, workload_cfg):
        limit = 100
        if workload_cfg:
            limit = workload_cfg["workload"]["params"]["limit"]

        with mp.Pool(num_processors) as pool:
            results = pool.map(self._work, [limit]*num_processors)

        print(f"[cpu-multi] Found total primes: {sum(results)}")
