from typing import Any
from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    params: dict[str, Any] | list[Any]
