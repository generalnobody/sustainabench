#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_stream
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=192
#SBATCH --partition=genoa
#SBATCH --time=0:20:00
#SBATCH --exclusive

# Answer the question: How energy-efficient is memory bandwidth?
# Run single configuration on single node.
# Number of repetitions: 3. Low variability.

module load 2023
module load pypmt/1.2.0-gfbf-2023a

RUNS=3


echo "Running STREAM experiments"
sustainabench run benchmark -w stream -m time -m rapl-pypmt -r $RUNS -c configs/stream.yaml -s
