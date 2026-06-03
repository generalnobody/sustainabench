from typing import Annotated
import typer
from pathlib import Path
import json
import os
from datetime import datetime
from sustainabench.core.runner import BenchmarkRunner
from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.core.backends import BACKENDS

app = typer.Typer()

def _is_main_process(wrapped):
    rank = ( # Should cover most MPI rank env variables.
        os.getenv("OMPI_COMM_WORLD_RANK")
        or os.getenv("PMI_RANK")
        or os.getenv("SLURM_PROCID")
    )

    if rank is None or str(rank) == "0" or wrapped:
        return True
    else:
        return False


@app.command()
def benchmark(
    workload: Annotated[str, typer.Option(..., "--workload", "-w", help="The workload to run (from 'workloads/')")],
    measurement_names: Annotated[list[str], typer.Option(..., "--measure", "-m", help="Which measurements to conduct while executing the workload (multiple allowed)")],
    runs: Annotated[int, typer.Option(..., "--runs", "-r", help="How many times to run the same benchmark")] = 1,
    config_file: Annotated[Path, typer.Option(..., "--config", "-c", help="Path to the config file for the workload. Only supports YAML/JSON files")] = Path(""),
    backend: Annotated[str, typer.Option(..., "--backend", "-b", help="Which backend to use")] = "local",
    node_processors: Annotated[int, typer.Option(..., "--node-processors", "-np", help="Number of nodes that the MPI backend (or backend with similar situation) uses. Not used with local backend, use --processors/-p then. When using this, normal --processors/-p describes how many local threads are used per node.")] = 1,
    hostfile: Annotated[Path | None, typer.Option(..., "--hostfile", "-hf", help="Hostfile used by the MPI backend (or similar backends).")] = None,
    processors: Annotated[int, typer.Option(..., "--processors", "-p", help="How many processors to use (when applicable)")] = 1,
    output_dir: Annotated[Path, typer.Option(..., "--output", "-o", help="Benchmark output directory")] = Path("./experiments/raw/"),
    output_filename: Annotated[str, typer.Option(..., "--output-filename", "-of", help="Which specific filename to use within the output directory. Note: meant only for internal child runs, so is hidden from the help menu.", hidden=True)] = "", # Might be removable, check this
    wrapped_execution: Annotated[bool, typer.Option(..., "--wrapped", "-we", help="Whether the execution (only works for external workloads and only if they support it) has already been wrapped by another 'sustainabench run benchmark ...' (should not be used manually)", hidden=True)] = False,
    no_output_file: Annotated[bool, typer.Option(..., "--no-output-file", "-nof", help="Do not output output to a file and instead only to stdout.", hidden=True)] = False,
    silent: Annotated[bool, typer.Option(..., "-s", "--silent", help="If selected, will not show the final benchmarking output. Useful for less clutter in cmd windows.")] = False
):
    """Command used to run a benchmark"""
    print(f"Running workload: {workload}")

    backend_cls = BACKENDS[backend]
    backend_instance = backend_cls(num_processors=processors, node_processors=node_processors, hostfile=hostfile)

    runner = BenchmarkRunner(
        workload_name=workload,
        config_filepath=config_file,
        measurement_names=measurement_names,
        runs=runs,
        backend=backend_instance,
        output_dir=output_dir,
        wrapped_execution=wrapped_execution
    )

    results = runner.run()

    if results is not None and _is_main_process(wrapped_execution):
        results_dict = results.model_dump()

        if not silent:
            print("Results:")
            print(json.dumps(results_dict, indent=4))

        if no_output_file:
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        if output_filename != "" and not output_filename.endswith(".json"): # Internally, always ends with .json. However, if users figure this one out, ensure it ends with .json by always appending .json
                output_filename = f"{output_filename}.json"
        filename = f"{workload}__{backend}__{'-'.join(measurement.name for measurement in runner.get_measurements())}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.json" if output_filename == "" else output_filename
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

    if backends:
        print("[bold]Available Backends:[/bold]")
        for k in BACKENDS:
            print(f" - {k}")
