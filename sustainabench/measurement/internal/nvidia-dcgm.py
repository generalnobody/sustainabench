from sustainabench.measurement.base import InternalMeasurement, register_measurement
import tempfile
import subprocess
from pathlib import Path
from collections import defaultdict
import os

@register_measurement
class NvidiaDCGMMeasurement(InternalMeasurement):

    name = "nvidia-dcgm"
    poll_interval = None
    
    require_file = False

    def start(self):
        self._samples = []

        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)

        self._tmp_path = Path(path)
        self._log_file = open(self._tmp_path, "w")

        self._process = subprocess.Popen(
            [
                "dcgmi",
                "dmon",
                "-e",
                "155,156,157,203,204,210,211",
                "-d",
                "1000",
            ],
            stdout=self._log_file,
            stderr=subprocess.STDOUT,
            text=True
        )


    def sample(self):
        pass

    def stop(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None

        self._log_file.flush()
        self._log_file.close()

        with open(self._tmp_path, "r") as f:
            for line in f:
                self._samples.append(line.strip())

        Path(self._tmp_path).unlink(missing_ok=True)

    def result(self):

        results = []

        for sample in self._samples:
            parts = sample.split()

            if len(parts) < 7:
                continue
            
            try:
                results.append({
                        "gpu_id": int(parts[0]),
                        "gpu_util": float(parts[1]),
                        "sm_util": float(parts[2]),
                        "mem_util": float(parts[3]),
                        "power_w": float(parts[4]),
                        "temp_c": float(parts[5]),
                        "pcie_tx": float(parts[6]),
                        "pcie_rx": float(parts[7]) if len(parts) > 7 else None,
                    })
            except ValueError:
                continue

        grouped = defaultdict(list)
        for s in results:
            grouped[s["gpu_id"]].append(s)

        def avg(lst, key):
            vals = [x[key] for x in lst if x[key] is not None]
            return sum(vals) / len(vals) if vals else None


        def mx(lst, key):
            vals = [x[key] for x in lst if x[key] is not None]
            return max(vals) if vals else None

        per_gpu = {}
        global_stats = {}
        if results:
            for gpu_id, gpu_samples in grouped.items():
                per_gpu[gpu_id] = {
                    "num_samples": len(gpu_samples),
                    "avg_gpu_util": avg(gpu_samples, "gpu_util"),
                    "avg_sm_util": avg(gpu_samples, "sm_util"),
                    "avg_mem_util": avg(gpu_samples, "mem_util"),
                    "avg_power_w": avg(gpu_samples, "power_w"),
                    "max_temp_c": mx(gpu_samples, "temp_c"),
                }

            global_stats = {
                "num_samples": len(results),
                "avg_gpu_util": avg(results, "gpu_util"),
                "avg_power_w": avg(results, "power_w"),
                "max_temp_c": mx(results, "temp_c"),
            }



        return {
            self.name: {
                "stats": global_stats,
                "per_gpu": per_gpu,
                "raw": results
            }
        }
    