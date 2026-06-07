#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpcg_1gpu
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --constraint=A4000
#SBATCH --time=01:30:00

RUNS=5

module load cuda12.6/toolkit/12.6

echo "warmup"
sustainabench run benchmark -w nvidia-hpcg -m none -b mpi -np $SLURM_NTASKS -c configs/nv-hpcg.yaml -s -nof
echo "Running Nvidia HPCG experiments (1 GPU)"
sustainabench run benchmark -w nvidia-hpcg -m time -m likwid=configs/likwid.yaml -m gpu-nv -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpcg.yaml -s
