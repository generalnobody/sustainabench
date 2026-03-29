# sustainabench
A sustainability benchmarking tool

## Install

Please ensure correct install for GPU version. For CUDA GPUs (NVIDIA), run (default index URL fetches torch for CUDA):

```bash
pip install . 
```

For ROCm GPUs (AMD), run:
```bash
pip install . --index-url https://download.pytorch.org/whl/rocm7.2
```

When neither is available (CPU-only), run:
```bash
pip install . --index-url https://download.pytorch.org/whl/cpu
```
