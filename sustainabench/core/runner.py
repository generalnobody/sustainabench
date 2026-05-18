from pathlib import Path
from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.measurement.base import ExternalMeasurement
from sustainabench.schemas.results.benchmark import BenchmarkResult, NodeResult
from sustainabench.schemas.configs.workloads.config import WorkloadConfig
from sustainabench.workloads.base import ExternalWorkload
import yaml
import json
import subprocess
from pydantic import ValidationError
import tempfile

class BenchmarkRunner:
    """Class than handles running the benchmarks"""

    def __init__(self, workload_name, config_filepath, measurement_names, runs, backend, output_dir, wrapped_execution):
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
        self.output_dir = output_dir
        self.wrapped_execution = wrapped_execution

    def _process_wrapped_results(self, output: str) -> list[NodeResult]:
        decoder = json.JSONDecoder()
        json_objects = []
        
        for i in range(len(output)):
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

        external_measurements = [
            m for m in self.measurements if isinstance(m, ExternalMeasurement) 
        ]

        for i in range(self.runs):
            if isinstance(self.workload, ExternalWorkload) and self.workload.require_wrapping and not self.wrapped_execution:
                # measurement_array = self._get_measurements_for_cli(self.measurements)
                # cmd = self.backend.get_wrap_command() + [
                #     "sustainabench",
                #     "run",
                #     "benchmark",
                #     "-w", self.workload.name
                # ] + measurement_array + [
                #     "-c", str(self.config_filepath),
                #     "-p", str(self.backend.num_processors),
                #     "-we",
                #     "-nof"
                # ]
                # output = subprocess.run(cmd, capture_output=True, text=True)

                with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", dir=self.output_dir) as f: # Technically not necessary with local/mpi backend, but you never know when some backend might be annoying like likwid-mpirun
                    measurement_array = self._get_measurements_for_cli(self.measurements)
                    script = f"#!/bin/bash\nsustainabench run benchmark -w {self.workload.name} {' '.join(measurement_array)} -c {str(self.config_filepath)} -p {str(self.backend.num_processors)} -we -nof\n"
                    f.write(script)
                    f.flush()

                    cmd = self.backend.get_wrap_command() + [
                        "--",
                        "bash", f.name
                    ]

                    output = subprocess.run(cmd, capture_output=True, text=True)
                    
                if output.returncode != 0 or output.stdout == "":
                    raise RuntimeError(
                        f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                        f"STDOUT: {output.stdout}\nSTDERR: {output.stderr}"
                    )
                node_results = self._process_wrapped_results(output.stdout)

            elif external_measurements:
                ext = max(external_measurements, key=lambda m: m.priority)
                # temp_results = {} # Should be a dict of each run's results

                # Get measurement's wrap command
                # If it is able to function as a replacement wrapper, dont set backend in new cmd
                # If not, set everything to how it was is new cmd
                # Use the same script logic just in case
                # Process the existing wrapped results just like above
                # Send additional results to measurement to process

                with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", dir=self.output_dir) as f:
                    measurement_array = self._get_measurements_for_cli([m for m in self.measurements if m.name != ext.name])
                    script = f"#!/bin/bash\nsustainabench run benchmark -w {self.workload.name} {' '.join(measurement_array)} -c {str(self.config_filepath)} -b {self.backend.name} -np {str(self.backend.node_processors)} -p {str(self.backend.num_processors)} -o {self.output_dir} -nof\n"
                    f.write(script)
                    f.flush()
                    
                    cmd = ext.get_wrap_command(self.backend.name, self.backend.node_processors) + [
                        "--",
                        "bash", f.name
                    ]

                    output = subprocess.run(cmd, capture_output=True, text=True)

                if output.returncode != 0 or output.stdout == "":
                    raise RuntimeError(
                        f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                        f"STDOUT: {output.stdout}\nSTDERR: {output.stderr}"
                    )
                node_results = self._process_wrapped_results(output.stdout)
                nodeids = [noderes.node_id for noderes in node_results]
                ext_results = ext.process_results(output.stdout, nodeids)

                node_results = self.backend.add_result(node_results, ext_results)
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
    
    # Function that turns a list of measurement objects back into subprocess runnable args list
    def _get_measurements_for_cli(self, measurements) -> list[str]:
        measurement_filelist = [
            (m.name, getattr(m, "file", None))
            for m in measurements
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

        return measurement_array

    def get_measurements(self):
        return self.measurements

    def get_workload(self):
        return self.workload

    def get_runs(self):
        return self.runs