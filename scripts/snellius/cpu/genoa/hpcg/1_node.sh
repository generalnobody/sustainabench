#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpcg_1node
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=96
#SBATCH --partition=genoa
#SBATCH --time=1:00:00
#SBATCH --exclusive

# Current config supposes Rome CPU's with 2 sockets per node, hence 2 MPI ranks per node. Better for HPCG. 

# Answer the question: How does realistic HPC scale?
# This script: Run on 1 node.

module load 2025
module load likwid/5.5.0-GCC-14.3.0
module load HPCG/3.1-foss-2025b

RUNS=3


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPCG experiments (1 node)"
sustainabench run benchmark -w hpcg -m time -m likwid=configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpcg/config.yaml -s

