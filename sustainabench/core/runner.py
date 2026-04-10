from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.indicators import INDICATORS
from sustainabench.measurement.manager import MeasurementManager
import psutil

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, measurement_names, backend):
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

        self.backend = backend        

    def _run_local(self, num_processors: int):
        """Run the benchmark locally"""

        manager = MeasurementManager(self.measurements)

        manager.start()

        self.workload.run(num_processors)

        manager.stop()

        raw_metrics = manager.collect()

        return raw_metrics
    
    def run(self):
        """Function that runs the benchmark on the correct backend"""
        return self.backend.run(self)