from multiprocessing import Pool
import numpy as np
import os
from sustainabench.workloads.base import Workload, register_workload

def worker(_):
            a = np.random.rand(1500,1500)
            b = np.random.rand(1500,1500)
            return a @ b

@register_workload
class CPUMatrixMultiWorkload(Workload):
    """Multi-threaded CPU Matrix-Multiplication workload"""
    name = "cpu-mm"

    def run(self):
        cores = os.cpu_count() or 1

        with Pool(cores) as p:
            p.map(worker, range(cores * 2))