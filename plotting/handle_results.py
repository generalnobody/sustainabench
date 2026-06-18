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
    carbon_sources = None
    for unitdef in metrics_dict.metrics_dict:
        if unitdef.unit == "carbon":
            carbon_sources = unitdef.sources
            break

    if not carbon_sources:
        raise ValueError("Provided metrics dictionary does not contain sources for paths leading to carbon data.")

    energy_sources = None
    for unitdef in metrics_dict.metrics_dict:
        if unitdef.unit == "energy-to-solution":
            energy_sources = unitdef.sources
            break

    if not energy_sources:
        raise ValueError("Provided metrics dictionary does not contain sources for paths leading to energy-to-solution data.")
    
    full_total_carbon = {}
    full_total_energy = {}
    for t, r in results.items():
        some_total_carbon = {}
        some_total_energy = {}
        for title, res in r.items():
            total_carbon = []
            total_energy = []
            for runid, runres in res.results.items():
                all_node_total_g = 0
                all_node_total_j = 0
                for noderes in runres:
                    for source_name, source_def in carbon_sources.items():
                        carbon_metrics = noderes.metrics.get(source_name)
                        if carbon_metrics is None:
                            continue

                        for metric in source_def.metrics:
                            if metric.kind == "scalar":
                                resolved = jmespath.search(metric.path, carbon_metrics)
                                if resolved is None:
                                    continue
                                all_node_total_g += float(resolved)
                            else:
                                print(f"Metric kind {metric.kind} is currently unsupported.")
                                continue

                    for source_name, source_def in energy_sources.items():
                        energy_metrics = noderes.metrics.get(source_name)
                        if energy_metrics is None:
                            continue
                        for metric in source_def.metrics:
                            if metric.kind == "scalar":
                                resolved = jmespath.search(metric.path, energy_metrics)
                                if resolved is None:
                                    continue
                                all_node_total_j += float(resolved)
                            else:
                                print(f"Metric kind {metric.kind} is currently unsupported.")
                                continue
                # As everything is for the CPUs, no need to split and analyse between them
                total_carbon.append(all_node_total_g)
                total_energy.append(all_node_total_j)

            some_total_carbon.update({title: total_carbon})
            some_total_energy.update({title: total_energy})

        full_total_carbon.update({t:some_total_carbon})
        full_total_energy.update({t:some_total_energy})

    return full_total_carbon, full_total_energy