#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_vllm
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus=1
#SBATCH --constraint=A6000
#SBATCH --time=01:00:00

RUNS=5

module load cuda12.6/toolkit/12.6

echo "Warmup"
sustainabench run benchmark -w vllm -m none -c configs/vllm.yaml -s -nof
echo "Running VLLM experiments"
sustainabench run benchmark -w vllm -m time -m likwid=configs/likwid.yaml -m gpu-nv -r $RUNS -c configs/vllm.yaml -s
