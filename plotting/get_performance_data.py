import pandas as pd
from handle_results import load_results
from stats import compute_statistics
from pathlib import Path

OUTPUT_DIR = Path("experiments/plots/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

rome_files = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/hpcg_4nodes.json",
    },
}

genoa_files = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpcg_4nodes.json",
    },
}

a100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/vllm_4gpus.json",
    }
}

h100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/vllm_4gpus.json",
    }
}

rome_files_FR = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/FR/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/FR/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/FR/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/FR/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/FR/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/FR/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/FR/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/FR/hpcg_4nodes.json",
    },
}

genoa_files_FR = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/FR/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/FR/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/FR/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/FR/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/FR/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/FR/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/FR/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/FR/hpcg_4nodes.json",
    },
}

a100_files_FR = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/FR/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/FR/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/FR/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/FR/vllm_4gpus.json",
    }
}

h100_files_FR = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/FR/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/FR/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/FR/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/FR/vllm_4gpus.json",
    }
}

rome_files_2022 = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2022/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2022/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2022/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/2022/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/2022/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2022/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/2022/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/2022/hpcg_4nodes.json",
    },
}

genoa_files_2022 = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2022/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2022/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2022/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/2022/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/2022/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2022/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/2022/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/2022/hpcg_4nodes.json",
    },
}

a100_files_2022 = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/2022/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/2022/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/2022/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2022/vllm_4gpus.json",
    }
}

h100_files_2022 = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/2022/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/2022/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/2022/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2022/vllm_4gpus.json",
    }
}

rome_results = load_results(rome_files)
genoa_results = load_results(genoa_files)
a100_results = load_results(a100_files)
h100_results = load_results(h100_files)

rome_results_FR = load_results(rome_files_FR)
genoa_results_FR = load_results(genoa_files_FR)
a100_results_FR = load_results(a100_files_FR)
h100_results_FR = load_results(h100_files_FR)

rome_results_2022 = load_results(rome_files_2022)
genoa_results_2022 = load_results(genoa_files_2022)
a100_results_2022 = load_results(a100_files_2022)
h100_results_2022 = load_results(h100_files_2022)


import pandas as pd


def extract_performance_per_carbon_df(results_dict):
    rows = []

    for arch, arch_results in results_dict.items():

        for benchmark_name, configs in arch_results.items():

            for config_name, result in configs.items():

                for run_name, nodes in result.results.items():

                    ppc = None

                    for node in nodes:
                        ppc = node.metrics.get("performance_per_carbon")

                        if ppc is not None:
                            break

                    if ppc is None:
                        continue

                    for benchmark, metrics in ppc.items():
                        for key, value in metrics.items():

                            # rows.append(
                            #     {
                            #         "arch": arch,
                            #         "metric": key,
                            #         "benchmark": benchmark,
                            #         "config": config_name,
                            #         "run": run_name,
                            #         "value": value,
                            #     }
                            # )

                            # performance-per-carbon metric
                            if key.startswith("(") and key.endswith(")/g"):
                                rows.append(
                                    {
                                        "arch": arch,
                                        "type": "performance-per-carbon",
                                        "metric": key,
                                        "benchmark": benchmark,
                                        "config": config_name,
                                        "run": run_name,
                                        "value": value,
                                    }
                                )

                            # raw performance metric
                            else:

                                rows.append(
                                    {
                                        "arch": arch,
                                        "type": "performance",
                                        "metric": key,
                                        "benchmark": benchmark,
                                        "config": config_name,
                                        "run": run_name,
                                        "value": value,
                                    }
                                )

    return pd.DataFrame(rows)

all_results = {
    "rome": rome_results,
    "genoa": genoa_results,
    "a100": a100_results,
    "h100": h100_results,
}

all_results_FR = {
    "rome": rome_results_FR,
    "genoa": genoa_results_FR,
    "a100": a100_results_FR,
    "h100": h100_results_FR,
}

all_results_2022 = {
    "rome": rome_results_2022,
    "genoa": genoa_results_2022,
    "a100": a100_results_2022,
    "h100": h100_results_2022,
}

df_ppc = extract_performance_per_carbon_df(all_results)
summary_ppc = compute_statistics(df_ppc)
summary_ppc.to_csv(
    OUTPUT_DIR / "performance_per_carbon.csv",
    index=False
)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}/performance_per_carbon.csv")

df_ppc_FR = extract_performance_per_carbon_df(all_results_FR)
summary_ppc_FR = compute_statistics(df_ppc_FR)
summary_ppc_FR.to_csv(
    OUTPUT_DIR / "FR" / "performance_per_carbon.csv",
    index=False
)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}/FR/performance_per_carbon.csv")

df_ppc_2022 = extract_performance_per_carbon_df(all_results_2022)
summary_ppc_2022 = compute_statistics(df_ppc_2022)
summary_ppc_2022.to_csv(
    OUTPUT_DIR / "2022" / "performance_per_carbon.csv",
    index=False
)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}/2022/performance_per_carbon.csv")