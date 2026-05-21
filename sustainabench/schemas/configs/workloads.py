from sustainabench.schemas.configs.base import BaseConfig
from pydantic import ConfigDict, BaseModel

class WorkloadConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workload: BaseConfig
