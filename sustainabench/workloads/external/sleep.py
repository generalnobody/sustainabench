from sustainabench.workloads.base import ExternalWorkload, register_workload
import subprocess

@register_workload
class SleepWorkload(ExternalWorkload):
    """Dummy external workload"""
    name = "sleep"
    require_wrapping = True
    require_config = False

    def execute(self):
        cmd = ["sleep", "5"]

        output = subprocess.run(cmd, capture_output=True, text=True)

        if output.returncode != 0:
            raise RuntimeError(
                f"FAILURE: Subprocess 'vllm' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )
    
    def process(self, backend_name: str):
        return {}
