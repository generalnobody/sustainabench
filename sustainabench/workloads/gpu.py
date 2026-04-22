import torch
from sustainabench.workloads.base import Workload, register_workload

@register_workload
class GPUMatrixWorkload(Workload):
    """GPU Matrix-Multiplication workload"""
    name = "gpu-mm"

    def run(self, num_processors: int, workload_cfg):
        m = n = p = 2000
        if workload_cfg:
            if "m" in workload_cfg["workload"]["params"]:
                m = workload_cfg["workload"]["params"]["m"]
            if "n" in workload_cfg["workload"]["params"]:
                n = workload_cfg["workload"]["params"]["n"]
            if "p" in workload_cfg["workload"]["params"]:
                p = workload_cfg["workload"]["params"]["p"]

        if torch.cuda.is_available(): # CUDA or ROCm GPU
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")

        print("Using device:", device)

        A = torch.randn(m, n, device=device)
        B = torch.randn(n, p, device=device)

        if device.type == "cuda":
            torch.cuda.synchronize()

        C = A @ B

        if device.type == "cuda":
            torch.cuda.synchronize()
