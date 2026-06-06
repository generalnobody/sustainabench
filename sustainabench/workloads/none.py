from sustainabench.workloads.base import InternalWorkload, register_workload

@register_workload
class NoneWorkload(InternalWorkload):
    """Dummy workload only used for testing"""
    name = "none"

    def run(self, num_processors: int, context=None):
        pass
