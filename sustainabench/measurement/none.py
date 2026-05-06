from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class NoneMeasurement(Measurement):
    """Dummy measurement. Useful when running external workloads that have their own measurement systems."""
    name = "none"
    poll_interval = None
    scope = "node"
    require_file = False

    def start(self):
        pass

    def sample(self):
        pass

    def stop(self):
        pass

    def result(self):
        return {}