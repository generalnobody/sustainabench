from sustainabench.schemas.configs.base import BaseConfig
from pydantic import ConfigDict, BaseModel

class MeasurementConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    measurement: BaseConfig
