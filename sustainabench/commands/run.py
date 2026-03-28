import typer
from rich import print
from sustainabench.core.runner import BenchmarkRunner
from sustainabench.measurement.base import TimeMeasurement
from sustainabench.indicators.carbon import CarbonIndicator

app = typer.Typer()

@app.command()
def benchmark(workload: str):
    print(f"Running workload: {workload}")

    runner = BenchmarkRunner(
        workload_name=workload,
        measurements=[TimeMeasurement()],
        indicators=[CarbonIndicator(400)]
    )

    raw, indicators = runner.run()

    print(raw)
    print(indicators)
