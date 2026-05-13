from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess

@register_workload
class CPUSingleWorkload(ExternalWorkload):
    """External Nvidia HPL benchmark runner & parser"""
    name = "hpl"

    class WorkloadParams(BaseModel):
        dir: str
        executable: str

    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)

        # It is expected, that this is already run inside a MPI instance, so no mpi-specific runs here. Just call the executable with its arguments. Expected to be run using MPI backend.

        output = subprocess.run(params.executable, cwd=params.dir, capture_output=True, text=True)

        if output.returncode != 0 or output.stdout == "":
            raise RuntimeError(
                f"FAILURE: Subprocess {params.executable} failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )

        self.results = output.stdout.splitlines()

    def _parse_results(self, data):
        result_blocks = []
        # Find first resuit
        for i in range(1, len(data)):
            if data[i].startswith("T/V") and data[i-1].endswith("=") and data[i+8].endswith("PASSED"): # Only append passed data
                block_data = data[i+2].split()
                block = {
                    "T/V": block_data[0],
                    "N":  int(block_data[1]),
                    "NB":  int(block_data[2]),
                    "P":  int(block_data[3]),
                    "Q":  int(block_data[4]),
                    "Time":  float(block_data[5]),
                    "Gflops":  float(block_data[6])
                }
                result_blocks.append(block)

        max_block = result_blocks[0]
        for block in result_blocks:
            if block["Gflops"] > max_block["Gflops"]:
                max_block = block

        return max_block
    
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
