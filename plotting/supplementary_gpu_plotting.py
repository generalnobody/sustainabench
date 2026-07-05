from handle_results import load_results


a100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/supplementary/gpu/a100/experiments/results/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/supplementary/gpu/a100/experiments/results/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/supplementary/gpu/a100/experiments/results/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/a100/experiments/results/vllm_4gpus.json",
    }
}

h100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/supplementary/gpu/h100/experiments/results/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/supplementary/gpu/h100/experiments/results/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/nv-hpcg_4gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/supplementary/gpu/h100/experiments/results/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/supplementary/gpu/h100/experiments/results/vllm_4gpus.json",
    }
}

a100_results = load_results(a100_files)
h100_results = load_results(h100_files)

