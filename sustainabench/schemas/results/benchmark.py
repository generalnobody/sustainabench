from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

class NodeResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    node_id: str
    metrics: dict[str, Any]
    metadata: dict[str, Any]

    @field_validator("metrics", mode="before")
    @classmethod
    def normalize_metric_keys(cls, value):

        def normalize(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {
                    re.sub(r"[\s\-]+", "_", str(k)): normalize(v)
                    for k, v in obj.items()
                }

            if isinstance(obj, list):
                return [normalize(v) for v in obj]

            return obj

        return normalize(value)


class BenchmarkResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workload: str
    backend: str
    results: dict[str, list[NodeResult]]
    metadata: dict[str, Any] = Field(default_factory=dict)

    # @field_validator("results")
    # @classmethod
    # def validate_run_keys(cls, value):
    #     for key in value:
    #         if not re.fullmatch(r"run\d+", key):
    #             raise ValueError(f"Invalid run key: {key}")
    #     return value