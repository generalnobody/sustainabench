import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class MemoryMeasurement(Measurement):
    name = "mem"
    poll_interval = 0.1
    scope = "node"

    def start(self):
        self.samples = []

    def sample(self):
        mem = psutil.virtual_memory()
        used_mb = mem.used / 1024**2
        percent = mem.percent
        self.samples.append((used_mb, percent))

    def stop(self):
        pass

    def result(self):
        if not self.samples:
            return {}

        mem_avg = sum(sample[0] for sample in self.samples) / len(self.samples)
        mem_max = max(sample[0] for sample in self.samples)
        return {
            "mem_avg_mb": mem_avg,
            "mem_max_mb": mem_max
        }