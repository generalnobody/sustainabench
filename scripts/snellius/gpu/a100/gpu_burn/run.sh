#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_gpu-burn
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --gpus=1
#SBATCH --time=1:00:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

module load 2025
module load CUDA/12.9.1


# Answer the question: How energy-efficient is raw GPU computation?
# No scaling. Run on a full node, running on a single GPU.
# Number of repetitions: 3. Low variability.

RUNS=5


echo "Warming GPU up"
/home/ibiemond/gpu-burn/gpu_burn 60
echo "Running gpu-burn experiments"
sustainabench run benchmark -w gpu-burn -m time -m perf-energy -m gpu-nv -r $RUNS -c configs/gpu-burn.yaml -s
