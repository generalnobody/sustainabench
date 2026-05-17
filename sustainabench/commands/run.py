from typing import Annotated
import typer
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
from sustainabench.schemas.results.benchmark import BenchmarkResult, NodeResult

app = typer.Typer()

def _is_main_process():
    return True # Rethink how to check this. Really annoying when running wrapped workloads as it cannot init MPI
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
    node_processors: Annotated[int | None, typer.Option(..., "--node-processors", "-np", help="Number of nodes that the MPI backend (or backend with similar situation) uses. Not used with local backend, use --processors/-p then. When using this, normal --processors/-p describes how many local threads are used per node.")] = None,
    hostfile: Annotated[Path | None, typer.Option(..., "--hostfile", "-hf", help="Hostfile used by the MPI backend (or similar backends).")] = None,
    processors: Annotated[int, typer.Option(..., "--processors", "-p", help="How many processors to use (when applicable)")] = 1,
    output_dir: Annotated[Path, typer.Option(..., "--output", "-o", help="Benchmark output directory")] = Path("./experiments/raw/"),
    output_filename: Annotated[str, typer.Option(..., "--output-filename", "-of", help="Which specific filename to use within the output directory. Note: meant only for internal child runs, so is hidden from the help menu.", hidden=True)] = "",
    wrapped_execution: Annotated[bool, typer.Option(..., "--wrapped", "-we", help="Whether the execution (only works for external workloads and only if they support it) has already been wrapped by another 'sustainabench run benchmark ...' (should not be used manually)", hidden=True)] = False,
    no_output_file: Annotated[bool, typer.Option(..., "--no-output-file", "-nof", help="Do not output output to a file and instead only to stdout.", hidden=True)] = False
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
        wrapped_execution=wrapped_execution
    )

    measurement_instances = runner.get_measurements()
    external_measurements = [
        m for m in measurement_instances if isinstance(m, ExternalMeasurement) 
    ]

    ###########################################################################################
    # TODO: major rework
    # Fix MPI: try to figure out how to have measurements & workloads run in parallel. Probably requires something like side-by-side MPI or smth
    # If using MPI, and an external workload, then external measurements should be run with MPI-specific commands (likwid-mpirun vs likwid-perfctr)
    # Main sustainabench should never initialize MPI. even import mpi4py initializes it and fucks up
    # For external workloads, maybe to make backend requirements clear, add something like 'allowed_backends = ["mpi"]'. If this is not set, then just allow all
    # 
    #
    #
    ############################################################################################

    # Maybe a good approach is to have sustainabench run benchmark perform a subprocess.popen on another sustainabench run benchmark, never load mpi4py and just have the local benchmark runs output their benchmark runs to stdout (and maybe a tempfile)
    # 
    # Flow:
    # sustainabench run benchmark -w hpl -np 4 ...
    # this does sustainabench run benchmark -w hpl and gets the results? no but that would cause infinite loop never calling hpl...
    # maybe run sustainabench run workload?? new command mayh fix the issue?
    # internally, maybe always set wrapper=true for hpl workload (and hpcg), then one command can be used? since other logic is the same


    # OR: handle external workload logic from runner/from here. putting it into the workloads seems annoying...
    # Also, for measurements like likwid, that have mpi wrappers, mauybe provide some way to cleanly run the program with those instead of with normal mpirun?

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

                raw = None
                child_file = Path(tmpdir, temp_output_filename)
                with child_file.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                if not raw:
                    raise ValueError(f"File {child_file} could not be loaded")
                
                child_results = BenchmarkResult.model_validate(raw)
                res = child_results.results["run0"] # Always run0 since child always does just 1 run
                nodeids = [noderes.node_id for noderes in res] # These are expected to match external measurements' node ids. If not match, treated as global. If parser has local backend, treat all results as falling under node_id local.
                index = {r.node_id: r for r in res}

                ext_results = ext.result_json(nodeids)
                for node_id, metrics in ext_results.items():
                    if node_id in index:
                        index[node_id].metrics.update(metrics)
                    else:
                        res.append(NodeResult(node_id=node_id, metrics=metrics, metadata={}))
                temp_results[f"run{i}"] = res
        results = BenchmarkResult(workload=workload, backend=backend, results=temp_results, metadata={})
    else:
        results = runner.run()
    
    if results is not None and _is_main_process():
        # results_dict = results.to_dict()
        results_dict = results.model_dump()

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

    # if indicator_names:
    #     print("[bold]Available Indicators:[/bold]")
    #     for k in INDICATORS:
    #         print(f" - {k}")

    if backends:
        print("[bold]Available Backends:[/bold]")
        for k in BACKENDS:
            print(f" - {k}")


# @app.command(hidden=True)
# def benchmark_worker(
#     workload: Annotated[str, typer.Option(..., "--workload", "-w", help="The workload to run (from 'workloads/')")],
#     measurement_names: Annotated[list[str], typer.Option(..., "--measure", "-m", help="Which measurements to conduct while executing the workload (multiple allowed)")],
#     processors: Annotated[int, typer.Option(..., "--processors", "-p", help="How many processors to use (when applicable)")] = 1,
#     config_file: Annotated[Path, typer.Option(..., "--config", "-c", help="Path to the config file for the workload. Only supports YAML/JSON files")] = Path("")
# ):
#     """Local worker command, used for workloads that require wrapping (such as HPL/HPCG)"""
#     backend_cls = BACKENDS["local"]
#     backend_instance = backend_cls(num_processors=processors, node_processors=1)

#     workload_cfg = None
#     if config_file != Path(""):
#         tmp = None
#         with open(config_file) as f:
#             tmp = yaml.safe_load(f)
#         workload_cfg = WorkloadConfig.model_validate(tmp)

#     runner = BenchmarkRunner(
#         workload_name=workload,
#         workload_cfg=workload_cfg,
#         measurement_names=measurement_names,
#         runs=1,
#         backend=backend_instance,
#     )

#     measurement_instances = runner.get_measurements()
#     external_measurements = [
#         m for m in measurement_instances if isinstance(m, ExternalMeasurement) 
#     ]
