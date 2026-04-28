import pandas as pd
from pathlib import Path
import requests
from sustainabench.indicators.base import Indicator, register_indicator

@register_indicator
class CarbonIndicator(Indicator):
    name = "carbon"
    require_file = True


    def __init__(self, filename):
        self.parquets = filename # Can be either a .parquet file containing all the traces, or can be a dir containing lots of .parquet traces. 
        # If it is a dir, filenames are used to automatically determine selected .parquet files based on county (and possibly region) code using metadata public IP.

    def setup(self, indicator_config):
        # Load config. Must always be run before compute()
        possible_modes = ["auto", "fixed", "fromto"]
        self.reference_time_mode = possible_modes[0] # Default is auto
        self.reference_time_value = ""
        self.reference_time_from = ""
        self.reference_time_to = ""

        # Default window is 1 year. With default 'auto' mode, uses the most recent available year
        self.window_years = 1
        self.window_months = 0
        self.window_days = 0

        # Config validation and application
        if indicator_config and self.name in indicator_config["indicators"]:
            params = indicator_config["indicators"][self.name]["params"]
            if "reference_time" in params:
                if "mode" in params["reference_time"]:
                    if params["reference_time"]["mode"] not in possible_modes:
                        raise ValueError(f"Unknown reference time mode detected. Mode '{indicator_config['indicators'][self.name]['params']['reference_time']['mode']} does not exist. Please select from these modes: {possible_modes}'")
                    self.reference_time_mode = params["reference_time"]["mode"]
                    if self.reference_time_mode == "fixed":
                        if "value" not in params["reference_time"]:
                            raise ValueError("Please make sure to select a reference time value when selecting fixed mode.")
                        self.reference_time_value = params["reference_time"]["value"]
                    if self.reference_time_mode == "fromto":
                        if "from" not in params["reference_time"]:
                            raise ValueError("Please make sure to select a reference 'from' time value when selecting fromto mode.")
                        elif "to" not in params["reference_time"]:
                            raise ValueError("Please make sure to select a reference 'to' time value when selecting fromto mode.")
                        self.reference_time_from = params["reference_time"]["from"]
                        self.reference_time_to = params["reference_time"]["to"]
            if "window" in params:
                years = months = days = 0
                if "years" in params["window"]:
                    years = params["window"]["years"]
                if "months" in params["window"]:
                    months = params["window"]["months"]
                if "days" in params["window"]:
                    days = params["window"]["days"]
                if years == months == days == 0 and self.reference_time_mode != "fromto":
                    raise ValueError("An all-zero window is unsupported. Please make sure to select at least 1 for either years, months or days")
                self.window_years = years; self.window_months = 0; self.window_days = 0

    def compute(self, measurements, metadata):
        # Load carbon tracefile
        df = None
        # Auto-region selection logic
        datapath = Path(self.parquets)
        if datapath.is_file():
            df = pd.read_parquet(datapath)
        elif datapath.is_dir():
            if "public_ip" not in metadata:
                raise ValueError (f"Key 'public_ip' absent from node's metadata. This is needed as you entered a directory for auto-selection of carbon traces.")
            response = requests.get(f"http://ip-api.com/json/{metadata['public_ip']}")
            data = response.json()
            country_code = data.get("countryCode")
            region_code = data.get("region")
            if not country_code:
                raise ValueError("Could not determine country code from IP lookup.")
            
            files = [p for p in datapath.iterdir() if p.is_file()]
            # First: exact region match
            region_match = [
                p for p in files
                if p.stem.startswith(f"{country_code}-{region_code}_")
            ]
            # Second: country-only fallback
            country_match = [
                p for p in files
                if p.stem.startswith(f"{country_code}_")
            ]
            if region_match:
                print(f"Loading carbon traces for region {region_code} in country {country_code}")
                df = pd.read_parquet(region_match[0])
            elif country_match:
                print(f"Loading carbon traces for country {country_code}")
                df = pd.read_parquet(country_match[0])
            else:
                raise FileNotFoundError(
                    f"No carbon traces found for country '{country_code}' "
                    f"and/or region '{region_code}'."
                )   
        else:
            raise ValueError(f"Tracefile '{self.parquets}' does not exist.")

        # Load parquet trace and check if selected gap is available, then calculate average intensity over the selected period
        if "timestamp" not in df.columns:
            raise ValueError("Missing 'timestamp' column")
        elif "carbon_intensity" not in df.columns:
            raise ValueError("Missing 'carbon_intensity' column")

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

        if df["timestamp"].notna().sum() == 0:
            raise ValueError("No valid timestamps found")
        

        reference_from = reference_to = None
        if self.reference_time_mode == "fromto":
            reference_from = pd.to_datetime(self.reference_time_from, utc=True)
            reference_to = pd.to_datetime(self.reference_time_to, utc=True)

            if reference_from > reference_to:
                raise ValueError("Reference time 'from' must be <= reference time 'to'")
        else:
            if self.reference_time_mode == "fixed":
                reference_to = pd.to_datetime(self.reference_time_value, utc=True)
            else:
                reference_to =  df["timestamp"].max()
            
            reference_from = reference_to - pd.DateOffset(years=self.window_years, months=self.window_months, days=self.window_days)

        filtered = df[
            df["timestamp"].between(reference_from, reference_to)
        ]
        if filtered.empty:
            raise ValueError("With the configured mode, reference time and cutoff window, no data was found in the parquet dataset. Please modify your config to ensure data is present.")
        filtered["carbon_intensity"] = pd.to_numeric(
            filtered["carbon_intensity"], errors="coerce"
        )

        avg_intensity = filtered["carbon_intensity"].mean()

        # Calculate carbon output
        # Load measurement data & check
        results = {}
        cpu_kwh = 0
        cpu_per_domain_kwh = [] # cpu_kwh is already total, so this is just for completeness. Further calculations for total system carbon are done using cpu_kwh and gpu_kwh, this only on itself
        gpu_kwh = []
        if "cpu-energy" in measurements:
            if "energy" in measurements["cpu-energy"] and "kwh" in measurements["cpu-energy"]["energy"]:
                cpu_kwh = measurements["cpu-energy"]["energy"]["kwh"]
            else:
                raise ValueError("Missing key in measurements related to cpu-energy. Please double-check")
            if "per_domain" in measurements["cpu-energy"]: # Not required per se, so if not available, just ignore it, no need for an error
                for domain in measurements["cpu-energy"]["per_domain"]:
                    if "energy" in domain and "kwh" in domain["energy"]:
                        cpu_per_domain_kwh.append(domain["energy"]["kwh"])
                    else:
                        raise ValueError("Missing key in a CPU domain's 'energy' value. Please check")
            
        if "gpu-nv" in measurements:
            for gpu_result in measurements["gpu-nv"]:
                if "gpu_id" in gpu_result and "energy" in gpu_result and "kwh" in gpu_result["energy"]:
                    gpu_kwh.append({
                        "gpu_id": gpu_result["gpu_id"],
                        "kwh": gpu_result["energy"]["kwh"]
                    })
                else:
                    raise ValueError("Missing key in measurement related to gpu-nv. Please double-check")
                
        cpu_carbon = {
            "carbon_g": cpu_kwh * avg_intensity
        }
        if cpu_per_domain_kwh:
            cpu_per_domain_carbon = [
                cpu_domain_kwh * avg_intensity
                for cpu_domain_kwh in cpu_per_domain_kwh
            ]
            cpu_carbon.update({
                "per_domain": [
                    {
                        "carbon_g": g
                    } for g in cpu_per_domain_carbon
                ]
            })
        print(cpu_carbon)
        gpu_carbon = [
            {
                "gpu_id": g_kwh["gpu_id"],
                "carbon_g": g_kwh["kwh"] * avg_intensity
            }
            for g_kwh in gpu_kwh
        ]
        total_run_carbon = cpu_carbon["carbon_g"] + sum(item["carbon_g"] for item in gpu_carbon)
        return {
            self.name: {
                "total_g": total_run_carbon,
                "cpu": cpu_carbon,
                "gpu": gpu_carbon
            }
        }
