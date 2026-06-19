from pathlib import Path
from sustainabench.schemas.results.metrics_dict import MetricsDict
import yaml
import pandas as pd
from stats import compute_statistics
from plot import build_dataframe, plot_structure
from handle_results import load_results, get_results

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
        "1 node": "scripts/snellius/cpu/rome/experiments/results/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/rome/experiments/results/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/rome/experiments/results/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/rome/experiments/results/hpcg_4nodes.json",
    },
}

genoa_files = {
    "stress-ng": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/hpl_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/cpu/genoa/experiments/results/hpcg_1node.json",
        "2 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/cpu/genoa/experiments/results/hpcg_4nodes.json",
    },
}

rome_results = load_results(rome_files)
genoa_results = load_results(genoa_files)

# rome_total_carbon, rome_total_energy, rome_carbon_per_second = get_results(rome_results, metrics_dict)
# genoa_total_carbon, genoa_total_energy, genoa_carbon_per_second = get_results(genoa_results, metrics_dict)

# ----------------------------
# BUILD DATASETS
# ----------------------------
# rome_df = build_dataframe(rome_total_carbon, rome_total_energy, "rome")
# genoa_df = build_dataframe(genoa_total_carbon, genoa_total_energy, "genoa")

rome_metrics = get_results(
    rome_results,
    metrics_dict,
    metrics_to_extract=metrics_to_plot
)

genoa_metrics = get_results(
    genoa_results,
    metrics_dict,
    metrics_to_extract=metrics_to_plot
)

rome_df = build_dataframe(
    rome_metrics,
    "rome"
)

genoa_df = build_dataframe(
    genoa_metrics,
    "genoa"
)

df = pd.concat([rome_df, genoa_df], ignore_index=True)


# ----------------------------
# CALCULATE STATS & ENERATE PLOTS
# ----------------------------

stats_df = compute_statistics(df)

stats_df.to_csv(
    OUTPUT_DIR / "cpu_benchmark_statistics.csv",
    index=False
)

# print(stats_df)
print(f"Stats saved to: {OUTPUT_DIR.resolve()}.cpu_benchmark_statistics.csv")


config_order = ["1 node", "2 nodes", "4 nodes"]
plot_structure(stats_df, "rome", OUTPUT_DIR, config_order=config_order, metrics_to_plot=metrics_to_plot)
plot_structure(stats_df, "genoa", OUTPUT_DIR, config_order=config_order, metrics_to_plot=metrics_to_plot)

print(f"Plots saved to: {OUTPUT_DIR.resolve()}")
