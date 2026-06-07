#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_gpu-burn
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus=1
#SBATCH --constraint=A6000
#SBATCH --time=00:30:00

RUNS=5

module load cuda12.6/toolkit/12.6

echo "Warmup"
sustainabench run benchmark -w gpu-burn -m none -c configs/gpu-burn.yaml -s
echo "Running gpu-burn experiments"
sustainabench run benchmark -w gpu-burn -m time -m likwid=configs/likwid.yaml -m gpu-nv -r $RUNS -c configs/gpu-burn.yaml -s
