from sustainabench.metrics.base import Metric, register_metric
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

@register_metric
class MaxExecutionTimeMetric(Metric):
    name = "max-execution-time"
    require_file = False

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
            raise ValueError("Provided metrics dictionary does not contain sources for paths leading to performance data. Please provide this, otherwise no max-execution-time output can be calculated.")
        
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
            if unitdef.unit == "time":
                time_sources = unitdef.sources
                break

        if not time_sources:
            raise ValueError(f"Provided metrics dictionary does not contain sources for paths leading to time data. Please provide this, otherwise no {self.name} output can be calculated.")

        execution_time = None
        execution_time_priority = -1

        for source_name, source_def in time_sources.items():
            for node_res in node_results:
                time_metrics = node_res.metrics.get(source_name)
                if time_metrics is None:
                    continue
                for metric in source_def.metrics:
                    if metric.kind != "scalar":
                        continue

                    resolved = jmespath.search(metric.path, time_metrics)
                    if resolved is None:
                        continue

                    value = float(resolved)

                    if (
                        source_def.priority > execution_time_priority
                        or (
                            source_def.priority == execution_time_priority
                            and (
                                execution_time is None
                                or value > execution_time
                            )
                        )
                    ):
                        execution_time = value
                        execution_time_priority = source_def.priority

        if execution_time is None or execution_time <= 0:
            return {}

        return {
            self.name: execution_time
        }
