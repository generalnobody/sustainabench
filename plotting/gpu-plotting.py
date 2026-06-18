from pathlib import Path
from sustainabench.schemas.results.metrics_dict import MetricsDict
import yaml
import pandas as pd
from stats import compute_statistics
from plot import build_dataframe, plot_structure
from handle_results import load_results, get_results

OUTPUT_DIR = Path("experiments/plots/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(Path("configs/metrics/metrics_dict.yaml")) as f:
    raw_metrics_dict = yaml.safe_load(f)
metrics_dict = MetricsDict.model_validate(raw_metrics_dict)

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


a100_results = load_results(a100_files)
h100_results = load_results(h100_files)

a100_total_carbon, a100_total_energy = get_results(a100_results, metrics_dict)
h100_total_carbon, h100_total_energy = get_results(h100_results, metrics_dict)

# ----------------------------
# BUILD DATASETS
# ----------------------------
a100_df = build_dataframe(a100_total_carbon, a100_total_energy, "a100")
h100_df = build_dataframe(h100_total_carbon, h100_total_energy, "h100")

df = pd.concat([a100_df, h100_df], ignore_index=True)


# ----------------------------
# CALCULATE STATS & ENERATE PLOTS
# ----------------------------

stats_df = compute_statistics(df)

stats_df.to_csv(
    OUTPUT_DIR / "gpu_benchmark_statistics.csv",
    index=False
)

# print(stats_df)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}.gpu_benchmark_statistics.csv")

config_order = ["1 GPU", "2 GPUs", "4 GPUs"]
plot_structure(stats_df, "a100", OUTPUT_DIR, config_order=config_order)
plot_structure(stats_df, "h100", OUTPUT_DIR, config_order=config_order)

print(f"Plots saved to: {OUTPUT_DIR.resolve()}")
