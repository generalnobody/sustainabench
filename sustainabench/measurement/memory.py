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
        mem_used_mb = mem.used / 1024**2

        swap = psutil.swap_memory()
        swap_used_mb = swap.used / 1024**2

        self.samples.append((mem_used_mb, mem.percent, swap_used_mb, swap.percent))

    def stop(self):
        pass

    def result(self):
        if not self.samples:
            return {}

        mem_avg = sum(sample[0] for sample in self.samples) / len(self.samples)
        mem_max = max(sample[0] for sample in self.samples)
        mem_avg_pct = sum(sample[1] for sample in self.samples) / len(self.samples)
        mem_max_pct = max(sample[1] for sample in self.samples)

        swap_avg = sum(sample[2] for sample in self.samples) / len(self.samples)
        swap_max = max(sample[2] for sample in self.samples)
        swap_avg_pct = sum(sample[3] for sample in self.samples) / len(self.samples)
        swap_max_pct = max(sample[3] for sample in self.samples)
        return {
            "mem": {
                "avg_mb": mem_avg,
                "max_mb": mem_max,
                "avg_pct": mem_avg_pct,
                "max_pct": mem_max_pct
            },
            "swap": {
                "avg_mb": swap_avg,
                "max_mb": swap_max,
                "avg_pct": swap_avg_pct,
                "max_pct": swap_max_pct
            }
        }