#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpcg_1gpu
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-task=1
#SBATCH --time=0:30:00
#SBATCH --exclusive

module load 2025
module load CUDA/12.8.0
module load likwid/5.4.1-GCC-14.2.0

# Answer the question: realistic GPU HPC scaling?

RUNS=3


echo "Warmup"
/home/ibiemond/nvidia_hpc_benchmarks/cuda12/hpcg.sh --nx 640 --ny 640 --nz 640 --rt 300
echo "Running Nvidia HPCG experiments"
sustainabench run benchmark -w nvidia-hpcg -m time -m likwid=configs/likwid.yaml -m gpu-nv -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpcg.yaml -s
