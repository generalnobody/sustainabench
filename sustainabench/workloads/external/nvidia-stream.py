from sustainabench.workloads.base import ExternalWorkload, register_workload
from sustainabench.utils.system_info import get_mpi_ranks
from pydantic import BaseModel
import subprocess
import re

@register_workload
class NvidiaStreamWorkload(ExternalWorkload):
    """External Nvidia Stream benchmark runner & parser"""
    name = "nvidia-stream"
    require_config = True
    require_wrapping = False

    class WorkloadParams(BaseModel):
        executable: str
        flags: list[list[str]]

    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        params = self.WorkloadParams.model_validate(self.workload_cfg.params)

        # It is expected, that this is already run inside a MPI instance, so no mpi-specific runs here. Just call the executable with its arguments. Expected to be run using MPI backend.

        cmd = [params.executable] + [item for flag in params.flags for item in flag]

        output = subprocess.run(cmd, capture_output=True, text=True)

        global_mpi_rank, _ = get_mpi_ranks()
        if (output.returncode != 0 or output.stdout == "") and (global_mpi_rank is None or global_mpi_rank == 0):
            raise RuntimeError(
                f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )

        self.results = output.stdout.splitlines()

    def _parse_results(self, data):
        results = {}

        for i in range(len(data)):
            if data[i].startswith("Function") and data[i+1].startswith("Copy:") and data[i+2].startswith("Scale:") and data[i+3].startswith("Add:") and data[i+4].startswith("Triad:"):
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
