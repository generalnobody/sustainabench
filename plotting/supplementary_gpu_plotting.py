from handle_results import load_results, extract_memory_df, extract_gpu_memory_df
from breakdown_plot import plot_memory_grouped , plot_gpu_memory_grouped
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("experiments/plots/supplementary/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

a100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "1 GPU": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-hpcg_4gpus.json",
        "8 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/nv-hpcg_8gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/supplementary/gpu/a100/experiments/raw/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/raw/vllm_4gpus.json",
    }
}

h100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "1 GPU": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpl_4gpus.json",
        "8 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpl_8gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpcg_4gpus.json",
        "8 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/nv-hpcg_8gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/supplementary/gpu/h100/experiments/raw/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/raw/vllm_4gpus.json",
    }
}

a100_results = load_results(a100_files)
h100_results = load_results(h100_files)

memory_df = pd.concat(
    [
        extract_memory_df(a100_results, "a100"),
        extract_memory_df(h100_results, "h100"),
    ],
    ignore_index=True,
)

memory_df[memory_df["arch"]=="a100"].to_csv(f"{OUTPUT_DIR}/a100_memory.csv", index=False)
memory_df[memory_df["arch"]=="h100"].to_csv(f"{OUTPUT_DIR}/h100_memory.csv", index=False)

config_order = [
    "1 GPU",
    "2 GPUs",
    "4 GPUs",
    "8 GPUs"
]

plot_memory_grouped(
    memory_df,
    arch_name="a100",
    output_dir=OUTPUT_DIR,
    config_order=config_order,
)

plot_memory_grouped(
    memory_df,
    arch_name="h100",
    output_dir=OUTPUT_DIR,
    config_order=config_order,
)


gpu_memory_df = pd.concat(
    [
        extract_gpu_memory_df(a100_results, "a100"),
        extract_gpu_memory_df(h100_results, "h100"),
    ],
    ignore_index=True,
)

gpu_memory_df[gpu_memory_df["arch"]=="a100"].to_csv(f"{OUTPUT_DIR}/a100_gpu_memory.csv", index=False)
gpu_memory_df[gpu_memory_df["arch"]=="h100"].to_csv(f"{OUTPUT_DIR}/h100_gpu_memory.csv", index=False)

plot_gpu_memory_grouped(
    gpu_memory_df,
    arch_name="a100",
    output_dir=OUTPUT_DIR,
    config_order=config_order,
)

plot_gpu_memory_grouped(
    gpu_memory_df,
    arch_name="h100",
    output_dir=OUTPUT_DIR,
    config_order=config_order,
)
print(f"Plots saved to: {OUTPUT_DIR.resolve()}")
