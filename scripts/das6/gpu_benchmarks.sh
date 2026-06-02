#!/bin/bash

#SBATCH --job-name=sustainabench_gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --time=01:00:00
#SBATCH --gres=gpu:1
#SBATCH --constraint=A4000


RUNS=5
MPI_RANKS=24
DEFAULT_OMP_THREADS=4
MPI_RANKS_WITH_OMP=$(($MPI_RANKS/$DEFAULT_OMP_THREADS))


module load cuda12.6/toolkit # Load Nvidia CUDA

#####################################################
# Micro
#####################################################

# gpu-burn (compute)
# Only 1 intensity level, but prepend a 'thermal ramp' (30-60s) run to pre-warm the GPU, excluded from measurements. 
# Intensity scaling does not show much, as gpu-burn is designed as a saturation stress test
echo "Running gpu-burn experiments"
( # Thermal ramp, not measured
    cd "/home/ibd350/gpu-burn" || exit 1
    ./gpu_burn 60
)
sustainabench run benchmark -w gpu-burn -m time -m gpu-nv -r $RUNS -c configs/workloads/gpu-burn/default.yaml



# Nvidia STREAM (memory)
# 2 intensity levels (memory bandwidth saturates quickly):
# - low (fits partly in L2 / cache effects)
# - high (fully exceed cache - DRAM/HBM bound)
# Basically exploit what STREAM is made for
echo "Running Nvidia STREAM experiments"
for t in "low" "high"; do
    echo "    Nvidia STREAM ($t)"
    sustainabench run benchmark -w nvidia-stream -m time -m gpu-nv -r $RUNS -c configs/workloads/nvidia-stream/$t.yaml
done

#####################################################
# Macro
#####################################################

# For both HPL and HPCG - keep same number of MPI ranks. Fix to number of CPU cores -> 32 cores means 32 MPI ranks. Avoids hybrid MPI/OpenMP scheduling effects

# Nvidia HPL
# 3 intensity levels:
# - small N (underutilized system) (30-40% VRAM usage)
# - medium N (scaling region) (60-70% VRAM usage)
# - large N (memory + communication bound) (80-90% VRAM usage)
# Expected - energy/FLOP change is non-linear
echo "Running Nvidia HPL experiments"
for t in "small" "medium" "large"; do
    echo "    Nvidia HPL ($t)"
    sustainabench run benchmark -w nvidia-hpl -m time -m gpu-nv -r $RUNS -b mpi -np $MPI_RANKS -c configs/workloads/nvidia-hpl/$t/default.yaml
done

# Nvidia HPCG
# Memory-bound, so 3 intensities is not necessary. 
# 2 intensity levels ideal
# - medium (representative stable run)
# - large (stress memory + network)
echo "Running Nvidia HPCG experiments"
for t in "medium" "large"; do
    echo "    Nvidia HPCG ($t)"
    OMP_NUM_THREADS=1 \
    sustainabench run benchmark \
    -w nvidia-hpcg \
    -m time -m gpu-nv \
    -r $RUNS \
    -b mpi -np 1 \
    -c configs/workloads/nvidia-hpcg/$t.yaml
done

# VLLM throughput benchmark
# Intensity defined by workload shape affecting GPU utilization, memory pressure,
# and KV-cache behavior.
# - low: batch=1, seq=512, small model (latency-bound)
# - medium: batch=8–16, seq=1024, medium model (balanced throughput)
# - high: max stable batch, seq=2048, largest model (memory/throughput bound)
echo "Running vllm experiments"
for t in "low" "medium" "high"; do
    echo "    vllm ($t)"
    sustainabench run benchmark -w vllm -m time -m gpu-nv -r $RUNS -c configs/workloads/vllm/$t.yaml
done
