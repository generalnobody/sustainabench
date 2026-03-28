class BenchmarkRunner:

    def __init__(self, workload, measurements, indicators):
        self.workload = workload
        self.measurements = measurements
        self.indicators = indicators

    def execute(self):

        self.workload.setup()

        for m in self.measurements:
            m.start()

        self.workload.run()

        raw_metrics = {}
        for m in self.measurements:
            raw_metrics.update(m.stop())

        self.workload.teardown()

        computed = {}
        for ind in self.indicators:
            computed.update(ind.compute(raw_metrics))

        return raw_metrics, computed
