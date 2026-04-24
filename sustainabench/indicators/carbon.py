import pandas as pd
from sustainabench.indicators.base import Indicator, register_indicator

@register_indicator
class CarbonIndicator(Indicator):
    name = "carbon"
    require_file = True


    def __init__(self, filename):
        self.filename = filename

    def compute(self, measurements, indicator_config):
        possible_modes = ["auto", "fixed"] # TODO: add fromto mode, where selecting two values is possible to select the dataset between those two timestamps (allows for finer control)
        reference_time_mode = possible_modes[0] # Default is auto
        reference_time_value = ""

        # Default window is 1 year. With default 'auto' mode, uses the most recent available year
        window_years = 1
        window_months = 0
        window_days = 0

        # Config validation and application
        if indicator_config and self.name in indicator_config["indicators"]:
            params = indicator_config["indicators"][self.name]["params"]
            if "reference_time" in params:
                if "mode" in params["reference_time"]:
                    if params["reference_time"]["mode"] not in possible_modes:
                        raise ValueError(f"Unknown reference time mode detected. Mode '{indicator_config['indicators'][self.name]['params']['reference_time']['mode']} does not exist. Please select from these modes: {possible_modes}'")
                    reference_time_mode = params["reference_time"]["mode"]
                    if reference_time_mode == "fixed":
                        if "value" not in params["reference_time"]:
                            raise ValueError("Please make sure to select a reference time value when selecting fixed mode.")
                        reference_time_value = params["reference_time"]["value"]
            if "window" in params:
                years = months = days = 0
                if "years" in params:
                    years = params["years"]
                if "months" in params:
                    months = params["months"]
                if "days" in params:
                    days = params["days"]
                if years == months == days == 0:
                    raise ValueError("An all-zero window is unsupported. Please make sure to select at least 1 for either yearsa, months or days")
                window_years = years; window_months = 0; window_days = 0
        
        # Load parquet trace and check if selected gap is available, then calculate average intensity over the selected period
        df = pd.read_parquet(self.filename)
        if "timestamp" not in df.columns:
            raise ValueError("Missing 'timestamp' column")
        elif "carbon_intensity" not in df.columns:
            raise ValueError("Missing 'carbon_intensity' column")

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

        if df["timestamp"].notna().sum() == 0:
            raise ValueError("No valid timestamps found")
        
        reference_timestamp = None
        if reference_time_mode == "fixed":
            reference_timestamp = pd.to_datetime(reference_time_value, utc=True)
        else:
            reference_timestamp =  df["timestamp"].max()

        cutoff = reference_timestamp - pd.DateOffset(years=window_years, months=window_months, days=window_days)

        filtered = df[
            (df["timestamp"] > cutoff) &
            (df["timestamp"] <= reference_timestamp)
        ]
        if filtered.empty:
            raise ValueError("With the configured mode, reference time and cutoff window, no data was found in the parquet dataset. Please modify your config to ensure data is present.")
        filtered["carbon_intensity"] = pd.to_numeric(
            filtered["carbon_intensity"], errors="coerce"
        )

        avg_intensity = filtered["carbon_intensity"].mean()

        # Calculate carbon output
        # Load measurement data & check
        results = []
        for node_result in measurements["node_results"]:
            node_ci = {}
            # Calculate, per run, carbon output
            for run in node_result["metrics"]: # 'run' is run's id
                cpu_kwh = 0
                gpu_kwh = []
                if "cpu-energy" in node_result["metrics"][run]:
                    if "energy" in node_result["metrics"][run]["cpu-energy"] and "kwh" in node_result["metrics"][run]["cpu-energy"]["energy"]:
                        cpu_kwh = node_result["metrics"][run]["cpu-energy"]["energy"]["kwh"]
                    else:
                        raise ValueError("Missing key in measurements related to cpu-energy. Please double-check")
                    
                if "gpu-nv" in node_result["metrics"][run]:
                    for gpu_result in node_result["metrics"][run]["gpu-nv"]:
                        if "gpu_id" in gpu_result and "energy" in gpu_result and "kwh" in gpu_result["energy"]:
                            gpu_kwh.append({
                                "gpu_id": gpu_result["gpu_id"],
                                "kwh": gpu_result["energy"]["kwh"]
                            })
                        else:
                            raise ValueError("Missing key in measurement related to gpu-nv. Please double-check")
                        
                # Here, we have cpu's kwh, as well as the kwh of all gpu's
                cpu_carbon = cpu_kwh * avg_intensity
                gpu_carbon = [
                    {
                        "gpu_id": g_kwh["gpu_id"],
                        "carbon_g": g_kwh["kwh"] * avg_intensity
                    }
                    for g_kwh in gpu_kwh
                ]
                total_run_carbon = cpu_carbon + sum(item["carbon_g"] for item in gpu_carbon)

                results.append({
                    f"{run}": {
                        "total_carbon_g": total_run_carbon,
                        "cpu_carbon_g": cpu_carbon,
                        "gpu_carbon": gpu_carbon
                    }
                })


        # Sum kWh, multiply with carbon intensity
        

        return {f"{self.name}": results}
        # energy_kwh = measurements.get("energy_kwh", 0)

        # return {
        #     "carbon_g": energy_kwh * self.ci
        # }
