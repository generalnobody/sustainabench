import psutil

from sustainabench.measurement.base import InternalMeasurement, register_measurement


@register_measurement
class NetworkMeasurement(InternalMeasurement):
    name = "network"
    poll_interval = None

    require_file = False
    only_once_per_node = True

    def _delta(self, start, end, bits=64):
        return end - start if end >= start else ((2**bits) - start) + end

    def start(self):
        self.start_net = psutil.net_io_counters()

    def sample(self):
        pass

    def stop(self):
        self.end_net = psutil.net_io_counters()

    def result(self):
        if self.start_net is None or self.end_net is None:
            return {}

        return {
            self.name: {
                "bytes": {
                    "sent": self._delta(
                        self.start_net.bytes_sent,
                        self.end_net.bytes_sent,
                    ),
                    "received": self._delta(
                        self.start_net.bytes_recv,
                        self.end_net.bytes_recv,
                    ),
                },
                "packets": {
                    "sent": self._delta(
                        self.start_net.packets_sent,
                        self.end_net.packets_sent,
                    ),
                    "received": self._delta(
                        self.start_net.packets_recv,
                        self.end_net.packets_recv,
                    ),
                },
            }
        }
