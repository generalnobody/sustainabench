from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.indicators import INDICATORS
from sustainabench.measurement.manager import MeasurementManager
import psutil
from .models import BenchmarkResult

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, measurement_names, runs, backend):
        if workload_name not in WORKLOADS:
            raise ValueError(f"Unknown workload: {workload_name}")
        
        self.workload = WORKLOADS[workload_name]()

        for name in measurement_names:
            if name not in MEASUREMENTS:
                raise ValueError(f"Unknown measurement: {name}")

        self.measurements = [
            MEASUREMENTS[name]()
            for name in measurement_names
        ]

        if runs >= 1:
            self.runs = runs
        else:
            raise ValueError(f"Runs amount lower than 1: {runs}")

        self.backend = backend        

    def _run_local(self, num_processors: int):
        """Run the benchmark locally"""

        measurements = {}
        for i in range(self.runs):
            manager = MeasurementManager(self.measurements)
            manager.start()
            self.workload.run(num_processors)
            manager.stop()
            raw_metrics = manager.collect()

            measurements[f"run{i}"] = raw_metrics
        

        return measurements
    
    def get_measurements(self): # Expose selected measurements
        return self.measurements

    def run(self) -> BenchmarkResult:
        """Function that runs the benchmark on the correct backend"""
        return self.backend.run(self)
    
    def get_workload_name(self):
        return self.workload.name