#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpl_48pus
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=2
#SBATCH --partition=gpu_a100
#SBATCH --ntasks-per-node=4
#SBATCH --gpus=8
#SBATCH --gpus-per-task=1
#SBATCH --time=0:30:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

module load 2025
module load CUDA/12.8.0
module load OpenMPI/5.0.7-NVHPC-25.3-CUDA-12.8.0

# Answer the question: GPU HPC scaling?
# Number of repetitions: 3. Low variability.

RUNS=1


echo "Warmup"
sustainabench run benchmark -w nvidia-hpl -m none -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/8GPUs/default.yaml -s -nof
echo "Running Nvidia HPL experiments  (8 GPUs)"
sustainabench run benchmark -w nvidia-hpl -m time -m perf-energy -m cpu-energy -m gpu-nv -m memory -m network -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/8GPUs/default.yaml -s
