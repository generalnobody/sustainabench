#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_hpl_4nodes
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=96
#SBATCH --partition=genoa
#SBATCH --time=1:00:00
#SBATCH --exclusive

# Answer the question: How does compute-heavy HPC scale?
# This script: run with 4 nodes.
# Number of repetitions: 3. Low variability.
# For N: N was chosen to achieve a sustained compute-intensive workload of approximately X minutes.

module load 2023
module load pypmt/1.2.0-gfbf-2023a
module load HPL/2.3-foss-2023a

RUNS=3


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

echo "Running HPL experiments (4 nodes)"
sustainabench run benchmark -w hpl -m time -m rapl-pypmt -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/hpl/4nodes/config.yaml -s
