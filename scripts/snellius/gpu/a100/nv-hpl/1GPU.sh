#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpl_1gpu
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

module load 2025
module load CUDA/12.8.0


# Answer the question: GPU HPC scaling?
# Number of repetitions: 3. Low variability.

RUNS=3

export CUDA_VISIBLE_DEVICES=$(echo "$CUDA_VISIBLE_DEVICES" | cut -d, -f1)

echo "Warmup"
sustainabench run benchmark -w nvidia-hpl -m none -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/1GPU/default.yaml -s -nof
echo "Running Nvidia HPL experiments (1 GPU)"
sustainabench run benchmark -w nvidia-hpl -m time -m perf-energy -m cpu-energy -m gpu-nv -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/1GPU/default.yaml -s
