import pynvml
import time
from sustainabench.measurement.base import InternalMeasurement, register_measurement


@register_measurement
class NvidiaGPUMeasurement(InternalMeasurement):

    name = "gpu-nv"
    poll_interval = 0.1
    
    require_file = False

    def start(self):
        pynvml.nvmlInit()
        self.gpu_count = pynvml.nvmlDeviceGetCount()
        self.handles = [
            pynvml.nvmlDeviceGetHandleByIndex(i)
            for i in range(self.gpu_count)
        ]
        self.samples = [[] for _ in self.handles]
        # self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    def sample(self):
        for i in range(self.gpu_count):
            self.samples[i].append((
                time.perf_counter(), 
                pynvml.nvmlDeviceGetPowerUsage(self.handles[i]), 
                pynvml.nvmlDeviceGetUtilizationRates(self.handles[i]).gpu, 
                pynvml.nvmlDeviceGetTemperature(self.handles[i], pynvml.NVML_TEMPERATURE_GPU),
                pynvml.nvmlDeviceGetClockInfo(self.handles[i], pynvml.NVML_CLOCK_SM)
            ))
        # self.samples.append((pynvml.nvmlDeviceGetPowerUsage(self.handle), time.perf_counter())) # Create list of tuples (mW, timestamp)
        # self.utils.append(pynvml.nvmlDeviceGetUtilizationRates(self.handle).gpu)

    def stop(self):
        pynvml.nvmlShutdown()

    def result(self):
        if len(self.samples) < 1: # No GPU-s available
            return {}
        
        results = []

        # Per-gpu loop
        for i, samples in enumerate(self.samples):
            length = len(samples)
            if length < 2: # Not enough samples
                continue

            # Energy calculation
            energy_j = 0.0
            for j in range(1, length):
                t1, mw1, *_ = samples[j]
                t0, mw0, *_ = samples[j-1]
                dt = t1 - t0
                avg_power_w = (mw1 + mw0) / 2 / 1000 # Average power between two measurements, converted from mW to W, using trapezoidal rule
                energy_j += avg_power_w * dt

            total_time = samples[-1][0] - samples[0][0]
            average_power_w = energy_j / total_time
            energy_kwh = energy_j / 3.6e6

            # Util
            avg_util = sum(sample[2] for sample in samples)/length
            max_util = max(sample[2] for sample in samples)

            # Temp
            avg_temp = sum(sample[3] for sample in samples)/length
            max_temp = max(sample[3] for sample in samples)

            # Clock
            avg_clock = sum(sample[4] for sample in samples)/length
            max_clock = max(sample[4] for sample in samples)

            results.append({
                "gpu_id": i,
                "energy": {
                    "j": energy_j,
                    "kwh": energy_kwh
                },
                "power": {
                    "avg_w": average_power_w
                },
                "util": {
                    "avg": avg_util,
                    "max": max_util
                },
                "temp": {
                    "avg": avg_temp,
                    "max": max_temp
                },
                "clock": {
                    "avg": avg_clock,
                    "max": max_clock
                }
            })

        return {
            f"{self.name}": results
        }
    