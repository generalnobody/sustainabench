from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from sustainabench.utils.system_info import get_mpi_ranks

@register_workload
class HPCGWorkload(ExternalWorkload):
    """External HPCG benchmark runner & parser"""
    name = "hpcg"
    require_wrapping = True
    require_config = True

    class WorkloadParams(BaseModel):
        dir: str
        executable: str
        args: list[list[str]]

    def _extract_datetime(self, path: Path) -> datetime:
        # e.g. filename: HPCG-Benchmark_3.1_2026-05-13_14-46-42.txt
        parts = path.stem.split("_")
        date_str = parts[-2] + "_" + parts[-1]  # "2026-05-13_14-46-42"
        return datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")

    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        params = self.WorkloadParams.model_validate(self.workload_cfg.params)
        cmd = [params.executable] + [item for flag in params.args for item in flag]
        workdir = Path(params.dir)
        output = subprocess.run(cmd, cwd = workdir)

        if output.returncode != 0:
            raise RuntimeError(
                f"FAILURE: Subprocess {params.executable} failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )
        
        rank, _ = get_mpi_ranks()
        if rank == 0:
            output_matches = list(workdir.glob("HPCG-Benchmark*.txt"))
            latest_file = max(output_matches, key=self._extract_datetime)
            self.results = latest_file.read_text(encoding="utf-8").splitlines()
            latest_file.unlink()
        else:
            self.results = None

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
        if not self.results:
            return {}
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
