from sustainabench.metrics.base import Metric, register_metric
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

@register_metric
class AllCarbonMetric(Metric):
    name = "energy-to-solution"
    require_file = False
    required_metrics = ["node-energy"]

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

        energy_sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "node-energy":
                energy_sources = unitdef.sources
                break

        if not energy_sources:
            raise ValueError(
                f"Provided metrics dictionary does not contain sources for "
                f"paths leading to energy data."
            )

        all_energy_j = 0
        for source_name, source_def in energy_sources.items():
            for node_res in run_metrics:
                energy_metrics = node_res.metrics.get(source_name)
                if energy_metrics is None:
                    continue

                priority = source_def.priority

                for metric in source_def.metrics:
                    if metric.kind != "scalar":
                        print(
                            f"Metric kind {metric.kind} is currently "
                            f"unsupported by metric {self.name}. Skipping..."
                        )
                        continue

                    resolved = jmespath.search(metric.path, energy_metrics)
                    if resolved is None:
                        continue

                    all_energy_j += float(resolved)

        return {
            self.name: {
                "j": all_energy_j
            }
        }