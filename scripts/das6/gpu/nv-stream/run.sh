#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-stream
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus=1
#SBATCH --constraint=A4000
#SBATCH --time=00:30:00

RUNS=5

echo "Running Nvidia STREAM experiments"
sustainabench run benchmark -w nvidia-stream -m time -m likwid=configs/likwid.yaml -m gpu-nvidia -r $RUNS -c configs/nv-stream.yaml -s
