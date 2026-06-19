from sustainabench.metrics.base import Metric, register_metric
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

@register_metric
class CarbonPerSecondMetric(Metric):
    name = "carbon-per-second"
    require_file = False
    required_metrics = ["carbon", "max-execution-time"]

    def __init__(self, filename, metrics_dict: MetricsDict):
        self.metrics_dict = metrics_dict

    def setup(self, metric_config):
        pass

    def compute(self, node_id, measurements, metadata, run_metrics, node_results):
        perf_sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "performance": # Should only be one in there
                perf_sources = unitdef.sources
                break

        if not perf_sources:
            raise ValueError(f"Provided metrics dictionary does not contain sources for paths leading to performance data. Please provide this, otherwise no {self.name} output can be calculated.")
        
        has_performance_data = False

        for source_name, source_def in perf_sources.items():
            perf_measurements = measurements.get(source_name)

            if perf_measurements is None:
                continue

            for metric in source_def.metrics:
                if metric.kind == "scalar":
                    resolved = jmespath.search(metric.path, perf_measurements)

                    if resolved is not None:
                        has_performance_data = True
                        break
                elif metric.kind == "collection":
                    items = jmespath.search(metric.collection_path, perf_measurements)
                    if items is None:
                        continue

                    for idx, item in enumerate(items):
                        value = jmespath.search(metric.value_path, item)
                        if value is not None:
                            has_performance_data = True
                            break
            if has_performance_data:
                break

        if not has_performance_data:
            return {}

        time_sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "max-execution-time":
                time_sources = unitdef.sources
                break

        if not time_sources:
            raise ValueError(f"Provided metrics dictionary does not contain sources for paths leading to time data. Please provide this, otherwise no {self.name} output can be calculated.")
            
        execution_time = None
        for source_name, source_def in time_sources.items():
            for node_res in run_metrics:
                time_metrics = node_res.metrics.get(source_name)
                if time_metrics is None:
                    continue
                
                priority = source_def.priority

                for metric in source_def.metrics:
                    if metric.kind == "scalar":
                        resolved = jmespath.search(metric.path, time_metrics)
                        if resolved is None:
                            continue

                        execution_time = float(resolved)

                    else:
                        print(f"Metric kind {metric.kind} is currently unsupported by metric {self.name}. Skipping...")
                        continue

        if not execution_time:
            raise ValueError(f"No max-execution-time metric found, please ensure it has been computed before computing {self.name}")

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

        # Then, once those have been selected, locate the gram metrics, and calculate with them, probably per node, if present
        return {
            self.name: {
                "g": all_node_total_g / execution_time
            }
        }
