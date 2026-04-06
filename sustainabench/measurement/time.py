import time

from sustainabench.measurement.base import  Measurement, register_measurement


@register_measurement
class TimeMeasurement(Measurement):
    name = "time"

    def start(self):
        self.t0 = time.perf_counter()

    def stop(self):
        self.t1 = time.perf_counter()

    def sample(self):
        pass

    def result(self):
        return {"execution_time": self.t1 - self.t0}
