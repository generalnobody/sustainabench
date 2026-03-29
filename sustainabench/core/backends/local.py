from sustainabench.core.backend import ExecutionBackend


class LocalBackend(ExecutionBackend):
    """Runs benchmark locally."""

    def run(self, runner):
        return runner._run_local()
