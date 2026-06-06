#!/bin/bash

#SBATCH --job-name=sustainabench_cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --constraint=cpunode
#SBATCH --time=01:00:00

RUNS=1 # Limiting to 5 runs to save on runtime budget. Set to 1 for testing
MPI_RANKS=24
DEFAULT_OMP_THREADS=4
MPI_RANKS_WITH_OMP=$(($MPI_RANKS / $DEFAULT_OMP_THREADS))

#####################################################
# Micro
#####################################################

# stress-ng (compute)
# 3 intensity levels:
# - low (25% cores) 
# - medium (50% cores)
# - high (100% cores)
# This aims to show power draw plateau behaviour and efficiency per FLOP, and how energy scales with parallelism
echo "Running stress-ng experiments"
for t in "tiny" "small" "medium" "large"; do
    echo "    stress-ng ($t)"
    sustainabench run benchmark -w stress-ng -m time -m likwid=$HOME/sustainabench/configs/measurement/likwid.yaml -r $RUNS -c configs/workloads/stress-ng/$t.yaml -s
done

# STREAM (memory)
# 3 intensity levels:
# - small (25% cores)
# - medium (50% cores)
# - large (100% cores)
# Make sure that, at build, array size is set so that it exceeds LLC significantly, but fits in RAM safely
echo "Running STREAM experiments"
for t in 1 8 16 32; do
    echo "    stream (threads=$t)"
    OMP_PROC_BIND=spread \
    OMP_PLACES=cores \
    OMP_NUM_THREADS=$t \
    sustainabench run benchmark \
        -w stream \
        -m time -m likwid=$HOME/sustainabench/configs/measurement/likwid.yaml \
        -r $RUNS \
        -c configs/workloads/stream/default.yaml \
        -s
done


#####################################################
# Macro
#####################################################

# For both HPL and HPCG - keep same number of MPI ranks. Fix to number of CPU cores -> 32 cores means 32 MPI ranks. Avoids hybrid MPI/OpenMP scheduling effects

# HPL
# 3 intensity levels:
# - small N (underutilized system)
# - medium N (scaling region)
# - large N (memory + communication bound)
# Expected - energy/FLOP change is non-linear
echo "Running HPL experiments"
for t in "small" "medium" "large"; do
    echo "    HPL ($t)"
    sustainabench run benchmark -w hpl -m time -m likwid=$HOME/sustainabench/configs/measurement/likwid.yaml -r $RUNS -b mpi -np $MPI_RANKS -c configs/workloads/hpl/$t/hpl.yaml -s
done



# HPCG
# Memory-bound, so 3 intensities is not necessary. 
# 2 intensity levels ideal
# - medium (representative stable run)
# - large (stress memory + network)
# Aim to scale problem size only, so baseline at default or 128^3, large at 192^3 or max stable. Keep number of MPI ranks fixed, check how more work per rank varies
echo "Running HPCG experiments"
for t in "medium" "large"; do
    echo "    HPCG ($t)"
    OMP_NUM_THREADS=$DEFAULT_OMP_THREADS \
    sustainabench run benchmark \
    -w hpcg \
    -m time -m likwid=$HOME/sustainabench/configs/measurement/likwid.yaml \
    -r $RUNS \
    -b mpi -np $MPI_RANKS_WITH_OMP \
    -c configs/workloads/hpcg/$t/hpcg.yaml \
    -s
done


