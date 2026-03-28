from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.indicators import INDICATORS

class BenchmarkRunner:

    def __init__(self, workload_name, measurement_names, indicator_names):
        self.workload_name = workload_name
        self.measurement_names = measurement_names
        self.indicator_names = indicator_names

    def run(self):

        if self.workload_name not in WORKLOADS:
            raise ValueError(f"Unknown workload: {self.workload_name}")

        workload_cls = WORKLOADS[self.workload_name]
        workload = workload_cls()

        measurements = [
            MEASUREMENTS[name]()
            for name in self.measurement_names
        ]

        indicators = [
            INDICATORS[name]()
            for name in self.indicator_names
        ]

        for m in measurements:
            m.start()

        workload.run()

        raw_metrics = {}
        for m in measurements:
            m.stop()
            raw_metrics.update(m.result())

        # workload.teardown()

        computed = {}
        for ind in indicators:
            computed.update(ind.compute(raw_metrics))

        return raw_metrics, computed
