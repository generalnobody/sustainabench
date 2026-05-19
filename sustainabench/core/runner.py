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
from sustainabench.core.backends.base import ExecutionBackend

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
        self.backend: ExecutionBackend = backend
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
    
    def _generate_external_measurement_scripts(self, external_measurements: list[ExternalMeasurement], workload_wrap_command: str | None, sustainabench_command: str):
        script_header = "#!/bin/bash"
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".sh",
            dir=self.output_dir,
            delete=False
        )
        tmp.write(f"{script_header}\n{sustainabench_command}\n")
        tmp.flush()
        script_files = [tmp]

        if workload_wrap_command is not None:
            tmp = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".sh",
                dir=self.output_dir,
                delete=False
            )
            tmp.write(f"{script_header}\n{workload_wrap_command} -- bash {script_files[-1].name}\n")
            tmp.flush()
            script_files.append(tmp)
        
        for m in external_measurements:
            tmp = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".sh",
                dir=self.output_dir,
                delete=False
            )
            cmd = " ".join(m.get_wrap_command(self.backend.name, self.backend.node_processors))
            tmp.write(f"{script_header}\n{cmd} -- bash {script_files[-1].name}\n")
            tmp.flush()
            script_files.append(tmp)

        return script_files

    def run(self) -> BenchmarkResult:
        """Function that runs the benchmark on the correct backend (only internal measurements)"""
        results = {}

        workload_wrap = isinstance(self.workload, ExternalWorkload) and self.workload.require_wrapping and not self.wrapped_execution
        workload_wrap_command = None
        external_measurements = sorted(
            (
                m for m in self.measurements 
                if isinstance(m, ExternalMeasurement) 
            ),
            key=lambda m: m.rank_priority,
            # reverse=True
        )
        if external_measurements:
            for m1 in external_measurements: # Check conflicts
                for m2 in external_measurements:
                    if m1.name in m2.wrapper_conflicts:
                        raise ValueError(f"Measurements {m1.name} and {m2.name} are incompatible. Please select only one of these and run again.")
                    
            if workload_wrap:
                wrappable_measurements = sorted(
                    (
                        m for m in external_measurements
                        if self.backend.name in m.replace_wrapper
                    ),
                    key=lambda m: m.wrapper_priority,
                    reverse=True
                )
                workload_wrap_command = max(wrappable_measurements, key=lambda m: m.wrapper_priority)
                external_measurements.remove(workload_wrap_command)
        elif workload_wrap: # No external measurements, but workload does need to be wrapped
            workload_wrap_command = self.backend.get_wrap_command()
        # Check if any external measurements conflict (add variable for this in ExternalMeasurement)
        # Get all external measurements that can wrap the workload if applicable
        # Recursively generate all wrapped commands
        # Make temp files not delete automatically, handle this later
        # Select a single wrap command (either from measurement or from workload), that continues into the runs loop

        # TODO: continue with implementation in runs range


        # ext = max(external_measurements, key=lambda m: m.rank_priority) if external_measurements else None
        # Check that proper ext was selected. Prioritize higher priority, but prioritize workload wrapper override above all else
        # measurement_array = self._get_measurements_for_cli([m for m in self.measurements if not ext or m.name != ext.name])
        measurement_array = self._get_measurements_for_cli([m for m in self.measurements if not isinstance(m, ExternalMeasurement)]) # Select all measurements that are not external (so, internal)

        for i in range(self.runs):
            if workload_wrap:
                sustainabench_cmd = f"sustainabench run benchmark -w {self.workload.name} {' '.join(measurement_array)} -c {str(self.config_filepath)} -p {str(self.backend.num_processors)} -we -nof"
                wrap_cmd = " ".join(self.backend.get_wrap_command())
                script_files = self._generate_external_measurement_scripts(external_measurements=external_measurements, workload_wrap_command=wrap_cmd, sustainabench_command=sustainabench_cmd)
                cmd = [
                    "bash", script_files[-1].name
                ]
                output = subprocess.run(cmd, capture_output=True, text=True)

                # with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", dir=self.output_dir) as f: # Technically not necessary with local/mpi backend, but you never know when some backend might be annoying like likwid-mpirun
                #     script = f"#!/bin/bash\nsustainabench run benchmark -w {self.workload.name} {' '.join(measurement_array)} -c {str(self.config_filepath)} -p {str(self.backend.num_processors)} -we -nof\n"
                #     f.write(script)
                #     f.flush()

                #     # If external measurement can replace backend's wrap command, then use external measurement's
                #     # Maybe make this override priority?

                #     cmd = self.backend.get_wrap_command() + [
                #         "--",
                #         "bash", f.name
                #     ]

                #     output = subprocess.run(cmd, capture_output=True, text=True)
                    
                if output.returncode != 0 or output.stdout == "":
                    raise RuntimeError(
                        f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                        f"STDOUT: {output.stdout}\nSTDERR: {output.stderr}"
                    )
                node_results = self._process_wrapped_results(output.stdout)

            elif external_measurements:
                sustainabench_cmd = f"sustainabench run benchmark -w {self.workload.name} {' '.join(measurement_array)} -c {str(self.config_filepath)} -b {self.backend.name} -np {str(self.backend.node_processors)} -p {str(self.backend.num_processors)} -o {self.output_dir} -nof"
                script_files = self._generate_external_measurement_scripts(external_measurements=external_measurements, workload_wrap_command=None, sustainabench_command=sustainabench_cmd)
                cmd = [
                    "bash", script_files[-1].name
                ]
                output = subprocess.run(cmd, capture_output=True, text=True)

                # with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", dir=self.output_dir) as f:
                #     script = f"#!/bin/bash\nsustainabench run benchmark -w {self.workload.name} {' '.join(measurement_array)} -c {str(self.config_filepath)} -b {self.backend.name} -np {str(self.backend.node_processors)} -p {str(self.backend.num_processors)} -o {self.output_dir} -nof\n"
                #     f.write(script)
                #     f.flush()
                    
                #     cmd = ext.get_wrap_command(self.backend.name, self.backend.node_processors) + [
                #         "--",
                #         "bash", f.name
                #     ]

                #     output = subprocess.run(cmd, capture_output=True, text=True)

                if output.returncode != 0 or output.stdout == "":
                    raise RuntimeError(
                        f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                        f"STDOUT: {output.stdout}\nSTDERR: {output.stderr}"
                    )
                node_results = self._process_wrapped_results(output.stdout)
                nodeids = [noderes.node_id for noderes in node_results]
                # ext_results = ext.process_results(output.stdout, nodeids)
                ext_results = [
                    ext.process_results(output.stdout, nodeids)
                    for ext in external_measurements
                ]

                # node_results = self.backend.add_result(node_results, ext_results)
                for res in ext_results:
                    node_results = self.backend.add_result(node_results, res)
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