from sustainabench.metrics import METRICS
from sustainabench.schemas.results.benchmark import BenchmarkResult, NodeResult
from sustainabench.schemas.configs.metrics import MetricConfig

class ResultProcessor:
    """Class than handles processing raw results"""

    def __init__(self, metric_names, metrics_dict):
        metric_dict = {}
        for name in metric_names:
            file = ""
            if "=" in name:
                name, file = name.split("=", 1)
            if name not in METRICS:
                raise ValueError(f"Unknown metric: {name}")
            metric_dict[name] = file

        self.metrics = [
            METRICS[name](file, metrics_dict)
            for name, file in metric_dict.items()
        ]

        for metric in self.metrics: # Check if all metrics got their required files
            if metric.require_file and metric_dict[metric.name] == "":
                raise ValueError(f"File not provided for metric '{metric.name}'. Use as follows: -i {metric.name}=<file>.")
            
    def get_loaded_metrics(self):
        return [
            metric.name
            for metric in self.metrics
        ]

    def process(self, raw_results: BenchmarkResult, metric_cfg: MetricConfig | None) -> BenchmarkResult:
        results: dict[str, list[NodeResult]] = {}

        for metric in self.metrics: # Setup all metrics. Prevents needing to re-config for every node for every run
            metric.setup(metric_cfg)
            
        for run, node_results in raw_results.results.items():
            run_results = []
            for node_result in node_results:
                node_metrics = {}
                for metric in self.metrics:
                    node_metrics.update(metric.compute(node_result.node_id, node_result.metrics, node_result.metadata))
                run_results.append(NodeResult(node_id=node_result.node_id, metrics=node_metrics, metadata=node_result.metadata))
            results.update({run: run_results})

        return BenchmarkResult(
            workload=raw_results.workload, 
            backend=raw_results.backend, 
            results=results, 
            metadata=raw_results.metadata
        )


