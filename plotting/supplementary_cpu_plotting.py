from handle_results import load_results, extract_memory_df
from breakdown_plot import plot_memory_grouped 
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("experiments/plots/supplementary/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

rome_files = {
    "stress-ng": {
        "1 node": "scripts/snellius/supplementary/cpu/rome/experiments/raw/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/supplementary/cpu/rome/experiments/raw/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/supplementary/cpu/rome/experiments/raw/hpl_1node.json",
        "2 nodes": "scripts/snellius/supplementary/cpu/rome/experiments/raw/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/supplementary/cpu/rome/experiments/raw/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/supplementary/cpu/rome/experiments/raw/hpcg_1node.json",
        "2 nodes": "scripts/snellius/supplementary/cpu/rome/experiments/raw/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/supplementary/cpu/rome/experiments/raw/hpcg_4nodes.json",
    },
}

genoa_files = {
    "stress-ng": {
        "1 node": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/stress-ng.json"
    },
    "STREAM": {
        "1 node": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/stream.json"
    },
    "HPL": {
        "1 node": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/hpl_1node.json",
        "2 nodes": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/hpl_2nodes.json",
        "4 nodes": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/hpl_4nodes.json",
    },
    "HPCG": {
        "1 node": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/hpcg_1node.json",
        "2 nodes": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/hpcg_2nodes.json",
        "4 nodes": "scripts/snellius/supplementary/cpu/genoa/experiments/raw/hpcg_4nodes.json",
    },
}

rome_results = load_results(rome_files)
genoa_results = load_results(genoa_files)

memory_df = pd.concat(
    [
        extract_memory_df(rome_results, "rome"),
        extract_memory_df(genoa_results, "genoa"),
    ],
    ignore_index=True,
)

config_order = [
    "1 node",
    "2 nodes",
    "4 nodes",
]

plot_memory_grouped(
    memory_df,
    arch_name="rome",
    output_dir=OUTPUT_DIR,
    config_order=config_order,
)

plot_memory_grouped(
    memory_df,
    arch_name="genoa",
    output_dir=OUTPUT_DIR,
    config_order=config_order,
)
print(f"Plots saved to: {OUTPUT_DIR.resolve()}")