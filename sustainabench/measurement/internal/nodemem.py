import psutil
import os
from sustainabench.measurement.base import InternalMeasurement, register_measurement


@register_measurement
class NodeMemoryMeasurement(InternalMeasurement):
    name = "nodemem" # Used when memory measurement cannot be used as too many MPI ranks
    poll_interval = 0.1
    
    require_file = False
    only_once_per_node = True

    def start(self):
        self.uid = os.getuid()
        self.samples = []

    def sample(self):        
        total = 0
        for p in psutil.process_iter(['pid', 'uids']):
            try:
                if p.uids().real != self.uid:
                    continue
                total += p.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self.samples.append(total / 1024**2) # MB

    def stop(self):
        pass

    def result(self):
        if not self.samples:
            return {}
        
        return {
            self.name: {
                "rss": {
                    "mb": {
                        "avg": sum(self.samples) / len(self.samples),
                        "max": max(self.samples),
                        "min": min(self.samples)
                    }
                }
            }
        }
