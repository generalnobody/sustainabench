from sustainabench.core.interfaces import Indicator


class CarbonIndicator(Indicator):

    def __init__(self, carbon_intensity):
        self.ci = carbon_intensity  # gCO2/kWh

    def compute(self, metrics):

        energy_kwh = metrics.get("energy_kwh", 0)

        return {
            "carbon_g": energy_kwh * self.ci
        }
