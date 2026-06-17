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
        params = self.WorkloadParams.model_validate(self.workload_cfg.params)
        # cmd_params = ["vllm", "bench", "throughput"] + params.args
        # output = subprocess.run(cmd_params, capture_output=True, text=True)
        cmd = [params.executable]
        if params.args is not None:
            cmd += params.args

        output = subprocess.run(cmd, cwd=params.dir, capture_output=True, text=True)

        if output.returncode != 0:
            raise RuntimeError(
                f"FAILURE: Subprocess '{self.name}' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )
        
        self.results = output.stdout.splitlines() if output.stdout != "" else None

    def _parse_results(self, data):
        results = {"gpus": []}

        gpu_map = {}
        last_progress_line = None

        for line in data:
            line = line.strip()

            # GPU header
            m = re.search(r'GPU (\d+): (.+?) \(UUID: (.+)\)', line)
            if m:
                gpu = {
                    "id": int(m.group(1)),
                    "name": m.group(2),
                    "uuid": m.group(3),
                    "memory": {},
                    "stats": {}
                }
                results["gpus"].append(gpu)
                gpu_map[gpu["id"]] = gpu
                continue

            # Memory info
            m = re.search(
                r'Initialized device (\d+) with (\d+) MB of memory '
                r'\((\d+) MB available, using (\d+) MB of it\)',
                line
            )

            if m:
                gpu_id = int(m.group(1))

                if gpu_id in gpu_map:
                    gpu_map[gpu_id]["memory"] = {
                        "total_mb": int(m.group(2)),
                        "available_mb": int(m.group(3)),
                        "used_mb": int(m.group(4))
                    }

                continue

            # Save the LAST progress line only
            if re.search(r"[\d.]+%\s+proc'd:", line):
                last_progress_line = line
                continue

            # Final pass/fail result
            m = re.search(r'GPU (\d+): (OK|FAIL)', line)

            if m:
                gpu_id = int(m.group(1))

                if gpu_id in gpu_map:
                    gpu_map[gpu_id]["stats"]["result"] = m.group(2)

        # Parse the final progress line
        if last_progress_line:
            # processed/gflops pairs
            perf = re.findall(
                r'(\d+)\s+\((\d+)\s+Gflop/s\)',
                last_progress_line
            )

            # errors
            errors_match = re.search(
                r'errors:\s*(.*?)\s*temps:',
                last_progress_line
            )

            errors = []
            if errors_match:
                errors = [
                    int(x.strip())
                    for x in errors_match.group(1).split('-')
                ]

            # temperatures
            temps_match = re.search(
                r'temps:\s*(.*)',
                last_progress_line
            )

            temps = []
            if temps_match:
                temps = [
                    int(x)
                    for x in re.findall(r'(\d+)\s*C', temps_match.group(1))
                ]

            # Attach stats to GPUs by position
            gpu_ids = sorted(gpu_map.keys())

            for idx, gpu_id in enumerate(sorted(gpu_map.keys())):
                gpu = gpu_map[gpu_id]

                if idx < len(perf):
                    gpu["stats"]["processed"] = int(perf[idx][0])
                    gpu["stats"]["gflops"] = int(perf[idx][1])

                if idx < len(errors):
                    gpu["stats"]["errors"] = errors[idx]

                if idx < len(temps):
                    gpu["stats"]["temp_c"] = temps[idx]

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
