import os
# Set OS environment variables to ensure single-threaded execution
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import numpy as np
from sustainabench.workloads.base import InternalWorkload, register_workload


@register_workload
class CPUMatrixSingleWorkload(InternalWorkload):
    """Single-threaded CPU Matrix-Multiplication workload"""
    name = "cpu-ms"

    def run(self, num_processors: int, context=None):
        a = np.random.rand(2000, 2000)
        b = np.random.rand(2000, 2000)
        for _ in range(5): # Run operation 5 times to ensure longer sustained load
            _ = a @ b
