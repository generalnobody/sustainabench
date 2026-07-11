import pandas as pd


def extract_cpu_node_breakdown(results, arch_name):

    rows = []

    for benchmark, configs in results.items():

        for config, benchmark_result in configs.items():

            for run_name, run_data in benchmark_result.results.items():

                cpu_entries = []

                for entry in run_data:

                    cpu_energy = (
                        entry.metrics
                        .get("cpu_energy")
                    )

                    if cpu_energy:
                        cpu_entries.append(entry)

                cpu_entries.sort(
                    key=lambda e: e.metadata.get(
                        "hostname",
                        ""
                    )
                )

                for idx, entry in enumerate(cpu_entries):

                    rows.append({
                        "arch": arch_name,
                        "benchmark": benchmark,
                        "config": config,
                        "run": run_name,
                        "component": f"node{idx}",
                        "value": (
                            entry.metrics
                            ["cpu_energy"]
                            ["energy"]
                            ["j"]
                        )
                    })

    return pd.DataFrame(rows)


def extract_gpu_breakdown(results, arch_name):

    rows = []

    for benchmark, configs in results.items():

        for config, benchmark_result in configs.items():

            for run_name, run_data in benchmark_result.results.items():

                entries_with_metrics = [
                    entry for entry in run_data
                    if (
                        entry.metrics.get("cpu_energy") is not None
                        or entry.metrics.get("gpu_nv")
                    )
                ]

                node_ids = [entry.node_id for entry in entries_with_metrics]
                unique_nodes = list(dict.fromkeys(node_ids))

                node_map = {
                    node_id: idx
                    for idx, node_id in enumerate(unique_nodes)
                }

                for entry in run_data:

                    # Ignore empty MPI ranks
                    if entry.node_id not in node_map:
                        continue

                    metrics = entry.metrics
                    node_idx = node_map[entry.node_id]

                    cpu_energy = metrics.get("cpu_energy")

                    if cpu_energy:
                        rows.append({
                            "arch": arch_name,
                            "benchmark": benchmark,
                            "config": config,
                            "run": run_name,
                            "component": f"cpu_{node_idx}",
                            "value": cpu_energy["energy"]["j"],
                        })

                    for gpu in metrics.get("gpu_nv", []):

                        rows.append({
                            "arch": arch_name,
                            "benchmark": benchmark,
                            "config": config,
                            "run": run_name,
                            "component": f"gpu{gpu['gpu_id']}_{node_idx}",
                            "value": gpu["energy"]["j"],
                        })

    return pd.DataFrame(rows)