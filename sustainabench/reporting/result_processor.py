from sustainabench.metrics import METRICS
from sustainabench.schemas.results.benchmark import BenchmarkResult, NodeResult
from sustainabench.schemas.configs.metrics import MetricConfig
from graphlib import TopologicalSorter

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

        unsorted_metrics = [
            METRICS[name](file, metrics_dict)
            for name, file in metric_dict.items()
        ]

        metrics_by_name = {metric.name: metric for metric in unsorted_metrics}

        ts = TopologicalSorter() # Perform topological sort of metrics, to ensure required metrics always get computed before the ones that require them
        for metric in unsorted_metrics:
            ts.add(metric.name, *metric.required_metrics)

        ordered_metric_names = list(ts.static_order())
        self.metrics = [metrics_by_name[name] for name in ordered_metric_names]


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
            run_results = [
                NodeResult(
                    node_id=node.node_id,
                    metrics={},
                    metadata=node.metadata,
                )
                for node in node_results
            ]

            for metric in self.metrics:
                for source, result in zip(node_results, run_results):
                    result.metrics.update(
                        NodeResult.normalize_metric_keys(metric.compute(
                            source.node_id,
                            source.metrics,
                            source.metadata,
                            run_results,
                            node_results,
                        ))
                    )

            results.update({run: run_results})

        return BenchmarkResult(
            workload=raw_results.workload, 
            backend=raw_results.backend, 
            results=results, 
            metadata=raw_results.metadata
        )


