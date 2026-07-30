from statistics import mean, stdev
import pandas as pd
from handle_results import load_results

from sustainabench.schemas.results.benchmark import BenchmarkResult

rome_files = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/rome/experiments/merged/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/rome/experiments/merged/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/rome/experiments/merged/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/merged/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/merged/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/rome/experiments/merged/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/merged/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/merged/hpcg_4nodes.json",
    },
}

genoa_files = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/merged/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/merged/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/merged/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/merged/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/merged/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/merged/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/merged/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/merged/hpcg_4nodes.json",
    },
}

a100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/merged/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/merged/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpl_4gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/merged/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpcg_4gpus.json",
        "8 GPUs": "scripts/snellius/gpu/a100/experiments/merged/nv-hpcg_8gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/a100/experiments/merged/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/a100/experiments/merged/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/a100/experiments/merged/vllm_4gpus.json",
    }
}

h100_files = {
    "gpu-burn": {
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/gpu-burn.json"
    },
    "Nvidia STREAM": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/merged/nv-stream.json"
    },
    "Nvidia HPL": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/merged/nv-hpl_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpl_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpl_4gpus.json",
        "8 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpl_8gpus.json",
    },
    "Nvidia HPCG": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/merged/nv-hpcg_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpcg_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpcg_4gpus.json",
        "8 GPUs": "scripts/snellius/gpu/h100/experiments/merged/nv-hpcg_8gpus.json",
    },
    "vllm": {
        "1 GPU": "scripts/snellius/gpu/h100/experiments/merged/vllm_1gpu.json",
        "2 GPUs": "scripts/snellius/gpu/h100/experiments/merged/vllm_2gpus.json",
        "4 GPUs": "scripts/snellius/gpu/h100/experiments/merged/vllm_4gpus.json",
    }
}


def extract_run_energies(result: BenchmarkResult) -> tuple[list[float], list[float]]:
    """
    Returns one CPU (RAPL) and perf energy value per run.

    If a run contains multiple nodes, their energies are summed first.
    """

    cpu_runs = []
    perf_runs = []

    for run in result.results.values():
        cpu_total = 0.0
        perf_total = 0.0
        found = False

        for node in run:

            cpu = node.metrics.get("cpu_energy")
            perf = node.metrics.get("perf_energy")

            if cpu is None or perf is None:
                continue

            cpu_total += cpu["energy"]["j"]
            perf_total += perf["joules"]
            found = True

        if found:
            cpu_runs.append(cpu_total)
            perf_runs.append(perf_total)

    return cpu_runs, perf_runs


def summarize(result: BenchmarkResult) -> dict:
    cpu, perf = extract_run_energies(result)

    if not cpu:
        return {
            "samples": 0,
            "cpu_mean_J": None,
            "perf_mean_J": None,
            "overhead_J": None,
            "overhead_pct": None,
        }

    cpu_mean = mean(cpu)
    perf_mean = mean(perf)

    overhead_J = perf_mean - cpu_mean
    overhead_pct = 100 * overhead_J / cpu_mean

    run_overheads = [
        100 * (p - c) / c
        for c, p in zip(cpu, perf)
    ]

    return {
        "samples": len(cpu),

        "cpu_mean_J": cpu_mean,
        "cpu_std_J": stdev(cpu) if len(cpu) > 1 else 0.0,

        "perf_mean_J": perf_mean,
        "perf_std_J": stdev(perf) if len(perf) > 1 else 0.0,

        "overhead_J": overhead_J,
        "overhead_pct": overhead_pct,

        # statistics of the per-run overhead
        "overhead_pct_mean": mean(run_overheads),
        "overhead_pct_std": stdev(run_overheads) if len(run_overheads) > 1 else 0.0,
        "overhead_pct_min": min(run_overheads),
        "overhead_pct_max": max(run_overheads),
    }


def analyze(arch: str, files: dict):
    results = load_results(files)

    rows = []

    for benchmark, configs in results.items():
        for configuration, result in configs.items():
            rows.append(
                {
                    "arch": arch,
                    "benchmark": benchmark,
                    "configuration": configuration,
                    **summarize(result),
                }
            )

    return rows


rows = []
rows += analyze("Rome", rome_files)
rows += analyze("Genoa", genoa_files)
rows += analyze("A100", a100_files)
rows += analyze("H100", h100_files)

df = pd.DataFrame(rows)

pd.set_option("display.float_format", "{:.3f}".format)

print(df[["arch", "benchmark", "configuration", "cpu_mean_J", "perf_mean_J", "overhead_J", "overhead_pct"]])
df.to_csv("experiments/plots/supplementary/perf_energy_overhead.csv", index=False)