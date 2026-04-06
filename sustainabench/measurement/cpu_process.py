import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class ProcessCPUMeasurement(Measurement):
    name = "process_cpu"
    poll_interval = 0.1  # seconds

    def start(self):
        self.proc = psutil.Process()
        self.proc.cpu_percent(None)
        self.samples = []

    def sample(self):
        total = self.proc.cpu_percent(None)

        for child in self.proc.children(recursive=True):
            try:
                total += child.cpu_percent(None)
            except psutil.NoSuchProcess:
                pass

        self.samples.append(total)

    def stop(self):
        pass

    def result(self):
        print(self.samples)
        return {
            "cpu_process_avg_percent": sum(self.samples) / len(self.samples),
            "cpu_process_max_percent": max(self.samples),
        }
