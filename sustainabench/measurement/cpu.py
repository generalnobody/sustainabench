import psutil
from sustainabench.measurement.base import Measurement, register_measurement


@register_measurement
class CPUMeasurement(Measurement):
    name = "cpu"
    poll_interval = 0.1
    scope = "node"

    def start(self):
        self.samples = []
        psutil.cpu_percent(interval=None) # Ignore first bogus value
        psutil.cpu_percent(interval=None, percpu=True)
        # psutil.cpu_times_percent(interval=None)
        # psutil.cpu_times_percent(interval=None, percpu=True)

        ################# Test #################
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            print(f"{name}:")
            for entry in entries:
                print(f"  {entry.label or 'N/A'}: {entry.current}°C")
        ########################################

    def sample(self):
        cpu_freq = psutil.cpu_freq()
        per_cpu_freq = psutil.cpu_freq(percpu=True)

        self.samples.append((
            psutil.cpu_percent(interval=None),
            psutil.cpu_percent(interval=None, percpu=True),
            cpu_freq.current,
            [freq.current for freq in per_cpu_freq]
            # psutil.cpu_times_percent(interval=None)._asdict(),
            # [t._asdict() for t in psutil.cpu_times_percent(interval=None, percpu=True)]
        ))

    def stop(self):
        pass

    def result(self):
        if not self.samples:
            return {}

        # Usage
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


        # Frequency
        cpu_freq = psutil.cpu_freq()
        per_cpu_freq = psutil.cpu_freq(percpu=True)

        cpu_freq_avg = sum(sample[2] for sample in self.samples) / len(self.samples)
        percore_freq_avg = [
            sum(values) / len(values)
            for values in zip(*(sample[3] for sample in self.samples))
        ]

        return {
            "cpu": {
                "usage": {
                    "avg": cpu_avg,
                    "max": cpu_max,
                },
                "frequency": {
                    "min": cpu_freq.min,
                    "max": cpu_freq.max,
                    "avg": cpu_freq_avg,
                },
            },
            "percpu": [
                {
                    "core": i,
                    "usage": {
                        "avg": u_avg,
                        "max": u_max,
                    },
                    "frequency": {
                        "avg": f_avg,
                        "min": freq.min,
                        "max": freq.max,
                    },
                }
                for i, (u_avg, u_max, f_avg, freq) in enumerate(
                    zip(per_cpu_avg, per_cpu_max, percore_freq_avg, per_cpu_freq)
                )
            ]
        }

        # percpu = [
        #     {
        #         "core": i,
        #         "avg": avg,
        #         "min": freq.min,
        #         "max": freq.max,
        #     }
        #     for i, (avg, freq) in enumerate(zip(percore_freq_avg, per_cpu_freq))
        # ]

        # cpu_times_avg = { # Should sum to approximately 100% (slight deviation possible due to floating point shift)
        #     key: sum(sample[4][key] for sample in self.samples) / len(self.samples)
        #     for key in self.samples[0][4]
        # }

        # cpu_times_max = { # Measures spikes. Is not expected to sum to 100%
        #     key: max(sample[4][key] for sample in self.samples)
        #     for key in self.samples[0][4]
        # }

        # per_cpu_times_avg = [] # Same logic as for cpu_times_avg
        # for core_idx in range(len(self.samples[0][5])):
        #     core_avg = {
        #         key: sum(sample[5][core_idx][key] for sample in self.samples) / len(self.samples)
        #         for key in self.samples[0][5][core_idx]
        #     }
        #     per_cpu_times_avg.append(core_avg)

        # per_cpu_times_max = [] # Same logic as for cpu_times_max
        # for core_idx in range(len(self.samples[0][5])):
        #     core_max = {
        #         key: max(sample[5][core_idx][key] for sample in self.samples)
        #         for key in self.samples[0][5][core_idx]
        #     }
        #     per_cpu_times_max.append(core_max)

        # return {
        #     "cpu_avg": cpu_avg,
        #     "cpu_max": cpu_max,
        #     "per_cpu_avg": per_cpu_avg,
        #     "per_cpu_max": per_cpu_max,
        #     # "cpu_times_avg": cpu_times_avg,
        #     # "cpu_times_max": cpu_times_max,
        #     # "per_cpu_times_avg": per_cpu_times_avg,
        #     # "per_cpu_times_max": per_cpu_times_max
        # }