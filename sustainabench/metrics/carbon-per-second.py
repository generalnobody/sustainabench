from sustainabench.metrics.base import Metric, register_metric
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

@register_metric
class CarbonPerSecondMetric(Metric):
    name = "carbon-per-second"
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
            raise ValueError("Provided metrics dictionary does not contain sources for paths leading to performance data. Please provide this, otherwise no carbon-per-second output can be calculated.")
        
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
            raise ValueError("Provided metrics dictionary does not contain sources for paths leading to time data. Please provide this, otherwise no carbon-per-second output can be calculated.")
        
        # execution_time = -1
        # execution_time_priority = -1

        # for source_name, source_def in time_sources.items():
        #     if source_def.priority < execution_time_priority:
        #         continue

        #     for node_res in run_metrics:
        #         time_metrics = node_res.metrics.get(source_name)
        #         if time_metrics is None:
        #             continue

        #         for metric in source_def.metrics:
        #             if metric.kind == "scalar":
        #                 resolved = jmespath.search(metric.path, time_metrics)
        #                 if resolved is None:
        #                     continue

        #                 value = float(resolved)

        #                 if value > execution_time:
        #                     execution_time = value
        #                     execution_time_priority = source_def.priority
        #             else:
        #                 continue # Currently not supporting collections as it not necessary right now

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

        carbon_sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "carbon":
                carbon_sources = unitdef.sources
                break
        
        if not carbon_sources:
            raise ValueError("Provided metrics dictionary does not contain sources for paths leading to carbon data. Please provide this, otherwise no carbon-per-second output can be calculated.")
    

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

        if execution_time is None or execution_time <= 0:
            return {}

        results = {
            "all_nodes_carbon_g": all_node_total_g,
            "max_execution_time_s": execution_time,
            "g_per_second": all_node_total_g / execution_time,
        }

        # Then, once those have been selected, locate the gram metrics, and calculate with them, probably per node, if present
        return {
            self.name: results
        }
