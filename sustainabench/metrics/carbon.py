import pandas as pd
from pathlib import Path
import requests
from sustainabench.metrics.base import Metric, register_metric
from pydantic import BaseModel, model_validator, ConfigDict, field_validator
from typing import Literal
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

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

class MetricValues(BaseModel):
    reference_time: ReferenceTime
    window: TimeWindow
    fallback_country: str | None

@register_metric
class CarbonMetric(Metric):
    name = "carbon"
    require_file = True

    def __init__(self, filename, metrics_dict: MetricsDict):
        self.parquets = filename # Can be either a .parquet file containing all the traces, or can be a dir containing lots of .parquet traces. 
        # If it is a dir, filenames are used to automatically determine selected .parquet files based on county (and possibly region) code using metadata public IP.
        self.metrics_dict = metrics_dict
        self.cache = { # Store some data, in this case geolocation data, to not get rate limited by the IP resolve API
            "geolocation": {} # For each public IP, store its region data
        }

    def setup(self, metric_config):
        raw_config = metric_config.metrics.get(self.name) if metric_config else None
        if raw_config:
            self.config = MetricValues.model_validate(raw_config.params)
        else:
            self.config = MetricValues(
                reference_time=ReferenceTime(),
                window=TimeWindow(),
                fallback_country=None
        )

    def compute(self, node_id, measurements, metadata, run_metrics, node_results):
        # Load carbon tracefile
        df = None
        # Auto-region selection logic
        datapath = Path(self.parquets)
        if datapath.is_file():
            df = pd.read_parquet(datapath)
        elif datapath.is_dir():
            public_ip = metadata.get("public_ip")
            if not public_ip and not self.config.fallback_country:
                return {}

            if public_ip:
                cache_store = self.cache["geolocation"].get(public_ip)
                if cache_store:
                    country_code = cache_store["country"]
                    region_code = cache_store["region"]
                else:
                    response = requests.get(f"http://ip-api.com/json/{public_ip}")
                    data = response.json()
                    country_code = data.get("countryCode")
                    region_code = data.get("region")
                    self.cache["geolocation"][public_ip] = {
                        "country": country_code,
                        "region": region_code
                    }
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

        sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "kwh": # Should only be one in there
                sources = unitdef.sources
                break

        if not sources:
            raise ValueError("Provided metrics dictionary does not contain sources for paths leading to kwh data. Please provide this, otherwise no carbon output can be calculated.")

        contribution_groups = {}
        results = {}

        for source_name, source_def in sources.items():
            curr_measurements = measurements.get(source_name)
            if curr_measurements is None: # Measurement source not present
                continue

            priority = source_def.priority

            source_results = results.setdefault(source_name, {})

            for metric in source_def.metrics:
                if metric.kind == "scalar":
                    resolved = jmespath.search(metric.path, curr_measurements)
                    if resolved is None:
                        continue

                    metric_value = float(resolved)
                    carbon_output = metric_value * avg_intensity

                    source_results[metric.path] = {
                        "g": carbon_output
                    }

                    contribution_value = carbon_output

                elif metric.kind == "collection":
                    items = jmespath.search(
                        metric.collection_path,
                        curr_measurements
                    )

                    if items is None:
                        continue

                    values = []

                    for idx, item in enumerate(items):
                        value = jmespath.search(
                            metric.value_path,
                            item
                        )

                        if value is None:
                            continue

                        value = float(value)

                        entry = {}
                        if metric.label_path:
                            entry[metric.label_path] = jmespath.search(metric.label_path, item)
                        entry["g"] = value * avg_intensity
                        values.append(entry)

                    sum_g = sum(v["g"] for v in values)

                    source_results[metric.collection_path] = {
                        "values": values,
                        "sum_g": sum_g
                    }

                    contribution_value = sum_g
                else:
                    continue

                if (
                    metric.contributes_to_total and
                    metric.contribution_group
                ):

                    group = metric.contribution_group

                    existing = contribution_groups.get(group)

                    if existing is None:

                        contribution_groups[group] = {
                            "priority": priority,
                            "value": contribution_value
                        }

                    else:

                        existing_priority = existing["priority"]

                        if priority == existing_priority:

                            existing["value"] += contribution_value

                        elif priority > existing_priority:

                            contribution_groups[group] = {
                                "priority": priority,
                                "value": contribution_value
                            }

        results["total_g"] = sum(
            group_data["value"]
            for group_data in contribution_groups.values()
        )

        return {
            self.name: results
        }
