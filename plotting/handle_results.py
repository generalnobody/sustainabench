from sustainabench.schemas.results.benchmark import BenchmarkResult
from pathlib import Path
import jmespath
import pandas as pd

def load_results(files: dict[str, dict[str, str]]) -> dict[str, dict[str, BenchmarkResult]]:
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

def extract_memory_df(results: dict[str, dict[str, BenchmarkResult]], arch):
    rows = []

    for benchmark, configs in results.items():
        for config, result in configs.items():

            run = result.results["run0"]  # list[NodeResult]

            memory_nodes = []

            for node in run:
                metrics = node.metrics

                if "nodemem" not in metrics and "memory" not in metrics:
                    continue

                if node.node_id == "local":
                    physical_node = "local"
                else:
                    physical_node = node.node_id.split(":")[0]

                if physical_node not in memory_nodes:
                    memory_nodes.append(physical_node)

            node_map = {
                physical_node: f"node{idx}"
                for idx, physical_node in enumerate(memory_nodes)
            }

            for node in run:

                metrics = node.metrics

                if "nodemem" in metrics:
                    rss = metrics["nodemem"]["rss"]["mb"]
                elif "memory" in metrics:
                    rss = metrics["memory"]["rss"]["mb"]
                else:
                    continue

                if node.node_id == "local":
                    physical_node = "local"
                else:
                    physical_node = node.node_id.split(":")[0]

                rows.append(
                    {
                        "arch": arch,
                        "benchmark": benchmark,
                        "config": config,
                        "node": node_map[physical_node],
                        "mean": rss["avg"],
                    }
                )

    return pd.DataFrame(rows)

# def extract_gpu_memory_df(results: dict, arch: str):
#     rows = []

#     for benchmark, configs in results.items():
#         for config, result in configs.items():

#             run = result.results["run0"]

#             for node in run:
#                 node_id = node.node_id

#                 # same physical node logic as CPU version
#                 if node_id == "local":
#                     physical_node = "local"
#                 else:
#                     physical_node = node_id.split(":")[0]

#                 metrics = node.metrics

#                 if "gpu_nv" not in metrics:
#                     continue

#                 gpu_list = metrics["gpu_nv"]

#                 for gpu in gpu_list:
#                     gpu_id = gpu["gpu_id"]
#                     mem = gpu.get("memory", {}).get("mb", None)

#                     if mem is None:
#                         continue

#                     rows.append({
#                         "arch": arch,
#                         "benchmark": benchmark,
#                         "config": config,
#                         "node": physical_node,
#                         "gpu": f"gpu{gpu_id}",
#                         "mean": mem["avg"],
#                     })

#     return pd.DataFrame(rows)

def extract_gpu_memory_df(results: dict, arch: str):
    rows = []

    for benchmark, configs in results.items():
        for config, result in configs.items():

            run = result.results["run0"]

            # Same node numbering logic, but only based on gpu_nv
            entries_with_gpu = [
                entry for entry in run
                if entry.metrics.get("gpu_nv")
            ]

            node_ids = [entry.node_id for entry in entries_with_gpu]
            unique_nodes = list(dict.fromkeys(node_ids))

            node_map = {
                node_id: idx
                for idx, node_id in enumerate(unique_nodes)
            }

            for node in run:

                if node.node_id not in node_map:
                    continue

                node_idx = node_map[node.node_id]
                gpu_list = node.metrics["gpu_nv"]

                for gpu in gpu_list:
                    mem = gpu.get("memory", {}).get("mb", None)

                    if mem is None:
                        continue

                    rows.append({
                        "arch": arch,
                        "benchmark": benchmark,
                        "config": config,
                        "node": node_idx,
                        "gpu": f"gpu{gpu['gpu_id']}_{node_idx}",
                        "mean": mem["avg"],
                    })

    return pd.DataFrame(rows)

def get_results(results, metrics_dict, metrics_to_extract=None):

    metric_sources = {}

    for unitdef in metrics_dict.metrics_dict:
        if (
            metrics_to_extract is not None
            and unitdef.unit not in metrics_to_extract
        ):
            continue

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
#         if unitdef.unit == "node-energy":
#             energy_sources = unitdef.sources
#             break

#     if not energy_sources:
#         raise ValueError("Provided metrics dictionary does not contain sources for paths leading to node-energy data.")
    
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