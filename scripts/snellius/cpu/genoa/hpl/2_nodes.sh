#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpl_2nodes
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=96
#SBATCH --partition=genoa
#SBATCH --time=1:00:00
#SBATCH --exclusive

# Answer the question: How does compute-heavy HPC scale?
# This script: run with 2 nodes.
# Number of repetitions: 3. Low variability.
# For N: N was chosen to achieve a sustained compute-intensive workload of approximately X minutes.

module load 2025
module load likwid/5.4.1-GCC-14.2.0
module load HPL/2.3-foss-2025b

RUNS=3
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPL experiments (2 nodes)"
sustainabench run benchmark -w hpl -m time -m likwid=$SCRIPT_DIR/../configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c $SCRIPT_DIR/../configs/hpl/2nodes/config.yaml -s
