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

rome_files_PL = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/PL/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/PL/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/PL/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/PL/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/PL/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/PL/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/PL/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/PL/hpcg_4nodes.json",
    },
}

genoa_files_PL = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/PL/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/PL/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/PL/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/PL/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/PL/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/PL/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/PL/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/PL/hpcg_4nodes.json",
    },
}

a100_files_PL = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/PL/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/PL/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/PL/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/PL/vllm_4gpus.json",
    }
}

h100_files_PL = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/PL/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/PL/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/PL/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/PL/vllm_4gpus.json",
    }
}

rome_files_2023 = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2023/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2023/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2023/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/2023/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/2023/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/2023/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/2023/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/2023/hpcg_4nodes.json",
    },
}

genoa_files_2023 = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2023/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2023/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2023/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/2023/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/2023/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/2023/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/2023/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/2023/hpcg_4nodes.json",
    },
}

a100_files_2023 = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/2023/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/2023/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/results/2023/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/results/2023/vllm_4gpus.json",
    }
}

h100_files_2023 = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/2023/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/2023/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/results/2023/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/results/2023/vllm_4gpus.json",
    }
}

rome_results = load_results(rome_files)
genoa_results = load_results(genoa_files)
a100_results = load_results(a100_files)
h100_results = load_results(h100_files)

rome_results_PL = load_results(rome_files_PL)
genoa_results_PL = load_results(genoa_files_PL)
a100_results_PL = load_results(a100_files_PL)
h100_results_PL = load_results(h100_files_PL)

rome_results_2023 = load_results(rome_files_2023)
genoa_results_2023 = load_results(genoa_files_2023)
a100_results_2023 = load_results(a100_files_2023)
h100_results_2023 = load_results(h100_files_2023)


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

all_results_PL = {
    "rome": rome_results_PL,
    "genoa": genoa_results_PL,
    "a100": a100_results_PL,
    "h100": h100_results_PL,
}

all_results_2023 = {
    "rome": rome_results_2023,
    "genoa": genoa_results_2023,
    "a100": a100_results_2023,
    "h100": h100_results_2023,
}

df_ppc = extract_performance_per_carbon_df(all_results)
summary_ppc = compute_statistics(df_ppc)
summary_ppc.to_csv(
    OUTPUT_DIR / "performance_per_carbon.csv",
    index=False
)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}/performance_per_carbon.csv")

df_ppc_PL = extract_performance_per_carbon_df(all_results_PL)
summary_ppc_PL = compute_statistics(df_ppc_PL)
summary_ppc_PL.to_csv(
    OUTPUT_DIR / "PL" / "performance_per_carbon.csv",
    index=False
)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}/PL/performance_per_carbon.csv")

df_ppc_2023 = extract_performance_per_carbon_df(all_results_2023)
summary_ppc_2023 = compute_statistics(df_ppc_2023)
summary_ppc_2023.to_csv(
    OUTPUT_DIR / "2023" / "performance_per_carbon.csv",
    index=False
)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}/2023/performance_per_carbon.csv")