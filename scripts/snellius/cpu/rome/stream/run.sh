#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_stream
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --partition=rome
#SBATCH --time=0:20:00
#SBATCH --exclusive

# Answer the question: How energy-efficient is memory bandwidth?
# Run single configuration on single node.
# Number of repetitions: 3. Low variability.

module load 2025
module load likwid/5.4.1-GCC-14.2.0

RUNS=3

echo "Running STREAM experiments"
sustainabench run benchmark -w stream -m time -m likwid=configs/likwid.yaml -r $RUNS -c /configs/stream.yaml -s
