from pathlib import Path
from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.measurement.base import ExternalMeasurement
from sustainabench.schemas.results.benchmark import BenchmarkResult

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, workload_cfg, measurement_names, runs, backend):
        if workload_name not in WORKLOADS:
            raise ValueError(f"Unknown workload: {workload_name}")
        
        self.workload = WORKLOADS[workload_name](workload_cfg)

        measurement_dict = {}
        for name in measurement_names:
            file = ""
            if "=" in name:
                name, file = name.split("=", 1)
            if name not in MEASUREMENTS:
                raise ValueError(f"Unknown measurement: {name}")
            measurement_dict[name] = file

        self.measurements = [
            MEASUREMENTS[name](file)
            for name, file in measurement_dict.items()
        ]

        for measurement in self.measurements: # Check if all indicators got their required files
            if measurement.require_file and measurement_dict[measurement.name] == "":
                raise ValueError(f"File not provided for indicator '{measurement.name}'. Use as follows: -i {measurement.name}=<file>.")

        if runs < 1:
            raise ValueError(f"Cannot perform {runs} runs")
            
        self.runs = runs
        self.backend = backend

    def run(self) -> BenchmarkResult:
        """Function that runs the benchmark on the correct backend (only internal measurements)"""
        results = {}
        for i in range(self.runs):
            node_results = self.backend.run(self)

            if node_results:
                results[f"run{i}"] = node_results

        return BenchmarkResult(
            workload=self.workload.name,
            backend=self.backend.name,
            results=results,
            metadata={}
        )

    def get_measurements(self):
        return self.measurements

    def get_workload(self):
        return self.workload

    def get_runs(self):
        return self.runs