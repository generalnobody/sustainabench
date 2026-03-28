from typing import Annotated
import typer
from rich import print
from sustainabench.core.runner import BenchmarkRunner
# from sustainabench.measurement.base import TimeMeasurement
# from sustainabench.indicators.carbon import CarbonIndicator

app = typer.Typer()

@app.command()
def benchmark(
    workload: Annotated[str, typer.Argument(help="The workload to run (from 'workloads/')")],
    measurement_names: Annotated[list[str], typer.Option(..., "--measure", "-m", help="Which measurements to conduct while executing the workload")],
    indicator_names: Annotated[list[str], typer.Option(..., "--indicator", "-i", help="Which indicators to derive from the raw measurements after the workload has been completed")]
):
    print(f"Running workload: {workload}")

    runner = BenchmarkRunner(
        workload_name=workload,
        # measurements=[TimeMeasurement()],
        # indicators=[CarbonIndicator(400)]
        measurement_names=measurement_names,
        indicator_names=indicator_names
    )

    raw, indicators = runner.run()

    print(raw)
    print(indicators)
