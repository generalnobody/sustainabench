from typing import Literal, Union, Annotated
from pydantic import BaseModel, Field

class BaseMetricDefinition(BaseModel):
    contributes_to_total: bool
    contribution_group: str | None

class ScalarMetricDefinition(BaseMetricDefinition):
    kind: Literal["scalar"]
    path: str

class CollectionMetricDefinition(BaseMetricDefinition):
    kind: Literal["collection"]
    collection_path: str
    value_path: str
    label_path: str | None = None

MetricDefinition = Annotated[
    Union[
        ScalarMetricDefinition,
        CollectionMetricDefinition
    ],
    Field(discriminator="kind")
]

class SourceDefinition(BaseModel):
    priority: int
    metrics: list[MetricDefinition]

class UnitDefinition(BaseModel):
    unit: str
    # metrics: dict[str, MetricDefinition]
    sources: dict[str, SourceDefinition]


class MetricsDict(BaseModel):
    metrics_dict: list[UnitDefinition]
