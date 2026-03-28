import time
from sustainabench.core.interfaces import MeasurementSource


class TimeMeasurement(MeasurementSource):

    def start(self):
        self.start_time = time.time()

    def stop(self):
        return {
            "runtime_sec": time.time() - self.start_time
        }
