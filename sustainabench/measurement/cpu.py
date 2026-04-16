import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class CPUMeasurement(Measurement):
    name = "cpu-usage"
    poll_interval = 0.1
    scope = "node"

    def start(self):
        self.samples = []
        psutil.cpu_percent(interval=None) # Ignore first bogus value
        psutil.cpu_percent(interval=None, percpu=True)

    def sample(self):
        self.samples.append((
            psutil.cpu_percent(interval=None),
            psutil.cpu_percent(interval=None, percpu=True)
        ))

    def stop(self):
        pass

    def result(self):
        if not self.samples:
            return {"cpu_avg": 0, "cpu_max": 0, "per-core": {}}

        cpu_avg = sum(sample[0] for sample in self.samples) / len(self.samples)
        cpu_max = sum(sample[0] for sample in self.samples)

        per_cpu_avg = [
            sum(col) / len(col)
            for col in zip(*(sample[1] for sample in self.samples))
        ]
        per_cpu_max = [
            max(col)
            for col in zip(*(sample[1] for sample in self.samples))
        ]

        return {
            "cpu_avg": cpu_avg,
            "cpu_max": cpu_max,
            "per_cpu_avg": per_cpu_avg,
            "per_cpu_max": per_cpu_max
        }