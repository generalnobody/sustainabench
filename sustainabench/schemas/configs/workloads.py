from sustainabench.schemas.configs.base import BaseConfig
from pydantic import ConfigDict, BaseModel

class WorkloadConfig(BaseModel):
    workloads: list[BaseConfig]
