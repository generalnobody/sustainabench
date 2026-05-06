import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class MemoryMeasurement(Measurement):
    name = "memory"
    poll_interval = 0.1
    scope = "node"
    require_file = False

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
            f"{self.name}": {
                "mem": {
                    "mb": {
                        "avg": mem_avg,
                        "max": mem_max
                    },
                    "pct": {
                        "avg": mem_avg_pct,
                        "max": mem_max_pct
                    }
                },
                "swap": {
                    "mb": {
                        "avg": swap_avg,
                        "max": swap_max
                    },
                    "pct": {
                        "avg": swap_avg_pct,
                        "max": swap_max_pct
                    }
                }
            }
        }