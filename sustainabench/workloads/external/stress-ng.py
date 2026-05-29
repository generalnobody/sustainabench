from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess
import re

@register_workload
class StressNGWorkload(ExternalWorkload):
    """Integrated workload that performs VLLM throughput benchmarking. VLLM parameters can be configured in config parameters."""
    name = "stress-ng"
    require_wrapping = False
    require_config = True

    class WorkloadParams(BaseModel):
        executable: str
        args: list[str]

    def execute(self):
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)
        cmd_params = [params.executable] + params.args + ["--metrics-brief"]
        output = subprocess.run(cmd_params, capture_output=True, text=True)

        if output.returncode != 0:
            raise RuntimeError(
                f"FAILURE: Subprocess {params.executable} failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )
        
        self.results = output.stdout.splitlines() if output.stdout != "" else None

    def _parse_results(self, data):
        results = {}

        for line in data:
            line = line.strip()
            # Runtime
            m = re.search(
                r"setting to a (\d+) mins?, (\d+) secs? run",
                line
            )
            if m:
                results["timeout_seconds"] = int(m.group(1)) * 60 + int(m.group(2))

            # Stressor dispatch
            m = re.search(
                r"dispatching hogs:\s+(\d+)\s+(\w+)",
                line
            )
            if m:
                results["workers"] = int(m.group(1))
                results["stressor"] = m.group(2)

            # Metrics line
            m = re.search(
                r"metrc:.*?cpu\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
                line
            )

            if m:
                results["metrics"] = {
                    "bogo_ops": int(m.group(1)),
                    "real_time_seconds": float(m.group(2)),
                    "user_time_seconds": float(m.group(3)),
                    "system_time_seconds": float(m.group(4)),
                    "bogo_ops_per_sec_real": float(m.group(5)),
                    "bogo_ops_per_sec_cpu": float(m.group(6)),
                }

            # Status
            for key in ["skipped", "failed", "metrics untrustworthy"]:
                m = re.search(rf"{re.escape(key)}:\s+(\d+)", line)
                if m:
                    results[key.replace(" ", "_")] = int(m.group(1))

            m = re.search(r"passed:\s+(\d+):\s+(\w+)\s+\((\d+)\)", line)
            if m:
                results["passed"] = {
                    "count": int(m.group(1)),
                    "name": m.group(2),
                    "workers": int(m.group(3)),
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
