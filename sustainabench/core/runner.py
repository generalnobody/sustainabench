from pathlib import Path
from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.schemas.results.benchmark import BenchmarkResult, NodeResult
from sustainabench.schemas.configs.workloads.config import WorkloadConfig
from sustainabench.workloads.base import ExternalWorkload
import yaml
import json
import subprocess
from pydantic import ValidationError

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, config_filepath, measurement_names, runs, backend, wrapped_execution):
        if workload_name not in WORKLOADS:
            raise ValueError(f"Unknown workload: {workload_name}")
        
        workload_cfg = None
        if config_filepath != Path(""):
            tmp = None
            with open(config_filepath) as f:
                tmp = yaml.safe_load(f)
            workload_cfg = WorkloadConfig.model_validate(tmp)
        self.workload = WORKLOADS[workload_name](workload_cfg)
        self.config_filepath = config_filepath

        measurement_dict = {}
        for name in measurement_names:
            file = ""
            if "=" in name:
                name, file = name.split("=", 1)
            if name not in MEASUREMENTS:
                raise ValueError(f"Unknown measurement: {name}")
            measurement_dict[name] = file

        self.measurements = [
            MEASUREMENTS[name](file)
            for name, file in measurement_dict.items()
        ]

        for measurement in self.measurements: # Check if all measurements got their required files
            if measurement.require_file and measurement_dict[measurement.name] == "":
                raise ValueError(f"File not provided for measurement '{measurement.name}'. Use as follows: -m {measurement.name}=<file>.")

        if runs < 1:
            raise ValueError(f"Cannot perform {runs} runs")
            
        self.runs = runs
        self.backend = backend
        self.wrapped_execution = wrapped_execution

    def _process_wrapped_results(self, output: str) -> list[NodeResult]:
        decoder = json.JSONDecoder()
        json_objects = []
        
        i = 0
        while i < len(output):
            if output[i] == "{":
                try:
                    obj, end = decoder.raw_decode(output[i:])
                    json_objects.append(obj)
                    i += end
                    continue
                except json.JSONDecodeError:
                    pass

        results = []
        for obj in json_objects:
            try:
                node_result = NodeResult.model_validate(obj)
                results.append(node_result)
            except ValidationError:
                pass
        return results

    def run(self) -> BenchmarkResult:
        """Function that runs the benchmark on the correct backend (only internal measurements)"""
        results = {}
        for i in range(self.runs):
            if isinstance(self.workload, ExternalWorkload) and self.workload.require_wrapping and not self.wrapped_execution:
                measurement_filelist = [
                    (m.name, getattr(m, "file", None))
                    for m in self.measurements
                ]
                measurement_array = []
                if len(measurement_filelist) > 0:
                    for measurement, filename in measurement_filelist:
                        if filename: 
                            measurement_array.extend(["-m", f"{measurement}={filename}"])
                        else:
                            measurement_array.extend(["-m", measurement])
                else:
                    measurement_array.extend(["-m", "none"])

                cmd = self.backend.get_wrap_command() + [
                    "sustainabench",
                    "run",
                    "benchmark",
                    "-w", self.workload.name
                ] + measurement_array + [
                    "-c", str(self.config_filepath),
                    "-p", str(self.backend.num_processors),
                    "-we",
                    "-nof"
                ]
                output = subprocess.run(cmd, capture_output=True, text=True)

                if output.returncode != 0 or output.stdout == "":
                    raise RuntimeError(
                        f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                        f"STDOUT: {output.stdout}\nSTDERR: {output.stderr}"
                    )
                node_results = self._process_wrapped_results(output.stdout)

            else:
                node_results = self.backend.run(self)

            if node_results:
                results[f"run{i}"] = node_results

        return BenchmarkResult(
            workload=self.workload.name,
            backend=self.backend.name,
            results=results,
            metadata={}
        )

    def get_measurements(self):
        return self.measurements

    def get_workload(self):
        return self.workload

    def get_runs(self):
        return self.runs