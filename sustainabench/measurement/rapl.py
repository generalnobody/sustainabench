from sustainabench.measurement.base import Measurement, register_measurement

@register_measurement
class RAPLMeasurement(Measurement):
    name = "rapl"
    poll_interval = None
    scope = "node"

    def start(self):
        import pyRAPL

        pyRAPL.setup()
        self.meter = pyRAPL.Measurement("benchmark")
        self.meter.begin()

    def stop(self):
        self.meter.end()

    def sample(self):
        pass  # not used

    def result(self):
        result = self.meter.result

        # pkg is per CPU socket — sum them
        energy_uj = sum(result.pkg) if result.pkg else 0

        return {
            "energy_uj": energy_uj,
            "energy_kwh": energy_uj / 3.6e9,
        }
