#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_gpu-burn
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus=1
#SBATCH --constraint=A4000
#SBATCH --time=00:30:00

RUNS=5

echo "Warmup"
/home/ibd350/gpu-burn/gpu_burn 60
echo "Running gpu-burn experiments"
sustainabench run benchmark -w gpu-burn -m time -m likwid=configs/likwid.yaml -m gpu-nv -r $RUNS -c configs/gpu-burn.yaml -s
