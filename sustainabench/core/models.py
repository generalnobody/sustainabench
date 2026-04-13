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
    node_results: list[NodeResult]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload": self.workload,
            "node_results": [asdict(node) for node in self.node_results],
            "metadata": self.metadata
        }
