import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class CPUMeasurement(Measurement):
    name = "cpu-usage"
    poll_interval = 0.1
    scope = "node"

    def start(self):
        self.samples = []
        psutil.cpu_percent(interval=None) # Ignore first bogus value
        psutil.cpu_percent(interval=None, percpu=True)
        # psutil.cpu_times_percent(interval=None)
        # psutil.cpu_times_percent(interval=None, percpu=True)

    def sample(self):
        self.samples.append((
            psutil.cpu_percent(interval=None),
            psutil.cpu_percent(interval=None, percpu=True),
            # psutil.cpu_times_percent(interval=None)._asdict(),
            # [t._asdict() for t in psutil.cpu_times_percent(interval=None, percpu=True)]
        ))

    def stop(self):
        pass

    def result(self):
        if not self.samples:
            return {"cpu_avg": 0, "cpu_max": 0, "per-core": {}}

        cpu_avg = sum(sample[0] for sample in self.samples) / len(self.samples)
        cpu_max = max(sample[0] for sample in self.samples)

        per_cpu_avg = [
            sum(col) / len(col)
            for col in zip(*(sample[1] for sample in self.samples))
        ]
        per_cpu_max = [
            max(col)
            for col in zip(*(sample[1] for sample in self.samples))
        ]

        # cpu_times_avg = { # Should sum to approximately 100% (slight deviation possible due to floating point shift)
        #     key: sum(sample[2][key] for sample in self.samples) / len(self.samples)
        #     for key in self.samples[0][2]
        # }

        # cpu_times_max = { # Measures spikes. Is not expected to sum to 100%
        #     key: max(sample[2][key] for sample in self.samples)
        #     for key in self.samples[0][2]
        # }

        # per_cpu_times_avg = [] # Same logic as for cpu_times_avg
        # for core_idx in range(len(self.samples[0][3])):
        #     core_avg = {
        #         key: sum(sample[3][core_idx][key] for sample in self.samples) / len(self.samples)
        #         for key in self.samples[0][3][core_idx]
        #     }
        #     per_cpu_times_avg.append(core_avg)

        # per_cpu_times_max = [] # Same logic as for cpu_times_max
        # for core_idx in range(len(self.samples[0][3])):
        #     core_max = {
        #         key: max(sample[3][core_idx][key] for sample in self.samples)
        #         for key in self.samples[0][3][core_idx]
        #     }
        #     per_cpu_times_max.append(core_max)

        return {
            "cpu_avg": cpu_avg,
            "cpu_max": cpu_max,
            "per_cpu_avg": per_cpu_avg,
            "per_cpu_max": per_cpu_max,
            # "cpu_times_avg": cpu_times_avg,
            # "cpu_times_max": cpu_times_max,
            # "per_cpu_times_avg": per_cpu_times_avg,
            # "per_cpu_times_max": per_cpu_times_max
        }