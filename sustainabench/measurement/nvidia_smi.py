import pynvml
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class CPUMeasurement(Measurement):

    name = "nv-pow"
    poll_interval = 0.1
    scope = "node"

    def start(self):
        self.samples = []
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    def sample(self):
        self.samples.append(pynvml.nvmlDeviceGetPowerUsage(self.handle))

    def stop(self):
        pynvml.nvmlShutdown()
        pass

    def result(self):
        if not self.samples:
            return {"cpu_avg": 0, "cpu_max": 0}

        return {
            "nv-pow-mW": self.samples
        }
