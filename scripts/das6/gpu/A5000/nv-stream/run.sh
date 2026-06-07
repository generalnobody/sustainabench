#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-stream
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus=1
#SBATCH --constraint=A5000
#SBATCH --time=00:30:00

RUNS=5

module load cuda12.6/toolkit/12.6

echo "Warmup"
sustainabench run benchmark -w nvidia-stream -m none -c configs/nv-stream.yaml -s -nof
echo "Running Nvidia STREAM experiments"
sustainabench run benchmark -w nvidia-stream -m time -m likwid=configs/likwid.yaml -m gpu-nv -r $RUNS -c configs/nv-stream.yaml -s
