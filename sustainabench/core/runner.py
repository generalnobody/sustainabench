from sustainabench.workloads import WORKLOADS   

# class BenchmarkRunner:

#     def __init__(self, workload, measurements, indicators):
#         self.workload = workload
#         self.measurements = measurements
#         self.indicators = indicators

#     def execute(self):

#         self.workload.setup()

#         for m in self.measurements:
#             m.start()

#         self.workload.run()

#         raw_metrics = {}
#         for m in self.measurements:
#             raw_metrics.update(m.stop())

#         self.workload.teardown()

#         computed = {}
#         for ind in self.indicators:
#             computed.update(ind.compute(raw_metrics))

#         return raw_metrics, computed


class BenchmarkRunner:

    def __init__(self, workload_name, measurements, indicators):
        self.workload_name = workload_name
        self.measurements = measurements
        self.indicators = indicators

    def run(self):

        if self.workload_name not in WORKLOADS:
            raise ValueError(f"Unknown workload: {self.workload_name}")

        workload_cls = WORKLOADS[self.workload_name]
        workload = workload_cls()

        for m in self.measurements:
            m.start()

        workload.run()

        raw_metrics = {}
        for m in self.measurements:
            raw_metrics.update(m.stop())

        # workload.teardown()

        computed = {}
        for ind in self.indicators:
            computed.update(ind.compute(raw_metrics))

        return raw_metrics, computed
