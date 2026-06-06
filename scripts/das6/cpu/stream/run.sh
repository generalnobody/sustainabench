#!/bin/bash

#SBATCH --job-name=sustainabench_cpu_stream
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --constraint=cpunode
#SBATCH --time=00:30:00

RUNS=5

echo "Running stream experiments"
sustainabench run benchmark -w stream -m time -m likwid=configs/likwid.yaml -r $RUNS -c configs/stream.yaml -s
