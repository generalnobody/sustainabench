#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_vllm_1gpu
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --gpus=1
#SBATCH --time=1:00:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

module load 2025
module load CUDA/12.9.1


# Answer the question: AI workload sustainability?

RUNS=3


echo "Warmup"
sustainabench run benchmark -w vllm -m none -c configs/vllm/1GPU.yaml -s -nof
echo "Running VLLM experiments"
sustainabench run benchmark -w vllm -m time -m perf-energy -m cpu-energy -m gpu-nv -r $RUNS -c configs/vllm/1GPU.yaml -s
