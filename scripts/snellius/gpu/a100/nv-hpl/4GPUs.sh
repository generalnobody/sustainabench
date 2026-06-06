#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_nv-hpl_4gpus
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --exclusive

module load 2023
module load CUDA/12.4.0
module load pypmt/1.2.0-gfbf-2023a

# Answer the question: GPU HPC scaling?
# Number of repetitions: 3. Low variability.

RUNS=3


echo "Warmup"
mpirun -np $SLURM_NTASKS /home/ibiemond/nvidia_hpc_benchmarks/cuda12/hpl.sh --dat /home/ibiemond/sustainabench/scripts/snellius/gpu/a100/configs/nv-hpl/4GPUs/HPL-4GPUs.dat
echo "Running Nvidia HPL experiments  (4 GPUs)"
sustainabench run benchmark -w nvidia-hpl -m time -m rapl-pypmt -m gpu-nv -r $RUNS -b mpi -np $SLURM_NTASKS -c configs/nv-hpl/4GPUs/default.yaml -s
