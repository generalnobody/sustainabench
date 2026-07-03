import psutil
from sustainabench.measurement.base import InternalMeasurement, register_measurement


@register_measurement
class MemoryMeasurement(InternalMeasurement):
    name = "memory"
    poll_interval = 0.1
    
    require_file = False

    def start(self):
        self.root_process = psutil.Process()
        self.samples = []

    def sample(self):        
        processes = [self.root_process]

        try:
            processes.extend(self.root_process.children(recursive=True))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        rss = 0 # Resident Sample Size. Represents memory used
        for proc in processes:
            try:
                rss += proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        self.samples.append(rss / 1024**2) # MB

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
