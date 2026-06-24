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

                for entry in run_data:

                    metrics = entry.metrics

                    cpu_energy = metrics.get(
                        "cpu_energy"
                    )

                    if cpu_energy:

                        rows.append({
                            "arch": arch_name,
                            "benchmark": benchmark,
                            "config": config,
                            "run": run_name,
                            "component": "cpu",
                            "value": (
                                cpu_energy
                                ["energy"]
                                ["j"]
                            )
                        })

                    for gpu in metrics.get(
                        "gpu_nv",
                        []
                    ):

                        rows.append({
                            "arch": arch_name,
                            "benchmark": benchmark,
                            "config": config,
                            "run": run_name,
                            "component": (
                                f"gpu{gpu['gpu_id']}"
                            ),
                            "value": (
                                gpu["energy"]["j"]
                            )
                        })

    return pd.DataFrame(rows)