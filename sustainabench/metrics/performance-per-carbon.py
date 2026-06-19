from sustainabench.metrics.base import Metric, register_metric
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

@register_metric
class PerformancePerCarbonMetric(Metric):
    name = "performance-per-carbon"
    require_file = False
    required_metrics = ["all-carbon"]

    def __init__(self, filename, metrics_dict: MetricsDict):
        self.metrics_dict = metrics_dict

    def setup(self, metric_config):
        pass

    def compute(self, node_id, measurements, metadata, run_metrics, node_results):
        sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "performance": # Should only be one in there
                sources = unitdef.sources
                break

        if not sources:
            raise ValueError(f"Provided metrics dictionary does not contain sources for paths leading to performance data. Please provide this, otherwise no {self.name} output can be calculated.")

        performance_metrics = {}
        for source_name, source_def in sources.items():
            perf_measurements = measurements.get(source_name)
            if perf_measurements is None:
                continue

            perf_results = performance_metrics.setdefault(source_name, {})

            for metric in source_def.metrics:
                if metric.kind == "scalar":
                    resolved = jmespath.search(metric.path, perf_measurements)
                    if resolved is None:
                        continue

                    perf_value = float(resolved)

                    perf_results[metric.path] = perf_value

                elif metric.kind == "collection":
                    items = jmespath.search(metric.collection_path, perf_measurements)
                    if items is None:
                        continue

                    perf_value = 0
                    for idx, item in enumerate(items):
                        value = jmespath.search(metric.value_path, item)
                        if value is None:
                            continue
                        
                        perf_value += float(value)
                        
                    perf_results[f"{metric.collection_path}.{metric.value_path}"] = perf_value

                else:
                    continue

        if len(performance_metrics) == 0:
            return {}

        all_carbon_sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "all-carbon":
                all_carbon_sources = unitdef.sources
                break
        
        if not all_carbon_sources:
            raise ValueError(f"Provided metrics dictionary does not contain sources for paths leading to carbon data. Please provide this, otherwise no {self.name} output can be calculated.")
    

        all_node_total_g = None
        for source_name, source_def in all_carbon_sources.items():
            for node_res in run_metrics:
                all_carbon_metrics = node_res.metrics.get(source_name)
                if all_carbon_metrics is None:
                    continue
                
                priority = source_def.priority

                for metric in source_def.metrics:
                    if metric.kind == "scalar":
                        resolved = jmespath.search(metric.path, all_carbon_metrics)
                        if resolved is None:
                            continue

                        all_node_total_g = float(resolved)

                    else:
                        print(f"Metric kind {metric.kind} is currently unsupported by metric {self.name}. Skipping...")
                        continue

        if not all_node_total_g:
            raise ValueError(f"No all-carbon metric found, please ensure it has been computed before computing {self.name}")

        results = {
            outer_k: {
                k: v
                for inner_k, inner_v in inner_dict.items()
                for k, v in (
                    (inner_k.replace('"', ''), inner_v), # Show this, mainly for the collection-originated performance metrics
                    (f"({inner_k})/g".replace('"', ''), inner_v / all_node_total_g),
                )
            }
            for outer_k, inner_dict in performance_metrics.items()
        }

        # Then, once those have been selected, locate the gram metrics, and calculate with them, probably per node, if present
        return {
            self.name: results
        }
