#!/bin/bash
sustainabench run benchmark -w nvidia-hpcg -m time -m likwid=configs/likwid.yaml -m gpu-nv -c configs/nv-hpcg.yaml -p 1 -we -nof
