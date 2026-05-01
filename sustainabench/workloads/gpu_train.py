import torch
import torch.nn as nn
from sustainabench.workloads.base import Workload, register_workload

@register_workload
class GPUTrainWorkload(Workload):
    """GPU Training workload"""
    name = "gpu-train"

    def run(self, num_processors: int, workload_cfg, context=None):
        if not torch.cuda.is_available(): # CUDA or ROCm GPU
            raise RuntimeError("CUDA is required for this benchmark but is not available on this system.")

        torch.backends.cudnn.benchmark = True

        steps = 50
        input_size = hidden_size = output_size = 4096
        batch_size = 1024
        if workload_cfg:
            if "steps" in workload_cfg["workload"]["params"]:
                steps = workload_cfg["workload"]["params"]["steps"]
            if "input_size" in workload_cfg["workload"]["params"]:
                input_size = workload_cfg["workload"]["params"]["input_size"]
            if "hidden_size" in workload_cfg["workload"]["params"]:
                hidden_size = workload_cfg["workload"]["params"]["hidden_size"]
            if "output_size" in workload_cfg["workload"]["params"]:
                output_size = workload_cfg["workload"]["params"]["output_size"]
            if "batch_size" in workload_cfg["workload"]["params"]:
                batch_size = workload_cfg["workload"]["params"]["batch_size"]

        model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        ).cuda()

        x = torch.randn(batch_size, input_size).cuda()

        torch.cuda.synchronize()

        for _ in range(steps):
            model.zero_grad(set_to_none=True)
            y = model(x)
            loss = y.sum()
            loss.backward()

        torch.cuda.synchronize()
