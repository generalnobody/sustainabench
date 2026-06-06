#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_gpu-burn
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --gpus=1
#SBATCH --time=1:00:00
#SBATCH --exclusive

module load 2025
module load CUDA/12.8.0
module load likwid/5.4.1-GCC-14.2.0

# Answer the question: How energy-efficient is raw GPU computation?
# No scaling. Run on a full node, running on a single GPU.
# Number of repetitions: 3. Low variability.

RUNS=3


echo "Warming GPU up"
/home/ibiemond/gpu-burn/gpu_burn 60
echo "Running gpu-burn experiments"
sustainabench run benchmark -w gpu-burn -m time -m likwid=configs/likwid.yaml -m gpu-nv -r $RUNS -c configs/gpu-burn.yaml -s
