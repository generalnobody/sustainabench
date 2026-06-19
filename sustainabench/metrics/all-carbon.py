from sustainabench.metrics.base import Metric, register_metric
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

@register_metric
class AllCarbonMetric(Metric):
    name = "all-carbon"
    require_file = False
    required_metrics = ["carbon"]

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

        carbon_sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "carbon":
                carbon_sources = unitdef.sources
                break
        
        if not carbon_sources:
            raise ValueError(f"Provided metrics dictionary does not contain sources for paths leading to carbon data. Please provide this, otherwise no {self.name} output can be calculated.")
    

        contribution_groups = {}
        for source_name, source_def in carbon_sources.items():
            for node_res in run_metrics:
                carbon_metrics = node_res.metrics.get(source_name)
                if carbon_metrics is None:
                    continue
                
                priority = source_def.priority

                for metric in source_def.metrics:
                    if metric.kind == "scalar":
                        resolved = jmespath.search(metric.path, carbon_metrics)
                        if resolved is None:
                            continue

                        carbon_value = float(resolved)

                        contribution_value = carbon_value

                    else:
                        print(f"Metric kind {metric.kind} is currently unsupported by metric {self.name}. Skipping...")
                        continue

                    
                    if (
                        metric.contributes_to_total and
                        metric.contribution_group
                    ):
                        
                        group = metric.contribution_group
                        existing = contribution_groups.get(group)

                        if existing is None:
                            contribution_groups[group] = {
                                "priority": priority,
                                "value": contribution_value
                            }

                        else:
                            existing_priority = existing["priority"]
                            if priority == existing_priority:
                                existing["value"] += contribution_value
                            elif priority > existing_priority:
                                contribution_groups[group] = {
                                    "priority": priority,
                                    "value": contribution_value
                                }

        all_node_total_g = sum(
            group_data["value"]
            for group_data in contribution_groups.values()
        )

        return {
            self.name: {
                "g": all_node_total_g
            }
        }
