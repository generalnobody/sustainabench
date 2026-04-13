from typing import Annotated
import typer
from rich import print
from pathlib import Path
import json
from datetime import datetime
from sustainabench.core.runner import BenchmarkRunner
from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.core.backends import BACKENDS

app = typer.Typer()

@app.command()
def benchmark(
    workload: Annotated[str, typer.Option(..., "--workload", "-w", help="The workload to run (from 'workloads/')")],
    measurement_names: Annotated[list[str], typer.Option(..., "--measure", "-m", help="Which measurements to conduct while executing the workload (multiple allowed)")],
    config_file: Annotated[Path, typer.Option(..., "--config", "-c", help="Path to the config file for the benchmark")] = Path(""),
    backend: Annotated[str, typer.Option(..., "--backend", "-b", help="Which backend to use")] = "local",
    processors: Annotated[int, typer.Option(..., "--processors", "-p", help="How many processors to use (when applicable)")] = 1,
    output_dir: Annotated[Path, typer.Option(..., "--output", "-o", help="Benchmark output directory")] = Path("./experiments/raw/") 
):
    """Command used to run a benchmark"""
    print(f"Running workload: {workload}")

    backend_cls = BACKENDS[backend]
    backend_instance = backend_cls(num_processors=processors)

    if "all" in measurement_names:
        measurement_names = list(MEASUREMENTS.keys())

    runner = BenchmarkRunner(
        workload_name=workload,
        measurement_names=measurement_names,
        backend=backend_instance
    )

    results = runner.run()
    results_dict = results.to_dict()

    print("Results:")
    print(json.dumps(results_dict, indent=4))

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{workload}__{'-'.join(measurement_names)}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        print(" - all")
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
