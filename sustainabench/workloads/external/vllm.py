from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess
from pathlib import Path

@register_workload
class VLLMWorkload(ExternalWorkload):
    """Integrated workload that performs VLLM throughput benchmarking. VLLM parameters can be configured in config parameters."""
    name = "vllm"
    require_wrapping = False
    require_config = True

    class WorkloadParams(BaseModel):
        args: list[str]

    def execute(self):
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)
        cmd_params = ["vllm", "bench", "throughput"] + params.args
        output = subprocess.run(cmd_params)

        if output.returncode != 0:
            raise RuntimeError(
                f"FAILURE: Subprocess 'vllm' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )
        
        self.results = output.stdout.splitlines() if output.stdout != "" else None

    def _parse_results(self, data):
        results = {}

        for i in range(len(data) - 2):
            if data[i].startswith("Throughput:") and data[i+1].startswith("Total num prompt tokens:") and data[i+2].startswith("Total num output tokens:"):
                _, rest = data[i].split(":", 1)
                parts = [p.strip() for p in rest.split(",")]
                results["throughput"] = {
                    "reqs/s": float(parts[0].split()[0]),
                    "tot_tkn/s": float(parts[1].split()[0]),
                    "out_tkn/s": float(parts[2].split()[0])
                }

                key, value = data[i+1].split(":", 1)
                normalized_key = key.strip().lower().replace(" ", "_")
                results[normalized_key] = int(value.strip())

                key, value = data[i+2].split(":", 1)
                normalized_key = key.strip().lower().replace(" ", "_")
                results[normalized_key] = int(value.strip())

                break

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
