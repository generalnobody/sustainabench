#!/bin/bash
sustainabench run benchmark -w nvidia-hpcg -m time -m gpu-nv -c configs/nv-hpcg.yaml -b local -np 1 -p 1 -o experiments/raw -we -nof
