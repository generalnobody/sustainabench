from sustainabench.measurement.base import InternalMeasurement, register_measurement
import os
import time

@register_measurement
class RAPLMeasurement(InternalMeasurement):
    name = "cpu-energy"
    poll_interval = None
    scope = "node"
    require_file = False
    only_once_per_node = True

    def _discover_domains(self, base_path="/sys/class/powercap/intel-rapl"): # Handles cases where multiple packages are present in system.
        domains = []

        if not os.path.exists(base_path):
            return domains

        for entry in os.listdir(base_path):
            path = os.path.join(base_path, entry)

            if not os.path.isdir(path):
                continue

            name_file = os.path.join(path, "name")
            energy_file = os.path.join(path, "energy_uj")
            max_file = os.path.join(path, "max_energy_range_uj")

            if not (os.path.exists(name_file) and os.path.exists(energy_file)):
                continue

            with open(name_file) as f:
                name = f.read().strip()

            # Only take package-level domains
            if "package" in name.lower():
                max_range = None
                if os.path.exists(max_file):
                    with open(max_file) as f:
                        max_range = int(f.read())

                domains.append({
                    "name": name,
                    "energy_path": energy_file,
                    "max_range": max_range
                })

        return domains
    
    def _read_energy(self):
        results = []

        for d in self.domains:
            with open(d["energy_path"]) as f:
                results.append(int(f.read()))
        
        return results
    
    def _energy_diff(self, start, end):
        diffs = []

        for i, d in enumerate(self.domains):
            s = start[i]
            e = end[i]
            max_range = d["max_range"]

            if max_range is not None and e < s: # Handle RAPL counter wrap-around
                diff = (max_range - s) + e
            else:
                diff = e - s

            diffs.append(diff)

        return diffs
    
    def start(self):
        self.domains = self._discover_domains()

        if not self.domains:
            raise RuntimeError("No RAPL domains found")

        self.start_energy = self._read_energy()
        self.start_time = time.perf_counter()
        self.end_energy = None
        self.end_time = None

    def stop(self):
        self.end_energy = self._read_energy()
        self.end_time = time.perf_counter()

    def sample(self):
        pass  # not used

    def result(self):
        if self.start_energy is None or self.end_energy is None or self.start_time is None or self.end_time is None:
            return {}

        diffs_uj = self._energy_diff(self.start_energy, self.end_energy)
        total_energy_j = sum(diffs_uj) / 1e6

        elapsed_time = self.end_time - self.start_time
        avg_total_power_w = total_energy_j / elapsed_time if elapsed_time > 0 else 0

        return {
            f"{self.name}": {
                "energy": {
                    "j": total_energy_j,
                    "kwh": total_energy_j / 3.6e6
                },
                "power": {
                    "w": avg_total_power_w
                },
                "per_domain": [
                    {
                        "energy": {
                            "j": d / 1e6,
                            "kwh": d / 3.6e12
                        },
                        "power": {
                            "w": (d / 1e6) / elapsed_time if elapsed_time > 0 else 0
                        }
                    }
                    for d in diffs_uj
                ]
            }
        }
