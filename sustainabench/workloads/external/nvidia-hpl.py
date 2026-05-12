from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess

@register_workload
class CPUSingleWorkload(ExternalWorkload):
    """External Nvidia HPL benchmark runner & parser"""
    name = "nvidia-hpl"

    class WorkloadParams(BaseModel):
        executable: str
        flags: list[list[str]]

    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)

        # It is expected, that this is already run inside a MPI instance, so no mpi-specific runs here. Just call the executable with its arguments. Expected to be run using MPI backend.

        cmd = [params.executable] + [item for flag in params.flags for item in flag]

        output = subprocess.run(cmd, capture_output=True, text=True)

        if output.returncode != 0 or output.stdout == "":
            raise RuntimeError(
                f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )

        self.results = output.stdout.splitlines()

    def _parse_results(self, data):
        for i in range(1, len(data)):
            if data[i].startswith("T/V") and data[i-1].endswith("=\n"):
                data = data[i:]
                break

        for i in range(len(data)):
            if data[i].startswith("\n"):
                data = data[:i]
                break

        if len(data) < 3:
            raise ValueError("Incorrect data got selected. Size not large enough for further extraction. Ended up selecting: ", data)
        values = data[2].split() # Select third row of extracted data and split it
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

        headers = [
            "T/V",
            "N",
            "NB",
            "P",
            "Q",
            "Time",
            "Gflops",
            "per_GPU"
        ]

        return dict(zip(headers, cleaned))

        # parsed = []

        # for row in results:
        #     values = row.split()

        #     # Last value is inside parentheses (requires stripping off right parenthesis due to how output is done)
        #     # Example:
        #     # ['WC0', '19456', '1024', '1', '1', '16.04',
        #     #  '3.062e+02', '(', '3.062e+02)']

        #     cleaned = [
        #         values[0],  # T/V
        #         int(values[1]),
        #         int(values[2]),
        #         int(values[3]),
        #         int(values[4]),
        #         float(values[5]),
        #         float(values[6]),
        #         float(values[8].strip(")"))  # inside parentheses
        #     ]

        #     parsed.append(dict(zip(headers, cleaned)))

        # return parsed

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
