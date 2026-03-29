from typing import Annotated
import typer
from rich import print
from sustainabench.core.runner import BenchmarkRunner
from sustainabench.workloads import WORKLOADS
from sustainabench.measurement import MEASUREMENTS
from sustainabench.indicators import INDICATORS

app = typer.Typer()

@app.command()
def benchmark(
    workload: Annotated[str, typer.Option(..., "--workload", "-w", help="The workload to run (from 'workloads/')")],
    measurement_names: Annotated[list[str], typer.Option(..., "--measure", "-m", help="Which measurements to conduct while executing the workload (multiple allowed)")],
    indicator_names: Annotated[list[str], typer.Option(..., "--indicator", "-i", help="Which indicators to derive from the raw measurements after the workload has been completed (multiple allowed)")]
):
    print(f"Running workload: {workload}")

    runner = BenchmarkRunner(
        workload_name=workload,
        measurement_names=measurement_names,
        indicator_names=indicator_names
    )

    raw, indicators = runner.run()

    print(raw)
    print(indicators)


@app.command()
def benchmark_list(
    workload: Annotated[bool, typer.Option(..., "--workload", "-w", help="View available workloads")] = False,
    measurement_names: Annotated[bool, typer.Option(..., "--measure", "-m", help="View available measurements")]  = False,
    indicator_names: Annotated[bool, typer.Option(..., "--indicator", "-i", help="View available indicators")] = False
):
    if workload:
        print("[bold]Available Workloads:[/bold]")
        for k in WORKLOADS:
            print(f" - {k}")

    if measurement_names:
        print("[bold]Available Measurements:[/bold]")
        for k in MEASUREMENTS:
            print(f" - {k}")

    if indicator_names:
        print("[bold]Available Indicators:[/bold]")
        for k in INDICATORS:
            print(f" - {k}")
