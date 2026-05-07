from typing import Annotated
import typer
from rich import print
from pathlib import Path
import json
import yaml
import tempfile
from datetime import datetime
from sustainabench.core.runner import BenchmarkRunner
from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.core.backends import BACKENDS
from sustainabench.measurement.base import ExternalMeasurement
from sustainabench.core.models import BenchmarkResult, NodeResult

app = typer.Typer()

def _is_main_process():
    try:
        from mpi4py import MPI
        return MPI.COMM_WORLD.Get_rank() == 0
    except:
        return True

@app.command()
def benchmark(
    workload: Annotated[str, typer.Option(..., "--workload", "-w", help="The workload to run (from 'workloads/')")],
    measurement_names: Annotated[list[str], typer.Option(..., "--measure", "-m", help="Which measurements to conduct while executing the workload (multiple allowed)")],
    runs: Annotated[int, typer.Option(..., "--runs", "-r", help="How many times to run the same benchmark")] = 1,
    config_file: Annotated[Path, typer.Option(..., "--config", "-c", help="Path to the config file for the workload. Only supports YAML/JSON files")] = Path(""),
    backend: Annotated[str, typer.Option(..., "--backend", "-b", help="Which backend to use")] = "local",
    node_processors: Annotated[int, typer.Option(..., "--node-processors", "-np", help="Number of nodes that the MPI backend (or backend with similar situation) uses. Not used with local backend, use --processors/-p then. When using this, normal --processors/-p describes how many local threads are used per node.")] = 1,
    processors: Annotated[int, typer.Option(..., "--processors", "-p", help="How many processors to use (when applicable)")] = 1,
    output_dir: Annotated[Path, typer.Option(..., "--output", "-o", help="Benchmark output directory")] = Path("./experiments/raw/"),
    output_filename: Annotated[str, typer.Option(..., "--output-filename", "-of", help="Which specific filename to use within the output directory. Note: meant only for internal child runs, so is hidden from the help menu.", hidden=True)] = ""
):
    """Command used to run a benchmark"""
    print(f"Running workload: {workload}")

    backend_cls = BACKENDS[backend]
    backend_instance = backend_cls(num_processors=processors)

    workload_cfg = None
    if config_file != Path(""):
        with open(config_file) as f:
            workload_cfg = yaml.safe_load(f)

    if workload_cfg is not None:
        if "workload" not in workload_cfg:
            raise ValueError("Missing 'workload' key in config")
        if "name" not in workload_cfg["workload"]:
            raise ValueError("Missing 'name' key under 'workload' key in config")
        if workload_cfg["workload"]["name"] != workload:
            raise ValueError(f"Workload's name does not match. Expected '{workload}', found: '{workload_cfg['workload']['name']}'")
        if "params" not in workload_cfg["workload"]:
            raise ValueError("Missing 'params' key under 'workload' key in config")

    runner = BenchmarkRunner(
        workload_name=workload,
        workload_cfg=workload_cfg,
        measurement_names=measurement_names,
        runs=runs,
        backend=backend_instance,
    )

    measurement_instances = runner.get_measurements()
    external_measurements = [
        m for m in measurement_instances if isinstance(m, ExternalMeasurement) 
    ]

    if external_measurements:
        ext = max(external_measurements, key=lambda m: m.priority)
        temp_results = {} # Should be a dict of each run's results

        for i in range(runs):
            with tempfile.TemporaryDirectory(dir=output_dir) as tmpdir:
                temp_output_filename = f"{ext.name}.json"

                ext.execute_cli_passthrough(
                    workload=workload,
                    measurements=measurement_instances,
                    runs=1, # When launching a child process, always use 1 run. This keeps implementation simple
                    config_file=config_file,
                    backend=backend,
                    node_processors=node_processors,
                    processors=processors,
                    output_dir=tmpdir,
                    output_filename=temp_output_filename,
                )

                child_results = None
                child_file = Path(tmpdir, temp_output_filename)
                with child_file.open("r", encoding="utf-8") as f:
                    child_results = json.load(f)
                if not child_results:
                    raise ValueError(f"File {child_file} could not be loaded")
                
                res = [NodeResult(**item) for item in child_results["results"]["run0"]]   # Always run0 since child always does just 1 run
                nodeids = [noderes.node_id for noderes in res] # These are expected to match external measurements' node ids. If not match, treated as global. If parser has local backend, treat all results as falling under node_id local.
                index = {r.node_id: r for r in res}

                # temp_results[f"run{i}"] = ext.result()
                ext_results = ext.result_json(nodeids)
                for node_id, metrics in ext_results.items():
                    if node_id in index:
                        index[node_id].metrics.update(metrics)
                    else:
                        res.append(NodeResult(node_id=node_id, metrics=metrics, metadata={}))
                temp_results[f"run{i}"] = res
        results = BenchmarkResult(workload, backend, temp_results, {})
    else:
        results = runner.run()
    
    if results is not None and _is_main_process():
        results_dict = results.to_dict()

        print("Results:")
        print(json.dumps(results_dict, indent=4))

        output_dir.mkdir(parents=True, exist_ok=True)
        if output_filename != "" and not output_filename.endswith(".json"): # Internally, always ends with .json. However, if users figure this one out, ensure it ends with .json by always appending .json
                output_filename = f"{output_filename}.json"
        filename = f"{workload}__{'-'.join(measurement.name for measurement in runner.get_measurements())}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.json" if output_filename == "" else output_filename
        output_file = output_dir / filename

        with output_file.open("w", encoding="utf-8") as f: # If other benchmarks can export to this format, then further analysis can be done using 'sustainabench generate' on third-party results
            json.dump(results_dict, f, indent=4, ensure_ascii=False)
            print("Outputted results to:", output_file)


@app.command()
def benchmark_list(
    workload: Annotated[bool, typer.Option(..., "--workload", "-w", help="View available workloads")] = False,
    measurement_names: Annotated[bool, typer.Option(..., "--measure", "-m", help="View available measurements")]  = False,
    # indicator_names: Annotated[bool, typer.Option(..., "--indicator", "-i", help="View available indicators")] = False,
    backends: Annotated[bool, typer.Option(..., "--backend", "-b", help="View available backends")] = False
):
    """Command to see benchmark command options. Lists all if none are selected."""
    if not workload and not measurement_names and not backends:
        workload = measurement_names = backends = True

    if workload:
        print("[bold]Available Workloads:[/bold]")
        for k in WORKLOADS:
            print(f" - {k}")

    if measurement_names:
        print("[bold]Available Measurements:[/bold]")
        for k in MEASUREMENTS:
            print(f" - {k}")

    # if indicator_names:
    #     print("[bold]Available Indicators:[/bold]")
    #     for k in INDICATORS:
    #         print(f" - {k}")

    if backends:
        print("[bold]Available Backends:[/bold]")
        for k in BACKENDS:
            print(f" - {k}")
