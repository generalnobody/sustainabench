from sustainabench.schemas.results.benchmark import BenchmarkResult
from pathlib import Path
import jmespath

def load_results(files: dict):
    results = {}

    for key, value in files.items():
        if isinstance(value, dict):
            results[key] = {
                subkey: BenchmarkResult.model_validate_json(Path(path).read_text())
                for subkey, path in value.items()
            }
        else:
            results[key] = BenchmarkResult.model_validate_json(Path(value).read_text())

    return results

def get_results(results, metrics_dict):

    metric_sources = {}

    for unitdef in metrics_dict.metrics_dict:
        metric_sources[unitdef.unit] = unitdef.sources

    full_results = {}

    for metric_name in metric_sources:
        full_results[metric_name] = {}

    for benchmark, benchmark_results in results.items():

        for metric_name in metric_sources:
            full_results[metric_name][benchmark] = {}

        for config, res in benchmark_results.items():

            per_metric_values = {
                metric_name: []
                for metric_name in metric_sources
            }

            for runid, runres in res.results.items():

                run_totals = {
                    metric_name: 0.0
                    for metric_name in metric_sources
                }

                for noderes in runres:

                    for metric_name, sources in metric_sources.items():

                        for source_name, source_def in sources.items():

                            metrics = noderes.metrics.get(source_name)

                            if metrics is None:
                                continue

                            for metric in source_def.metrics:

                                if metric.kind != "scalar":
                                    continue

                                resolved = jmespath.search(
                                    metric.path,
                                    metrics
                                )

                                if resolved is None:
                                    continue

                                run_totals[metric_name] += float(resolved)

                for metric_name, value in run_totals.items():
                    per_metric_values[metric_name].append(value)

            for metric_name in metric_sources:
                full_results[metric_name][benchmark][config] = (
                    per_metric_values[metric_name]
                )

    return full_results

# def get_results(results, metrics_dict):
#     carbon_sources = None
#     for unitdef in metrics_dict.metrics_dict:
#         if unitdef.unit == "carbon":
#             carbon_sources = unitdef.sources
#             break

#     if not carbon_sources:
#         raise ValueError("Provided metrics dictionary does not contain sources for paths leading to carbon data.")

#     energy_sources = None
#     for unitdef in metrics_dict.metrics_dict:
#         if unitdef.unit == "energy-to-solution":
#             energy_sources = unitdef.sources
#             break

#     if not energy_sources:
#         raise ValueError("Provided metrics dictionary does not contain sources for paths leading to energy-to-solution data.")
    
#     carbon_per_second_sources = None

#     for unitdef in metrics_dict.metrics_dict:
#         if unitdef.unit == "carbon-per-second":
#             carbon_per_second_sources = unitdef.sources
#             break

#     if not carbon_per_second_sources:
#         raise ValueError("Provided metrics dictionary does not contain sources for paths leading to carbon-per-second data")
    
#     full_total_carbon = {}
#     full_total_energy = {}
#     full_total_carbon_per_second = {}
#     for t, r in results.items():
#         some_total_carbon = {}
#         some_total_energy = {}
#         some_total_carbon_per_second = {}
#         for title, res in r.items():
#             total_carbon = []
#             total_energy = []
#             total_carbon_per_second = []
#             for runid, runres in res.results.items():
#                 all_node_total_g = 0
#                 all_node_total_j = 0
#                 all_node_total_carbon_per_second = 0
#                 for noderes in runres:
#                     for source_name, source_def in carbon_sources.items():
#                         carbon_metrics = noderes.metrics.get(source_name)
#                         if carbon_metrics is None:
#                             continue

#                         for metric in source_def.metrics:
#                             if metric.kind == "scalar":
#                                 resolved = jmespath.search(metric.path, carbon_metrics)
#                                 if resolved is None:
#                                     continue
#                                 all_node_total_g += float(resolved)
#                             else:
#                                 print(f"Metric kind {metric.kind} is currently unsupported.")
#                                 continue

#                     for source_name, source_def in energy_sources.items():
#                         energy_metrics = noderes.metrics.get(source_name)
#                         if energy_metrics is None:
#                             continue
#                         for metric in source_def.metrics:
#                             if metric.kind == "scalar":
#                                 resolved = jmespath.search(metric.path, energy_metrics)
#                                 if resolved is None:
#                                     continue
#                                 all_node_total_j += float(resolved)
#                             else:
#                                 print(f"Metric kind {metric.kind} is currently unsupported.")
#                                 continue

#                     for source_name, source_def in carbon_per_second_sources.items():
#                         carbon_per_second_metrics = noderes.metrics.get(source_name)
#                         if carbon_per_second_metrics is None:
#                             continue

#                         for metric in source_def.metrics:
#                             if metric.kind == "scalar":
#                                 resolved = jmespath.search(metric.path, carbon_per_second_metrics)
#                                 if resolved is None:
#                                     continue
#                                 all_node_total_carbon_per_second += float(resolved)
#                             else:
#                                 print(f"Metric kind {metric.kind} is currently unsupported.")
#                                 continue
#                 # As everything is for the CPUs, no need to split and analyse between them
#                 total_carbon.append(all_node_total_g)
#                 total_energy.append(all_node_total_j)
#                 total_carbon_per_second.append(all_node_total_carbon_per_second)

#             some_total_carbon.update({title: total_carbon})
#             some_total_energy.update({title: total_energy})
#             some_total_carbon_per_second.update({title: total_carbon_per_second})

#         full_total_carbon.update({t:some_total_carbon})
#         full_total_energy.update({t:some_total_energy})
#         full_total_energy.update({t:some_total_carbon_per_second})

#     return full_total_carbon, full_total_energy, full_total_carbon_per_second