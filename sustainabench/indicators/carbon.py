import pandas as pd
from pathlib import Path
import requests
from sustainabench.indicators.base import Indicator, register_indicator
from sustainabench.schemas.configs.indicators.config import IndicatorConfig
from pydantic import BaseModel, model_validator, ConfigDict, field_validator
from typing import Literal

class ReferenceTime(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    mode: Literal["auto", "fixed", "fromto"] = "auto"
    value: pd.Timestamp | None = None
    start: pd.Timestamp | None = None
    end: pd.Timestamp | None = None

    @field_validator("value", "start", "end", mode="before")
    @classmethod
    def parse_timestamp(cls, v):
        if v is None:
            return None
        return pd.to_datetime(v, utc=True)

    @model_validator(mode="after")
    def validate_mode_constraints(self):
        if self.mode == "fromto":
            if self.start is None or self.end is None:
                raise ValueError(
                    "With mode 'fromto' you must specify both start and end"
                )
            if self.start > self.end:
                raise ValueError("start must be <= end")

        elif self.mode == "fixed":
            if self.value is None:
                raise ValueError(
                    "With mode 'fixed' you must specify value"
                )

        return self

class TimeWindow(BaseModel):
    years: int = 0
    months: int = 0
    days: int = 0
    hours: int = 0

    @model_validator(mode="after")
    def apply_years_default(self):
        any_fields_set = any(
            v != 0 for k, v in self.model_dump().items()
        )

        if not any_fields_set:
            self.years = 1

        return self

    @property
    def offset(self) -> pd.DateOffset:
        return pd.DateOffset(**self.model_dump())

class IndicatorValues(BaseModel):
    reference_time: ReferenceTime
    window: TimeWindow
    fallback_country: str | None

@register_indicator
class CarbonIndicator(Indicator):
    name = "carbon"
    require_file = True

    def __init__(self, filename):
        self.parquets = filename # Can be either a .parquet file containing all the traces, or can be a dir containing lots of .parquet traces. 
        # If it is a dir, filenames are used to automatically determine selected .parquet files based on county (and possibly region) code using metadata public IP.

    def setup(self, indicator_config):
        raw_config = indicator_config.indicators.get(self.name) if indicator_config else None
        if raw_config:
            self.config = IndicatorValues.model_validate(raw_config.params)
        else:
            self.config = IndicatorValues(
                reference_time=ReferenceTime(),
                window=TimeWindow(),
                fallback_country=None
        )

    def compute(self, measurements, metadata):
        # Load carbon tracefile
        df = None
        # Auto-region selection logic
        datapath = Path(self.parquets)
        if datapath.is_file():
            df = pd.read_parquet(datapath)
        elif datapath.is_dir():
            public_ip = metadata.get("public_ip")
            if not public_ip and not self.config.fallback_country:
                raise ValueError("Missing 'public_ip' in metadata and no fallback country configured. Either is required for auto-selection of carbon traces.")

            if public_ip:
                response = requests.get(f"http://ip-api.com/json/{public_ip}")
                data = response.json()
                country_code = data.get("countryCode")
                region_code = data.get("region")
            else:
                country_code = self.config.fallback_country
                region_code = ""
            
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
        
        start = end = None
        if self.config.reference_time.mode == "fromto":
            end = self.config.reference_time.end
            start = self.config.reference_time.start
        else:
            if self.config.reference_time.mode == "fixed":
                end = self.config.reference_time.value
            else:
                end =  df["timestamp"].max()
            
            if end is None:
                raise ValueError("How did we get here? Config stuff shouldve been foolproof with pydantic, how did you still manage to get everything this messed up?")
            start = end - self.config.window.offset

        if start is None or end is None:
            raise ValueError("I only added this error to deal with PyLance errors. If you still managed to get it, congrats! You have royally messed something up which should not have been possible. Now, please use the program as intended.")
        filtered = df[
            df["timestamp"].between(start, end)
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
