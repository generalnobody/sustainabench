from pathlib import Path
from sustainabench.schemas.results.metrics_dict import MetricsDict
import yaml
import pandas as pd
from stats import compute_statistics
from plot import build_dataframe, plot_structure
from handle_results import load_results, get_results
from energy_breakdown import (
    extract_gpu_breakdown
)

from breakdown_stats import (
    compute_breakdown_statistics
)

from breakdown_plot import (
    plot_energy_breakdown_grouped
)

OUTPUT_DIR = Path("experiments/plots/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(Path("configs/metrics/metrics_dict.yaml")) as f:
    raw_metrics_dict = yaml.safe_load(f)
metrics_dict = MetricsDict.model_validate(raw_metrics_dict)

metrics_to_plot = [
    "all-carbon",
    "energy-to-solution",
    "carbon-per-second"
]

a100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/merged/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/merged/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/merged/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/merged/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/vllm_4gpus.json",
    }
}

h100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/merged/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/merged/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/merged/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/merged/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/vllm_4gpus.json",
    }
}

a100_results = load_results(a100_files)
h100_results = load_results(h100_files)



a100_breakdown = extract_gpu_breakdown(
    a100_results,
    "a100"
)

h100_breakdown = extract_gpu_breakdown(
    h100_results,
    "h100"
)

breakdown_df = pd.concat(
    [
        a100_breakdown,
        h100_breakdown
    ],
    ignore_index=True
)

breakdown_stats = (
    compute_breakdown_statistics(
        breakdown_df
    )
)

breakdown_stats.to_csv(
    OUTPUT_DIR /
    "gpu_energy_breakdown.csv",
    index=False
)

plot_energy_breakdown_grouped(
    breakdown_stats,
    "a100",
    OUTPUT_DIR,
    config_order=[
        "1 GPU",
        "2 GPUs",
        "4 GPUs"
    ]
)

plot_energy_breakdown_grouped(
    breakdown_stats,
    "h100",
    OUTPUT_DIR,
    config_order=[
        "1 GPU",
        "2 GPUs",
        "4 GPUs"
    ]
)