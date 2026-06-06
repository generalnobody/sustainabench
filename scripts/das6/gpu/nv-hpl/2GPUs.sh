#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpl_2gpus
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --constraint=A4000
#SBATCH --time=01:30:00

RUNS=5

echo "Running Nvidia HPL experiments (2 GPUs)"
sustainabench run benchmark -w nvidia-hpl -m time -m likwid=configs/likwid.yaml -m gpu-nvidia -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/2GPUs/config.yaml -s
