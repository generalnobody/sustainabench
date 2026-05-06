from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class NodeResult:
    node_id: str
    # worker_results: list[Dict[str, Any]]
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class BenchmarkResult:
    workload: str
    backend: str # Only included to make processing weird nodes (global) easier when using, for instance, MPI
    results: Dict[str, list[NodeResult]]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)