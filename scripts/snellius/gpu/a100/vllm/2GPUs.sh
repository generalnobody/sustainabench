#!/bin/bash

#SBATCH --job-name=sustainabench_gpu_vllm_2gpus
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --partition=gpu_a100
#SBATCH --gpus=2
#SBATCH --time=1:00:00
#SBATCH --exclusive

module load 2023
module load CUDA/12.4.0
module load pypmt/1.2.0-gfbf-2023a

# Answer the question: AI workload sustainability?

RUNS=3


echo "Warmup"
vllm --model --num-prompts 500 --input-len 2048 --output-len 256 --max-num-seqs 32 --tensor-parallel-size 2
echo "Running VLLM experiments"
sustainabench run benchmark -w nvidia-hpcg -m time -m rapl-pypmt -m gpu-nv -r $RUNS -c configs/vllm/2GPUs.yaml -s
