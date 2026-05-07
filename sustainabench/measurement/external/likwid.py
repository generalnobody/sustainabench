from sustainabench.measurement.base import  ExternalMeasurement, register_measurement
import yaml
import subprocess
import csv
import tempfile
import os
import stat
import io
import re

@register_measurement
class LikwidMeasurement(ExternalMeasurement):
    name = "likwid"
    poll_interval = None
    scope = "node"
    require_file = True
    priority = 100

    def __init__(self, filename: str):
        self.file = filename

    def execute_cli_passthrough(self, workload, measurements, runs, config_file, backend, node_processors, processors, output_dir, output_filename):
        self.backend = backend

        cfg = None
        with open(self.file) as f:
            cfg = yaml.safe_load(f)

        if cfg is not None:
            if "measurement" not in cfg:
                raise ValueError("Missing 'measurement' key in config")
            if "name" not in cfg["measurement"]:
                raise ValueError("Missing 'name' key under 'measurement' key in config")
            if cfg["measurement"]["name"] != self.name:
                raise ValueError(f"Measurement's name does not match. Expected '{self.name}', found: '{cfg['measurement']['name']}'")
            if "params" not in cfg["measurement"]:
                raise ValueError("Missing 'params' key under 'measurement' key in config")
            if "flags" not in cfg["measurement"]["params"]:
                raise ValueError("Missing 'flags' key under 'params' key in config")
            for flag in cfg["measurement"]["params"]["flags"]:
                if len(flag) != 2:
                    raise ValueError(f"Flag '{flag}' is incorrectly structured. Expected: [<flag>, <value>]")
                p, v = flag
                if not isinstance(p, str) or not (isinstance(v, str) or v is None):
                    raise ValueError(f"Flag parameters require first item to be a string and second item to be a string or null. Flag {flag} does not follow this")
            
            # self.cores = cfg["measurement"]["params"]["c"]
            # self.group = cfg["measurement"]["params"]["g"]
            self.likwid_params = [v for s in cfg["measurement"]["params"]["flags"] for v in s if v is not None]
            self.likwid_params += ["-O"] # Doesnt need to be added in likwid's yaml, since this one is required for output parsing.
        else:
            raise RuntimeError(f"Measurement {self.name} expects config to be provided.")

        # Decide which launcher to use. Depending on future backend functionality, might need to be changed
        if backend == "mpi":
            launcher = [
                "likwid-mpirun",
                "-np", str(node_processors),
            ]
        else:
            launcher = [
                "likwid-perfctr",
            ]

        # cmd = launcher + self.likwid_params + [
        #     "--",
        #     "sustainabench",
        #     "run",
        #     "benchmark",
        #     "-w", workload,
        # ] # Excludes measurements for now

        
        # + [
        #     "--",
        #     "sustainabench",
        #     "run",
        #     "benchmark",
        #     "-w", workload,
        # ] # Excludes measurements for now

        # Measurements should be a dict (passed from runner.run()), add them dynamically, or add 'none' if no other measurement present
        # filtered_measurements = []
        # for m in measurements:
        #     if m.name != self.name:
        #         filtered_measurements.append((m.name, getattr(m, "file", None)))
        # # filtered_measurements = {m.name: m.file for m in measurements if m.name != self.name} # Exclude current measurement
        # if len(filtered_measurements) > 0:
        #     for measurement, filename in filtered_measurements:
        #         if filename:
        #             cmd.extend(["-m", f"{measurement}={filename}"])
        #         else:
        #             cmd.extend(["-m", measurement])
        # else:
        #     cmd.extend(["-m", "none"])

        # cmd.extend([ # Add the rest of the cmd params
        #     "-r", str(runs),
        #     "-c", str(config_file),
        #     "-b", backend,
        #     "-p", str(processors),
        #     "-o", output_dir,
        #     "-of", output_filename
        # ])


        with tempfile.NamedTemporaryFile(mode="w+", suffix=".sh", dir=output_dir) as f:
            # TODO: launch sustainabench from a temp script file, such that likwid-mpirun doesnt mess up args
            filtered_measurements = []
            for m in measurements:
                if m.name != self.name:
                    filtered_measurements.append((m.name, getattr(m, "file", None)))

            measurement_array = []
            if len(filtered_measurements) > 0:
                for measurement, filename in filtered_measurements:
                    if filename: 
                        measurement_array.extend(["-m", f"{measurement}={filename}"])
                    else:
                        measurement_array.extend(["-m", measurement])
            else:
                measurement_array.extend(["-m", "none"])

            script = f"""#!/bin/bash\n
            sustainabench run benchmark -w {workload} {" ".join(measurement_array)} -r {str(runs)} -c {str(config_file)} -b {backend} -np {str(node_processors)} -p {str(processors)} -o {output_dir} -of {output_filename}\n
            """
            f.write(script)
            f.flush()
            cmd = launcher + self.likwid_params  + [
                "--",
                "bash", f.name
            ]

            output = subprocess.run(cmd, capture_output=True, text=True)

        if output.returncode != 0 or output.stdout == "":
            raise RuntimeError(
                f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\nSTDERR: {output.stderr}"
            )
        
        self.results = output.stdout.splitlines()

    def _parse_likwid_output(self, results):
        csvdata = None
        for i in range(len(results)):
            if results[i].startswith("STRUCT") or results[i].startswith("TABLE"):
                csvdata = results[i:]
                break

        if not csvdata:
            raise ValueError("Expected likwid output, not found")
        reader = csv.reader(csvdata)

        structs = []
        tables = []
        current_tag = None
        for row in reader:
            if not row:
                continue

            tag = row[0]

            if tag == "STRUCT":
                structs.append([row])
                current_tag = tag
            elif tag == "TABLE":
                tables.append([row])
                current_tag = tag
            else:
                if current_tag == "STRUCT":
                    structs[-1].append(row)
                elif current_tag == "TABLE":
                    tables[-1].append(row)

        results = {}
        for struct in structs:
            struct_def = [x for x in struct[0][1:] if x != ""] # Select top-level row, remove STRUCT keyword from it and remove all empty items
            struct_key = struct_def[0]
            results[struct_key] = {}
            length = len(struct_def) # Get number of struct_def items
            for i in range(1, len(struct)):
                r = [x for x in struct[i] if x != ""] # Select row and remove empty strings
                results[struct_key].update({r[0]: r[1:]})

        for table in tables:
            table_def = [x for x in table[0][1:] if x != ""]
            table_key = table_def[0]
            table_group = table_def[1]
            if not table_group in results:
                results[table_group] = {}
            results[table_group].update({table_key: {}})

            headers = [x for x in table[1] if x != ""] # Select all table headers and remove all empty items
            for i, header in enumerate(headers):
                if i == 0:
                    continue

                results[table_group][table_key][header] = {}

                for row in table[2:]:
                    results[table_group][table_key][header].update({row[0]: row[i]})

        return results
    
    def _split_results(self, data, nodeids):
        node_results = {node_id: {} for node_id in nodeids}
        global_results = {}

        def insert_nested(target, path, key, value):
            """Insert value at target[path...][key]"""
            d = target
            for p in path:
                d = d.setdefault(p, {})
            d[key] = value

        def recurse(current, path):
            if not isinstance(current, dict):
                return current

            new_global = {}

            for key, value in current.items():
                if key in nodeids and isinstance(value, dict):
                    # Insert FULL structure into the correct node
                    insert_nested(node_results[key], path, key, value)
                else:
                    processed = recurse(value, path + [key])
                    if processed is not None:
                        new_global[key] = processed

            return new_global

        global_results = recurse(data, [])

        return node_results, global_results

    def result_json(self, nodeids: list[str]) -> dict:
        parsed = self._parse_likwid_output(self.results)
        result = {}

        if self.backend == "local":
            result = {
                "local": {
                    self.name: parsed
                }
            }
        elif self.backend == "mpi":
            node_results, global_results = self._split_results(parsed, nodeids)
            result = {
                **{
                    node_id: {"likwid": node_result}
                    for node_id, node_result in node_results.items()
                },
                "global": {
                    "likwid": global_results
                }
            }
        else:
            raise ValueError(f"Backend {self.backend} not yet implemented in external measurement {self.name} parser. Please implement first.")

        return result
