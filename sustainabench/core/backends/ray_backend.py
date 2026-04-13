# from typing import Tuple
# from .base import ExecutionBackend, register_backend
# import ray


# @ray.remote
# def _ray_execute(runner):
#     return runner._run_local(num_processors=1)

# @register_backend
# class RayBackend(ExecutionBackend):
#     """Runs benchmark using Ray (used for distributed execution)"""
#     name = "ray"

#     def __init__(self, num_processors: int = 1) -> None:
#         super().__init__(*args, **kwargs)
#         self.num_workers = num_processors
#         ray.init(ignore_reinit_error=True)

#     def run(self, runner):
#         futures = [
#             _ray_execute.remote(runner)
#             for _ in range(self.num_workers)
#         ]

#         results = ray.get(futures)

#         # raws = [r[0] for r in results]

#         # simple aggregation
#         aggregated = {}
#         for k in raws[0]:
#             values = [d.get(k) for d in raws if k in d]
#             if all(isinstance(v, (int, float)) for v in values):
#                 aggregated[k] = sum(values) / len(values)

#         return aggregated_raw

from typing import Any, Dict, List
from .base import ExecutionBackend, register_backend
import ray
from ..models import BenchmarkResult, NodeResult


@ray.remote
def _ray_execute_node(runner):
    """
    Runs a full benchmark on a single node.
    """
    return runner._run_local(num_processors=1)


@register_backend
class RayBackend(ExecutionBackend):
    """Node-aware Ray backend with correct RAPL handling"""
    name = "ray"

    def __init__(self, num_processors: int = 1) -> None:
        self.num_workers = num_processors

        ray.init(ignore_reinit_error=True)

        # Detect nodes
        self.nodes = [n for n in ray.nodes() if n["Alive"]]
        self.num_nodes = len(self.nodes)

    def _get_node_resource_key(self, node: dict) -> str:
        """
        Extract node-specific resource key like 'node:192.168.x.x'
        """
        for key in node["Resources"]:
            if key.startswith("node:"):
                return key
        raise RuntimeError("Node resource key not found")

    def _has_node_scoped_measurement(self, runner) -> bool:
        return any(m.scope == "node" for m in runner.get_measurements())

    def run(self, runner) -> BenchmarkResult:
        has_node_scope = self._has_node_scoped_measurement(runner)

        # Single node + node-scoped measurement (RAPL)
        if self.num_nodes == 1 and has_node_scope:
            print("[WARNING] RAPL detected but only one node available.")
            print("Running a single worker to avoid double counting.")

            result = ray.get(_ray_execute_node.remote(runner))
            node_results = self._format_results([result])
            return BenchmarkResult(runner.get_workload_name(), node_results, {})

        # Multi-node → run one task per node
        futures = []

        for node in self.nodes:
            node_key = self._get_node_resource_key(node)

            futures.append(
                _ray_execute_node.options(
                    resources={node_key: 0.01}
                ).remote(runner)
            )

        results: List[Dict[str, Any]] = ray.get(futures)

        # # Aggregate results
        # return self._aggregate(results)

        node_results = self._format_results(results)
        return BenchmarkResult(runner.get_workload_name(), node_results, {})

    def _format_results(self, raw_results: list) -> list[NodeResult]:
        node_results = []

        for node, node_worker_results in zip(self.nodes, raw_results):
            node_results.append(
                NodeResult(
                    node_id=node["NodeID"],
                    metrics=node_worker_results,
                    metadata={
                        "address": node["NodeManagerAddress"]
                    }
                )
            )

        return node_results

    # def _aggregate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    #     """
    #     Aggregates per-node results safely.
    #     - numeric → average
    #     """

    #     if not results:
    #         return {}

    #     aggregated = {}

    #     keys = results[0].keys()

    #     for k in keys:
    #         values = [r.get(k) for r in results if k in r]

    #         if all(isinstance(v, (int, float)) for v in values):
    #             aggregated[k] = sum(values) / len(values)
    #         else:
    #             aggregated[k] = values  # fallback

    #     return aggregated


