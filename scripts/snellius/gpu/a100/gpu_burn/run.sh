#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_gpu-burn
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --gpus=1
#SBATCH --time=1:00:00
#SBATCH --exclusive

module load 2023
module load CUDA/12.4.0
module load pypmt/1.2.0-gfbf-2023a

# Answer the question: How energy-efficient is raw GPU computation?
# No scaling. Run on a full node, running on a single GPU.
# Number of repetitions: 3. Low variability.

RUNS=3


echo "Warming GPU up"
/home/ibiemond/gpu-burn/gpu_burn 60
echo "Running gpu-burn experiments"
sustainabench run benchmark -w gpu-burn -m time -m rapl-pypmt -m gpu-nv -r $RUNS -c configs/gpu-burn.yaml -s
