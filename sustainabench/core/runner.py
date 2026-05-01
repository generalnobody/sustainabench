from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from .models import BenchmarkResult

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, workload_cfg, measurement_names, runs, backend):
        if workload_name not in WORKLOADS:
            raise ValueError(f"Unknown workload: {workload_name}")
        
        self.workload = WORKLOADS[workload_name]()

        self.workload_cfg = workload_cfg

        for name in measurement_names:
            if name not in MEASUREMENTS:
                raise ValueError(f"Unknown measurement: {name}")

        self.measurements = [
            MEASUREMENTS[name]()
            for name in measurement_names
        ]

        if runs < 1:
            raise ValueError(f"Cannot perform {runs} runs")
            
        self.runs = runs
        self.backend = backend

    def run(self) -> BenchmarkResult:
        """Function that runs the benchmark on the correct backend"""
        return self.backend.run(self)

    def get_measurements(self):
        return self.measurements

    def get_workload(self):
        return self.workload

    def get_runs(self):
        return self.runs

    def get_workload_cfg(self):
        return self.workload_cfg