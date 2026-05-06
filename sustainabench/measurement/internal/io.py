import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class IOMeasurement(Measurement):
    name = "io"
    poll_interval = None
    scope = "node"
    require_file = False

    def _delta(self, start, end, bits=64):
        return end - start if end >= start else ((2**bits) - start) + end

    def start(self):
        # self.samples = []
        self.start_disk = psutil.disk_io_counters()
        self.start_net = psutil.net_io_counters() # Maybe do this one pernic?

    def sample(self):
        # curr_disk = psutil.disk_io_counters()
        # curr_net = psutil.net_io_counters()

        # self.samples.append((curr_disk, curr_net))
        pass

    def stop(self):
        self.end_disk = psutil.disk_io_counters()
        self.end_net = psutil.net_io_counters()

    def result(self):
        # if not self.samples:
        #     return {}

        delta_disk = delta_net = {}

        if self.start_disk is not None and self.end_disk is not None:
            delta_disk = {
                "read_count": self._delta(self.start_disk.read_count, self.end_disk.read_count),
                "write_count": self._delta(self.start_disk.write_count, self.end_disk.write_count),
                "read_bytes": self._delta(self.start_disk.read_bytes, self.end_disk.read_bytes),
                "write_bytes": self._delta(self.start_disk.write_bytes, self.end_disk.write_bytes),
            }

        if self.start_net is not None and self.end_net is not None:
            delta_net = {
                "bytes_sent": self._delta(self.start_net.bytes_sent, self.start_net.bytes_sent),
                "bytes_recv": self._delta(self.start_net.bytes_recv, self.start_net.bytes_recv),
                "packets_sent": self._delta(self.start_net.packets_sent, self.start_net.packets_sent),
                "packets_recv": self._delta(self.start_net.packets_recv, self.start_net.packets_recv),
            }

        return {
            f"{self.name}": {
                "io_disk": delta_disk,
                "io_net": delta_net,
                # "samples": self.samples
            }
        }