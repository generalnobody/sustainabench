import time
import numpy as np
from sustainabench.core.interfaces import Workload


class CPUMatrixWorkload(Workload):
    name = "cpu_matrix"

    def setup(self):
        pass

    def run(self):
        a = np.random.rand(2000, 2000)
        b = np.random.rand(2000, 2000)
        _ = a @ b

    def teardown(self):
        pass
