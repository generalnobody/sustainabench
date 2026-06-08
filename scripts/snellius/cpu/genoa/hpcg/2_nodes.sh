#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpcg_2nodes
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=96
#SBATCH --partition=genoa
#SBATCH --time=1:00:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

# Current config supposes Rome CPU's with 2 sockets per node, hence 2 MPI ranks per node. Better for HPCG. 

# Answer the question: How does realistic HPC scale?
# This script: Run on 2 nodes.

module load 2025

module load HPCG/3.1-foss-2025b

RUNS=5


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPCG experiments (2 nodes)"
sustainabench run benchmark -w hpcg -m time -m perf-energy -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpcg/config.yaml -s