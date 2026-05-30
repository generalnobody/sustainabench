import torch
import torch.nn as nn
from sustainabench.workloads.base import InternalWorkload, register_workload
from pydantic import BaseModel

@register_workload
class GPUTrainWorkload(InternalWorkload):
    """GPU Training workload"""
    name = "gpu-train"

    class WorkloadParams(BaseModel):
        steps: int = 50
        input_size: int = 4096
        hidden_size: int = 4096
        output_size: int = 4096
        batch_size: int = 1024

    def run(self, num_processors: int, context=None):
        if not torch.cuda.is_available(): # CUDA or ROCm GPU
            raise RuntimeError("CUDA is required for this benchmark but is not available on this system.")

        torch.backends.cudnn.benchmark = True
        
        if self.workload_cfg is None:
            params = self.WorkloadParams()
        else:
            params = self.WorkloadParams.model_validate(self.workload_cfg.params)


        model = nn.Sequential(
            nn.Linear(params.input_size, params.hidden_size),
            nn.ReLU(),
            nn.Linear(params.hidden_size, params.output_size)
        ).cuda()

        x = torch.randn(params.batch_size, params.input_size).cuda()

        torch.cuda.synchronize()

        for _ in range(params.steps):
            model.zero_grad(set_to_none=True)
            y = model(x)
            loss = y.sum()
            loss.backward()

        torch.cuda.synchronize()
