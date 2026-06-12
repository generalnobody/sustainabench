#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpl_2gpus
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --ntasks-per-node=2
#SBATCH --gpus=2
#SBATCH --gpus-per-task=1
#SBATCH --time=0:30:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

module load 2025
module load CUDA/12.8.0
module load OpenMPI/5.0.7-NVHPC-25.3-CUDA-12.8.0

# Answer the question: GPU HPC scaling?
# Number of repetitions: 3. Low variability.

RUNS=3

export CUDA_VISIBLE_DEVICES=$(echo "$CUDA_VISIBLE_DEVICES" | cut -d, -f1-2)

echo "Warmup"
sustainabench run benchmark -w nvidia-hpl -m none -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/2GPUs/default.yaml -s -nof
echo "Running Nvidia HPL experiments (2 GPUs)"
sustainabench run benchmark -w nvidia-hpl -m time -m perf-energy -m cpu-energy -m gpu-nv -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/2GPUs/default.yaml -s
