from .base import ExecutionBackend, register_backend

@register_backend
class LocalBackend(ExecutionBackend):
    """Runs benchmark locally."""
    name = "local"

    def __init__(self, num_processors: int = 1, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.num_processors = num_processors

    def run(self, runner):
        return runner._run_local(self.num_processors)
