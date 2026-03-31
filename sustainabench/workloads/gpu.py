import torch
from sustainabench.workloads.base import Workload, register_workload

@register_workload
class CGPUMatrixWorkload(Workload):
    """GPU Matrix-Multiplication workload"""
    name = "gpu-mm"

    def run(self, *args: object, **kwargs: object):
        if torch.cuda.is_available(): # CUDA or ROCm GPU
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")

        print("Using device:", device)

        A = torch.randn(2000, 2000, device=device)
        B = torch.randn(2000, 2000, device=device)

        if device.type == "cuda":
            torch.cuda.synchronize()

        for _ in range(5):
            _ = A @ B

        if device.type == "cuda":
            torch.cuda.synchronize()
