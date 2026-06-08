from sustainabench.measurement.base import  ExternalMeasurement, register_measurement
from sustainabench.utils.system_info import get_mpi_ranks, get_node_metadata

@register_measurement
class PerfEnergyMeasurement(ExternalMeasurement):
    name = "perf-energy"
    poll_interval = None
    scope = "node"
    require_file = False
    rank_priority = 100
    within_wrapper = True
    only_once_per_node = True
    replace_wrapper = []
    wrapper_conflicts = ["likwid"]

    def get_wrap_command(self, backend_name, node_processors):        
        self.backend_name = backend_name

        cmd = [
            "perf",
            "stat",
            "-e", "power/energy-pkg/",
            "2>&1"
        ]

        return cmd

    def _parse_perf_output(self, results: list[str]):
        energy_line = ""
        time_line = ""
        for i in range(len(results)):
            if results[i].strip().startswith("Performance counter stats"):
                energy_line = results[i+2].strip()
                time_line = results[i+4].strip()

        if energy_line == "" or time_line == "":
            return {}
        
        return {
            "joules": float(energy_line.split()[0]),
            "time": float(time_line.split()[0])
        }

    def process_results(self, output: str, nodeids: list[str]) -> dict:
        parsed = self._parse_perf_output(output.splitlines())

        metadata = get_node_metadata()
        rank, local_rank = get_mpi_ranks()
        node_id = f"{metadata['hostname']}:{rank}:{local_rank}" if local_rank is not None else f"{metadata['hostname']}:{rank}" if rank is not None else "local"
        result = {
            node_id: {
                self.name: parsed
            }
        }
        return result
