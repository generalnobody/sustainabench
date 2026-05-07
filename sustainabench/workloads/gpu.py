import torch
from sustainabench.workloads.base import Workload, register_workload
from pydantic import BaseModel

@register_workload
class GPUMatrixWorkload(Workload):
    """GPU Matrix-Multiplication workload"""
    name = "gpu-mm"

    class WorkloadParams(BaseModel):
        m: int = 2000
        n: int = 2000
        p: int = 2000

    def run(self, num_processors: int, context=None):
        if self.workload_cfg is None:
            params = self.WorkloadParams()
        else:
            params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)

        if torch.cuda.is_available(): # CUDA or ROCm GPU
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")

        print("Using device:", device)

        A = torch.randn(params.m, params.n, device=device)
        B = torch.randn(params.n, params.p, device=device)

        if device.type == "cuda":
            torch.cuda.synchronize()

        C = A @ B

        if device.type == "cuda":
            torch.cuda.synchronize()
