#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_vllm_2gpus
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --gpus=2
#SBATCH --time=1:00:00
#SBATCH --exclusive

module load 2025
module load CUDA/12.8.0
module load likwid/5.4.1-GCC-14.2.0

# Answer the question: AI workload sustainability?

RUNS=3
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Warmup"
vllm --model --num-prompts 500 --input-len 2048 --output-len 256 --max-num-seqs 32 --tensor-parallel-size 2
echo "Running VLLM experiments"
sustainabench run benchmark -w nvidia-hpcg -m time -m likwid=$SCRIPT_DIR/../configs/likwid.yaml -m gpu-nv -r $RUNS -c $SCRIPT_DIR/../configs/vllm/2GPUs.yaml -s
