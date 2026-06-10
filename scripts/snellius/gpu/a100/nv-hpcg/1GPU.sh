#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpcg_1gpu
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --time=0:30:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

module load 2025
module load CUDA/12.8.0


# Answer the question: realistic GPU HPC scaling?

RUNS=3


echo "Warmup"
sustainabench run benchmark -w nvidia-hpcg -m none -b mpi -np $SLURM_NTASKS -c configs/nv-hpcg.yaml -s -nof
echo "Running Nvidia HPCG experiments"
sustainabench run benchmark -w nvidia-hpcg -m time -m perf-energy -m cpu-energy -m gpu-nv -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpcg.yaml -s
