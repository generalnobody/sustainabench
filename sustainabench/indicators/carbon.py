import pandas as pd
from sustainabench.indicators.base import Indicator, register_indicator

@register_indicator
class CarbonIndicator(Indicator):
    name = "carbon"
    require_file = True


    def __init__(self, filename):
        self.filename = filename

    def compute(self, measurements, indicator_config):
        possible_modes = ["auto", "fixed"]
        reference_time_mode = possible_modes[0]
        reference_time_value = None

        # Default window is 1 year. With default 'auto' mode, uses the most recent available year
        window_years = 1
        window_months = 0
        window_days = 0

        # Config validation and application
        if indicator_config and self.name in indicator_config["indicators"]:
            if "reference_time" in indicator_config["indicators"][self.name]["params"]:
                if "mode" in indicator_config["indicators"][self.name]["params"]["reference_time"]:
                    if indicator_config["indicators"][self.name]["params"]["reference_time"]["mode"] not in possible_modes:
                        raise ValueError(f"Unknown reference time mode detected. Mode '{indicator_config['indicators'][self.name]['params']['reference_time']['mode']} does not exist. Please select from these modes: {possible_modes}'")
                    reference_time_mode = indicator_config["indicators"][self.name]["params"]["reference_time"]["mode"]
                    if reference_time_mode == "fixed":
                        if "value" not in indicator_config["indicators"][self.name]["params"]["reference_time"]:
                            raise ValueError("Please make sure to select a reference time value when selecting fixed mode.")
                        reference_time_value = indicator_config["indicators"][self.name]["params"]["reference_time"]["value"]
            if "window" in indicator_config["indicators"][self.name]["params"]:
                years = months = days = 0
                if "years" in indicator_config["indicators"][self.name]["params"]:
                    years = indicator_config["indicators"][self.name]["params"]["years"]
                if "months" in indicator_config["indicators"][self.name]["params"]:
                    months = indicator_config["indicators"][self.name]["params"]["months"]
                if "days" in indicator_config["indicators"][self.name]["params"]:
                    days = indicator_config["indicators"][self.name]["params"]["days"]
                if years == months == days == 0:
                    raise ValueError("An all-zero window is unsupported. Please make sure to select at least 1 for either yearsa, months or days")
                window_years = years; window_months = 0; window_days = 0
        
        # Load parquet trace and check if selected gap is available

        # Calculate carbon output

        return {}
        # energy_kwh = measurements.get("energy_kwh", 0)

        # return {
        #     "carbon_g": energy_kwh * self.ci
        # }
