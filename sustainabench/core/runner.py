from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.indicators import INDICATORS

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, measurement_names, indicator_names, backend):
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

        for name in indicator_names:
            if name not in INDICATORS:
                raise ValueError(f"Unknown indicator: {name}")
            
        self.indicators = [
            INDICATORS[name]()
            for name in indicator_names
        ]

        self.backend = backend        

    def _run_local(self):
        """Run the benchmark locally"""
        for m in self.measurements:
            m.start()

        self.workload.run()

        raw_metrics = {}
        for m in self.measurements:
            m.stop()
            raw_metrics.update(m.result())

        computed = {}
        for ind in self.indicators:
            computed.update(ind.compute(raw_metrics))

        return raw_metrics, computed
    
    def run(self):
        """Function that runs the benchmark on the correct backend"""
        return self.backend.run(self)