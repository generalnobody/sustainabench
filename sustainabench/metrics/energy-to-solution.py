from sustainabench.metrics.base import Metric, register_metric
from sustainabench.schemas.results.metrics_dict import MetricsDict
import jmespath

@register_metric
class EnergyToSolutionMetric(Metric):
    name = "energy-to-solution"
    require_file = False

    def __init__(self, filename, metrics_dict: MetricsDict):
        self.metrics_dict = metrics_dict

    def setup(self, metric_config):
        pass

    def compute(self, node_id, measurements, metadata):
        contribution_groups = {}
        results = {}

        sources = None
        for unitdef in self.metrics_dict.metrics_dict:
            if unitdef.unit == "j": # Should only be one in there
                sources = unitdef.sources
                break

        if not sources:
            raise ValueError("Provided metrics dictionary does not contain sources for paths leading to j data. Please provide this, otherwise no energy-to-solution output can be calculated.")

        for source_name, source_def in sources.items():
            curr_measurements = measurements.get(source_name)
            if curr_measurements is None: # Measurement source not present
                continue

            priority = source_def.priority

            for metric in source_def.metrics:
                if metric.kind == "scalar":
                    resolved = jmespath.search(metric.path, curr_measurements)
                    if resolved is None:
                        continue

                    metric_value = float(resolved)

                    contribution_value = metric_value

                elif metric.kind == "collection":
                    items = jmespath.search(
                        metric.collection_path,
                        curr_measurements
                    )

                    if items is None:
                        continue

                    values = []

                    for idx, item in enumerate(items):
                        value = jmespath.search(
                            metric.value_path,
                            item
                        )

                        if value is None:
                            continue

                        value = float(value)
                        values.append(value)

                    sum_g = sum(values)

                    contribution_value = sum_g
                else:
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

        results["j"] = sum(
            group_data["value"]
            for group_data in contribution_groups.values()
        )

        return {
            self.name: results
        }
