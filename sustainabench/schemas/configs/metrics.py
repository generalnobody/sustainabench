from typing import Any
from pydantic import BaseModel, ValidationInfo, field_validator

class MetricParams(BaseModel):
    params: dict[str, Any] | list[Any]

class MetricConfig(BaseModel):
    metrics: dict[str, MetricParams]

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, v, info: ValidationInfo):
        context = info.context or {}
        allowed = context.get("allowed_metrics", [])

        unknown = [k for k in v if k not in allowed]

        if unknown:
            raise ValueError(
                f"Unknown metric(s): {', '.join(sorted(unknown))}"
            )

        return v
