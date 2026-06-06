#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpl_1node
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=96
#SBATCH --partition=genoa
#SBATCH --time=1:30:00
#SBATCH --exclusive

# Answer the question: How does compute-heavy HPC scale?
# This script: run with 1 node.
# Number of repetitions: 3. Low variability.
# For N: N was chosen to achieve a sustained compute-intensive workload of approximately X minutes.

module load 2025
module load likwid/5.5.0-GCC-14.3.0
module load HPL/2.3-foss-2025b

RUNS=3


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPL experiments (1 node)"
sustainabench run benchmark -w hpl -m time -m likwid=configs/likwid.yaml -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpl/1node/config.yaml -s
