import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class CPUMeasurement(Measurement):

    name = "cpu"
    poll_interval = 0.1

    def start(self):
        self.samples = []

    def sample(self):
        self.samples.append(psutil.cpu_percent())

    def stop(self):
        pass

    def result(self):
        return {
            "cpu_avg": sum(self.samples) / len(self.samples),
            "cpu_max": max(self.samples),
        }
