#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-stream
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --gpus=1
#SBATCH --time=0:20:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

module load 2025
module load CUDA/12.9.1


# Answer the question: How is GPU memory bandwidth efficiency?
# No scaling. Run on a full node, running on a single GPU.
# Number of repetitions: 3. Low variability.

RUNS=3


echo "Warmup"
/home/ibiemond/nvidia_hpc_benchmarks/cuda12/stream-gpu-test.sh --n 268435456
echo "Running Nvidia STREAM experiments"
sustainabench run benchmark -w nvidia-stream -m time -m perf-energy -m cpu-energy -m gpu-nv -r $RUNS -c configs/nv-stream.yaml -s
