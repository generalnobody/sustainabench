#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpl-1node
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --cpus-per-task=1
#SBATCH --constraint=cpunode
#SBATCH --time=01:30:00

RUNS=5

echo "Running HPL experiments (1 node)"
sustainabench run benchmark -w hpl -m time -m likwid=configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpl/1node/config.yaml -s
