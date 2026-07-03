#!/bin/bash
sustainabench run benchmark -w nvidia-hpl -m time -m cpu-energy -m gpu-nv -m memory -m network -c configs/nv-hpl/4GPUs/default.yaml -b local -np 1 -p 1 -o experiments/raw -we -nof
