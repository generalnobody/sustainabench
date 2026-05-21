from pydantic import BaseModel

class MetricDefinition(BaseModel):
    paths: list[str]


class UnitDefinition(BaseModel):
    unit: str
    metrics: dict[str, MetricDefinition]


class MetricsDict(BaseModel):
    metrics_dict: list[UnitDefinition]
