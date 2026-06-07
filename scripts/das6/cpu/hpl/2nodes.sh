#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpl-2nodes
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=24
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=2

#SBATCH --time=01:30:00

RUNS=5

echo "Running HPL experiments (2 nodes)"
sustainabench run benchmark -w hpl -m time -m likwid=configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpl/2nodes/config.yaml -s
