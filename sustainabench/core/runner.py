from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.indicators import INDICATORS
from sustainabench.measurement.manager import MeasurementManager
import psutil

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, measurement_names, backend):
        # self.workload_name = workload_name
        # self.measurement_names = measurement_names
        # self.indicator_names = indicator_names
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

        # for name in indicator_names:
        #     if name not in INDICATORS:
        #         raise ValueError(f"Unknown indicator: {name}")
            
        # self.indicators = [
        #     INDICATORS[name]()
        #     for name in indicator_names
        # ]

        self.backend = backend        

    def _run_local(self, num_processors):
        """Run the benchmark locally"""

        manager = MeasurementManager(self.measurements)

        manager.start()

        self.workload.run(num_processors)

        manager.stop()

        raw_metrics = manager.collect()

        # for ind in self.indicators:
        #     computed.update(ind.compute(raw_metrics))

        return raw_metrics
    
    def run(self):
        """Function that runs the benchmark on the correct backend"""
        return self.backend.run(self)