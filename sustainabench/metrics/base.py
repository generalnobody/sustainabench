from abc import ABC, abstractmethod
from typing import Dict, Type
from sustainabench.schemas.configs.metrics import MetricConfig
from sustainabench.schemas.results.metrics_dict import MetricsDict
from sustainabench.schemas.results.benchmark import NodeResult

METRICS: Dict[str, Type["Metric"]] = {}

def register_metric(cls):
    """Macro used by each metric to register in METRICS"""
    METRICS[cls.name] = cls
    return cls


class Metric(ABC):
    """Base Metric class"""
    name: str
    require_file: bool # Control whether this metric should require a file path to be included or not.
    required_metrics: list[str] = [] # Which DERIVED metrics to require. Makes this happen after those are computed (e.g. performance-per-carbon requires carbon).

    @abstractmethod
    def __init__(self, filename: str, metrics_dict: MetricsDict) -> None:
        pass

    @abstractmethod
    def setup(self, metric_config: MetricConfig | None) -> None:
        pass

    @abstractmethod
    def compute(self, node_id: str, measurements: dict, metadata: dict, run_metrics: list[NodeResult], node_results: list[NodeResult]) -> dict:
        pass
