from sustainabench.measurement.base import InternalMeasurement, register_measurement


@register_measurement
class NoneMeasurement(InternalMeasurement): # Technically run as an internal measurement, just not included among the other internal measurements as its sole purpose is being useless.
    """Dummy measurement. Useful when running external workloads that have their own measurement systems."""
    name = "none"
    poll_interval = None
    
    require_file = False

    def start(self):
        pass

    def sample(self):
        pass

    def stop(self):
        pass

    def result(self):
        return {}