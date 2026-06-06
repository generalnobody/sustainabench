#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpcg-4nodes
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --constraint=cpunode
#SBATCH --time=01:30:00

RUNS=5

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPCG experiments (4 nodes)"
sustainabench run benchmark -w hpcg -m time -m likwid=configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpcg/config.yaml -s
