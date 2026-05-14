from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess
import tempfile
import shutil
from pathlib import Path
from mpi4py import MPI

@register_workload
class HPCGWorkload(ExternalWorkload):
    """External Nvidia HPL benchmark runner & parser"""
    name = "hpcg"

    class WorkloadParams(BaseModel):
        dir: str
        executable: str

    def execute(self, node_processors):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)

        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        if self.rank == 0:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                datfile = "hpcg.dat"
                shutil.copy(Path(params.dir)/datfile, tmpdir / datfile)
                cmd = [
                    "mpirun",
                    "-np", str(node_processors),
                    params.executable
                ]
                subprocess.run(cmd, cwd = tmpdir)
                output_matches = list(tmpdir.glob("HPCG-Benchmark*.txt"))
                self.results = output_matches[0].read_text(encoding="utf-8").splitlines()

        self.comm.Barrier()

    def _parse_results(self, data):
        results = {}

        for line in data:
            line = line.strip()

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key_parts = key.split("::")

            # try to convert value to float/int if possible
            value = value.strip()
            try:
                if "." in value or "e" in value.lower():
                    value_cast = float(value)
                else:
                    value_cast = int(value)
                value = value_cast
            except:
                pass  # keep as string

            # build nested dict
            cur = results

            for part in key_parts[:-1]:
                if part not in cur:
                    cur[part] = {}
                elif not isinstance(cur[part], dict):
                    cur[part] = {"_value": cur[part]}

                cur = cur[part]

            leaf = key_parts[-1]

            # handle collision at leaf too
            if leaf in cur and isinstance(cur[leaf], dict):
                cur[leaf]["_value"] = value
            else:
                cur[leaf] = value

        return results
    
    def process(self, backend_name: str):
        # Process the results obtained from the execute() method. Please make sure to turn them into a format that fits what this suite expects.
        results = {}
        if self.rank == 0:
            results = {
                self.name: self._parse_results(self.results)
            }
            if backend_name == "local":
                results = {"local": results}
            elif backend_name == "mpi":
                results = {"global": results}
            else:
                raise ValueError(f"Backend {backend_name} currently not supported by workload {self.name}. Please modify the workload to support this backend.")
            
        self.comm.Barrier()

        return results
