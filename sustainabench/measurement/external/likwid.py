from sustainabench.measurement.base import  ExternalMeasurement, register_measurement
import subprocess
import csv
import tempfile
from pydantic import BaseModel

@register_measurement
class LikwidMeasurement(ExternalMeasurement):
    name = "likwid"
    poll_interval = None
    scope = "node"
    require_file = True
    rank_priority = 100
    wrapper_priority = 100
    replace_wrapper = ["mpi"]
    wrapper_conflicts = ["perf"]

    class MeasurementParams(BaseModel):
        flags: list[list[str]]

    def get_wrap_command(self, backend_name, node_processors):
        if not self.config:
            raise RuntimeError(f"Measurement {self.name} expects a config to be provided")
        
        self.backend_name = backend_name
        if backend_name == "mpi":
            launcher = [
                "likwid-mpirun",
                "-np", str(node_processors),
            ]
        else:
            launcher = [
                "likwid-perfctr",
            ]
        
        likwid_flags = self.MeasurementParams.model_validate(self.config.measurement.params)
        likwid_params = [item for flag in likwid_flags.flags for item in flag] + ["-O"] # '-O' doesnt need to be added in likwid's yaml, since this one is required for output parsing.

        return launcher + likwid_params

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
    
    def _collapse_nodeid_layer(self, obj, nodeids):
        """
        Recursively removes dict layers where the dict only contains
        node IDs as keys.

        Example:
        {
            "node031:0:0": {...}
        }

        becomes:
        {...}
        """

        if not isinstance(obj, dict):
            return obj

        keys = set(obj.keys())

        # if this dict is purely a node-id wrapper layer
        if keys and keys.issubset(set(nodeids)):
            # usually one entry for local node results
            if len(obj) == 1:
                return self._collapse_nodeid_layer(
                    next(iter(obj.values())),
                    nodeids
                )

        return {
            k: self._collapse_nodeid_layer(v, nodeids)
            for k, v in obj.items()
        }

    def process_results(self, output: str, nodeids: list[str]) -> dict:
        parsed = self._parse_likwid_output(output.splitlines())
        result = {}

        if self.backend_name == "local":
            result = {
                "local": {
                    self.name: parsed
                }
            }
        elif self.backend_name == "mpi":
            node_results, global_results = self._split_results(parsed, nodeids)

            node_results = {
                node_id: self._collapse_nodeid_layer(node_result, nodeids)
                for node_id, node_result in node_results.items()
            }

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
            raise ValueError(f"Backend '{self.backend_name}' not yet implemented in external measurement '{self.name}' parser. Please implement first.")

        return result
