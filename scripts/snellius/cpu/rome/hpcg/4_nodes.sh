#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpcg_4nodes
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=64
#SBATCH --partition=rome
#SBATCH --time=1:00:00
#SBATCH --exclusive

# Current config supposes Rome CPU's with 2 sockets per node, hence 2 MPI ranks per node. Better for HPCG. 

# Answer the question: How does realistic HPC scale?
# This script: Run on 4 nodes.

module load 2025
module load likwid/5.4.1-GCC-14.2.0
module load HPCG/3.1-foss-2025b

RUNS=5
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPCG experiments (4 nodes)"
sustainabench run benchmark -w hpcg -m time -m likwid=$SCRIPT_DIR/../configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c $SCRIPT_DIR/../configs/hpcg/config.yaml -s