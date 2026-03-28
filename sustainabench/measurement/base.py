# import time
# from sustainabench.core.interfaces import MeasurementSource


# class TimeMeasurement(MeasurementSource):

#     def start(self):
#         self.start_time = time.time()

#     def stop(self):
#         return {
#             "runtime_sec": time.time() - self.start_time
#         }

from abc import ABC, abstractmethod
from typing import Dict, Type

MEASUREMENTS: Dict[str, Type["Measurement"]] = {}

def register_measurement(cls):
    MEASUREMENTS[cls.name] = cls
    return cls


class Measurement(ABC):
    name: str

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def result(self) -> dict:
        pass
