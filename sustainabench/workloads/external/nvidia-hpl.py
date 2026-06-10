from sustainabench.workloads.base import ExternalWorkload, register_workload
from sustainabench.utils.system_info import get_mpi_ranks
from pydantic import BaseModel
import subprocess

@register_workload
class NvidiaHPLWorkload(ExternalWorkload):
    """External Nvidia HPL benchmark runner & parser"""
    name = "nvidia-hpl"
    require_config = True
    require_wrapping = True

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
        data_sel = []
        for i in range(1, len(data)):
            if data[i].startswith("T/V") and data[i-1].endswith("="):
                data_sel = data[i:]
                break

        for i in range(len(data_sel)):
            if data_sel[i] == "":
                data_sel = data_sel[:i]
                break

        if len(data_sel) < 3:
            raise ValueError("Incorrect data got selected. Size not large enough for further extraction. Ended up selecting: ", data_sel, "\nOriginal data: ", data)
        raw_headers = data_sel[0].split()
        headers = [
            raw_headers[0],
            raw_headers[1],
            raw_headers[2],
            raw_headers[3],
            raw_headers[4],
            raw_headers[5],
            raw_headers[6],
            f"{raw_headers[8]}_{raw_headers[9]}".strip(")"),

        ]
        values = data_sel[2].split() # Select third row of extracted data and split it
        cleaned = [
            values[0],  # T/V
            int(values[1]),
            int(values[2]),
            int(values[3]),
            int(values[4]),
            float(values[5]),
            float(values[6]),
            float(values[8].strip(")"))  # inside parentheses
        ]

        return dict(zip(headers, cleaned))
    
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
