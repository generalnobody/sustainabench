import threading
import time
from sustainabench.utils.system_info import get_mpi_ranks

class MeasurementManager:

    def __init__(self, measurements):
        _, local_rank = get_mpi_ranks()
        self.measurements = [m for m in measurements if not m.only_once_per_node or local_rank is None or local_rank == 0]
        self._running = False
        self._thread = None

        # scheduling state
        self._next_sample = {}

    def start(self):
        now = time.perf_counter()

        for m in self.measurements:
            m.start()

            if m.poll_interval is not None:
                self._next_sample[m] = now

        if self._next_sample:
            self._running = True
            self._thread = threading.Thread(
                target=self._poll_loop,
                daemon=True,
            )
            self._thread.start()

    def _poll_loop(self):
        while self._running:

            now = time.perf_counter()
            next_wakeup = float("inf")

            for m, next_time in self._next_sample.items():

                if now >= next_time:
                    m.sample()
                    self._next_sample[m] += m.poll_interval

                remaining = self._next_sample[m] - now
                next_wakeup = min(next_wakeup, remaining)

            time.sleep(max(0.0, next_wakeup))

    def stop(self):
        self._running = False

        if self._thread:
            self._thread.join()

        for m in self.measurements:
            m.stop()

    def collect(self):
        results = {}
        for m in self.measurements:
            results.update(m.result())
        return results