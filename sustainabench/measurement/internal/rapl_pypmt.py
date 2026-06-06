from sustainabench.measurement.base import InternalMeasurement, register_measurement
from sustainabench.utils.system_info import get_mpi_ranks
import pypmt # type: ignore # Only works on Snellius

@register_measurement
class RaplPypmtMeasurement(InternalMeasurement):
    name = "rapl-pypmt"
    poll_interval = None
    scope = "node"
    require_file = False
    
    def start(self):
        self.pmt = pypmt.Rapl.create()
        self.start = self.pmt.read()

    def stop(self):
        self.end = self.pmt.read()

    def sample(self):
        pass  # not used

    def result(self):
        _, local_mpi_rank = get_mpi_ranks()
        if local_mpi_rank == 0 or local_mpi_rank == None: # Prevent duplication with multiple MPI ranks per node
            return {
                self.name: {
                    "j": pypmt.PMT.joules(self.start, self.end),
                    "w": pypmt.PMT.watts(self.start, self.end),
                    "s": pypmt.PMT.seconds(self.start, self.end)
                }
            }
        else:
            return {}