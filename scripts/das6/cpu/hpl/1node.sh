#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpl-1node
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --constraint=cpunode
#SBATCH --time=01:00:00

RUNS=5

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPL experiments (1 node)"
sustainabench run benchmark -w hpl -m time -m likwid=configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpl/1node/config.yaml -s
