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
module load CUDA/12.9.1


# Answer the question: GPU HPC scaling?
# Number of repetitions: 3. Low variability.

RUNS=3


echo "Warmup"
mpirun -np $SLURM_NTASKS /home/ibiemond/nvidia_hpc_benchmarks/cuda12/hpl.sh --dat /home/ibiemond/sustainabench/scripts/snellius/gpu/a100/configs/nv-hpl/1GPU/HPL-1GPU.dat
echo "Running Nvidia HPL experiments (1 GPU)"
sustainabench run benchmark -w nvidia-hpl -m time -m perf-energy -m cpu-energy -m gpu-nv -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/1GPU/default.yaml -s
