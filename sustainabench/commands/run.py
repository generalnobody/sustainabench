import typer
from rich import print
from sustainabench.core.runner import BenchmarkRunner
from sustainabench.workloads.cpu import CPUMatrixWorkload
from sustainabench.measurement.base import TimeMeasurement
from sustainabench.indicators.carbon import CarbonIndicator

app = typer.Typer()


@app.command()
def benchmark(workload: str = "cpu"):
    print(f"Running workload: {workload}")

    if workload == "cpu":
        runner = BenchmarkRunner(
            workload=CPUMatrixWorkload(),
            measurements=[TimeMeasurement()],
            indicators=[CarbonIndicator(400)]
        )

        raw, indicators = runner.execute()

        print(raw)
        print(indicators)
    else:
        print(f"Workload '{workload}' not recognized")
