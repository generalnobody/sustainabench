from typing import Any
from pydantic import BaseModel, ValidationInfo, field_validator

class IndicatorParams(BaseModel):
    params: dict[str, Any] | list[Any]

class IndicatorConfig(BaseModel):
    indicators: dict[str, IndicatorParams]

    @field_validator("indicators")
    @classmethod
    def validate_indicators(cls, v, info: ValidationInfo):
        context = info.context or {}
        allowed = context.get("allowed_indicators", [])

        unknown = [k for k in v if k not in allowed]

        if unknown:
            raise ValueError(
                f"Unknown indicator(s): {', '.join(sorted(unknown))}"
            )

        return v
