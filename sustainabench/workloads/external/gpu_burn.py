from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess
import re

@register_workload
class GPUBurnWorkload(ExternalWorkload):
    """Integrated workload that performs VLLM throughput benchmarking. VLLM parameters can be configured in config parameters."""
    name = "gpu-burn"
    require_wrapping = False
    require_config = True

    class WorkloadParams(BaseModel):
        dir: str
        executable: str
        args: list[str] | None

    def execute(self):
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)
        # cmd_params = ["vllm", "bench", "throughput"] + params.args
        # output = subprocess.run(cmd_params, capture_output=True, text=True)
        cmd = [params.executable]
        if params.args is not None:
            cmd += params.args

        output = subprocess.run(cmd, cwd=params.dir, capture_output=True, text=True)

        if output.returncode != 0:
            raise RuntimeError(
                f"FAILURE: Subprocess 'vllm' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )
        
        self.results = output.stdout.splitlines() if output.stdout != "" else None

    def _parse_results(self, data):
        results = {
            "gpus": [],
            "summaries": [],
            "final": {}
        }

        current_gpu = None

        for line in data:
            line = line.strip()
            # gpu header
            m = re.search(r'GPU (\d+): (.+?) \(UUID: (.+)\)', line)
            if m:
                current_gpu = {
                    "id": int(m.group(1)),
                    "name": m.group(2),
                    "uuid": m.group(3),
                }
                results["gpus"].append(current_gpu)

            # memory init
            m = re.search(
                r'Initialized device (\d+) with (\d+) MB of memory '
                r'\((\d+) MB available, using (\d+) MB of it\)',
                line
            )
            if m and current_gpu:
                current_gpu["memory_mb"] = int(m.group(2))
                current_gpu["available_mb"] = int(m.group(3))
                current_gpu["used_mb"] = int(m.group(4))


            # progress
            m = re.search(
                r'([\d.]+)%\s+proc\'d:\s+(\d+) '
                r'\((\d+) Gflop/s\)\s+errors:\s+(\d+)\s+temps:\s+(\d+) C',
                line
            )
            if m:
                results["summaries"].append({
                    "percent": float(m.group(1)),
                    "processed": int(m.group(2)),
                    "gflops": int(m.group(3)),
                    "errors": int(m.group(4)),
                    "temp_c": int(m.group(5)),
                })

            # final result
            m = re.search(r'GPU (\d+): (OK|FAIL)', line)
            if m:
                results["final"][f"gpu_{m.group(1)}"] = m.group(2)

        return results
    
    def process(self, backend_name: str):
        # Process the results obtained from the execute() method. Please make sure to turn them into a format that fits what this suite expects.
        results = {
            self.name: self._parse_results(self.results)
        }
        if backend_name == "local":
            results = {"local": results}
        elif backend_name == "mpi":
            results = {"global": results}
        else:
            raise ValueError(f"Backend {backend_name} currently not supported by workload {self.name}. Please modify the workload to support this backend.")

        return results
