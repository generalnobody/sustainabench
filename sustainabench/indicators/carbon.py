from sustainabench.indicators.base import (
    Indicator,
    register_indicator,
)

@register_indicator
class CarbonIndicator(Indicator):
    name = "carbon"

    def __init__(self, carbon_intensity=400):
        self.ci = carbon_intensity  # gCO2/kWh

    def compute(self, measurements):

        energy_kwh = measurements.get("energy_kwh", 0)

        return {
            "carbon_g": energy_kwh * self.ci
        }



# @register_indicator
# class RuntimeIndicator(Indicator):
#     name = "runtime"

#     def compute(self, measurements):
#         return {
#             "runtime_seconds": measurements["execution_time"]
#         }