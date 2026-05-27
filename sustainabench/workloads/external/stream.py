from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess
import os
import re

@register_workload
class StreamWorkload(ExternalWorkload):
    """Integrated workload that performs the STREAM benchmark."""
    name = "stream"
    require_wrapping = False
    require_config = True

    class WorkloadParams(BaseModel):
        executable: str

    def execute(self):
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = str(os.cpu_count()) # Allow STREAM to use all CPU cores
        output = subprocess.run(params.executable, env=env, capture_output=True, text=True)

        if output.returncode != 0:
            raise RuntimeError(
                f"FAILURE: Subprocess 'vllm' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )
        
        self.results = output.stdout.splitlines() if output.stdout != "" else None

    def _parse_results(self, data):
        results = {}

        for i in range(len(data)):
            if data[i].startswith("Function") and data[i+1].startswith("Copy:") and data[i+2].startswith("Scale:") and data[3].startswith("Add:") and data[i+4].startswith("Triad:"):
                headers = [
                    h.strip().replace(" ", "_")
                    for h in re.split(r'\s{2,}', data[i])
                ]

                rows = [data[i + j].split() for j in range(1, 5)]

                results[headers[0]] = {
                    row[0]: {
                        headers[k]: float(row[k])
                        for k in range(1, len(headers))
                    }
                    for row in rows
                }

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
