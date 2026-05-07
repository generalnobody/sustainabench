from typing import Any
from pydantic import BaseModel

class IndicatorConfig(BaseModel):
    params: dict[str, Any] | list[Any]

class Config(BaseModel):
    indicators: dict[str, IndicatorConfig]
