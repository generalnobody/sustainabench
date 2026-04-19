import pynvml
import time
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class NvidiaGPUMeasurement(Measurement):

    name = "gpu-nv"
    poll_interval = 0.1
    scope = "node"

    def start(self):
        self.samples = []
        self.utils = []
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    def sample(self):
        self.samples.append((pynvml.nvmlDeviceGetPowerUsage(self.handle), time.perf_counter())) # Create list of tuples (mW, timestamp)
        self.utils.append(pynvml.nvmlDeviceGetUtilizationRates(self.handle).gpu)

    def stop(self):
        pynvml.nvmlShutdown()

    def result(self):
        if len(self.samples) < 2:
            return {
                "avg_util": 0,
                "peak_util": 0,
                "energy_j": 0,
                "energy_kwh": 0,
                "pow_avg": 0,
                "raw": {
                    "pow": self.samples,
                    "utils": self.utils,
                }
            }

        energy_j = 0.0

        for i in range(1, len(self.samples)): # Calculate energy used in joules
            mw1, t1 = self.samples[i]
            mw0, t0 = self.samples[i-1]
            dt = t1 - t0
            avg_power_w = (mw1 + mw0) / 2 / 1000 # Average power between two measurements, converted from mW to W, using trapezoidal rule
            energy_j += avg_power_w * dt

        total_time = self.samples[-1][1] - self.samples[0][1]
        average_power_w = energy_j / total_time

        energy_kwh = energy_j / 3600000

        return {
            "avg_util": sum(self.utils) / len(self.utils),
            "peak_util": max(self.utils),
            "energy_j": energy_j,
            "energy_kwh": energy_kwh,
            "pow_avg": average_power_w,
            "raw": {
                "pow": self.samples,
                "utils": self.utils,
            }
        }
        
