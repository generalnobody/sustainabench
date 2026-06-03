from sustainabench.measurement.base import  ExternalMeasurement, register_measurement
from sustainabench.utils.system_info import get_mpi_ranks, get_node_metadata

import csv
from pydantic import BaseModel

@register_measurement
class LikwidMeasurement(ExternalMeasurement):
    name = "likwid"
    poll_interval = None
    scope = "node"
    require_file = True
    rank_priority = 100
    within_wrapper = True
    replace_wrapper = []
    wrapper_conflicts = ["perf"]

    class MeasurementParams(BaseModel):
        flags: list[list[str]]

    def get_wrap_command(self, backend_name, node_processors):
        if not self.config:
            raise RuntimeError(f"Measurement {self.name} expects a config to be provided")
        
        self.backend_name = backend_name
        
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

    def process_results(self, output: str, nodeids: list[str]) -> dict:
        parsed = self._parse_likwid_output(output.splitlines())

        metadata = get_node_metadata()
        rank, local_rank = get_mpi_ranks()
        node_id = f"{metadata['hostname']}:{rank}:{local_rank}" if local_rank is not None else f"{metadata['hostname']}:{rank}" if rank is not None else "local"
        result = {
            node_id: {
                self.name: parsed
            }
        }
        return result
