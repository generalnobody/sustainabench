from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class BenchmarkResult:
    workload: str
    raw_metrics: Dict[str, Any]
    indicators: Dict[str, Any]
    metadata: Dict[str, Any]
