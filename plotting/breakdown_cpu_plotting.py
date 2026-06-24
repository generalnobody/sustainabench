from pathlib import Path
from sustainabench.schemas.results.metrics_dict import MetricsDict
import yaml
import pandas as pd
from stats import compute_statistics
from plot import build_dataframe, plot_structure
from handle_results import load_results, get_results
from energy_breakdown import (
    extract_cpu_node_breakdown
)

from breakdown_stats import (
    compute_breakdown_statistics
)

from breakdown_plot import (
    plot_energy_breakdown_grouped
)

OUTPUT_DIR = Path("experiments/plots/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(Path("configs/metrics/metrics_dict.yaml")) as f:
    raw_metrics_dict = yaml.safe_load(f)
metrics_dict = MetricsDict.model_validate(raw_metrics_dict)

metrics_to_plot = [
    "all-carbon",
    "energy-to-solution",
    "carbon-per-second"
]

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

rome_merged = load_results(rome_files)
genoa_merged = load_results(genoa_files)



rome_breakdown = extract_cpu_node_breakdown(
    rome_merged,
    "rome"
)

genoa_breakdown = extract_cpu_node_breakdown(
    genoa_merged,
    "genoa"
)

breakdown_df = pd.concat(
    [
        rome_breakdown,
        genoa_breakdown
    ],
    ignore_index=True
)

breakdown_stats = (
    compute_breakdown_statistics(
        breakdown_df
    )
)

breakdown_stats.to_csv(
    OUTPUT_DIR /
    "cpu_energy_breakdown.csv",
    index=False
)
plot_energy_breakdown_grouped(
    breakdown_stats,
    "rome",
    OUTPUT_DIR,
    config_order=[
        "1 node",
        "2 nodes",
        "4 nodes"
    ]
)

plot_energy_breakdown_grouped(
    breakdown_stats,
    "genoa",
    OUTPUT_DIR,
    config_order=[
        "1 node",
        "2 nodes",
        "4 nodes"
    ]
)