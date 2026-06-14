#!/bin/bash
sustainabench run benchmark -w vllm -m time -m cpu-energy -m gpu-nv -c configs/vllm/4GPUs.yaml -b local -np 1 -p 1 -o experiments/raw -we -nof
