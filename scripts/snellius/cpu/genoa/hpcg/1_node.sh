#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpcg_1node
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=96
#SBATCH --partition=genoa
#SBATCH --time=1:00:00
#SBATCH --exclusive
#SBATCH --constraint=hwperf

# Current config supposes Rome CPU's with 2 sockets per node, hence 2 MPI ranks per node. Better for HPCG. 

# Answer the question: How does realistic HPC scale?
# This script: Run on 1 node.

module load 2023
module load pypmt/1.2.0-gfbf-2023a
module load HPCG/3.1-foss-2023a

RUNS=3


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPCG experiments (1 node)"
sustainabench run benchmark -w hpcg -m time -m perf-energy -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpcg/config.yaml -s

