import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ----------------------------
# FLATTEN FUNCTION
# ----------------------------
def flatten_results(data, arch_name, metric_name):
    rows = []

    for benchmark, configs in data.items():
        for config, values in configs.items():
            for v in values:
                rows.append({
                    "arch": arch_name,
                    "benchmark": benchmark,
                    "config": config,
                    "metric": metric_name,
                    "value": v
                })

    return rows


# ----------------------------
# DATAFRAME BUILDER
# ----------------------------
# def build_dataframe(total_carbon, total_energy, arch_name):
#     rows = []
#     rows += flatten_results(total_carbon, arch_name, "carbon")
#     rows += flatten_results(total_energy, arch_name, "energy")
#     return pd.DataFrame(rows)

def build_dataframe(all_metrics, arch_name):
    rows = []

    for metric_name, metric_data in all_metrics.items():
        rows += flatten_results(
            metric_data,
            arch_name,
            metric_name
        )

    return pd.DataFrame(rows)

def plot_structure(stats_df, arch_name, output_dir, config_order=None):
    sns.set_theme(style="whitegrid", context="talk")

    arch_df = stats_df[
        stats_df["arch"] == arch_name
    ]

    for metric in ["carbon", "energy"]:

        metric_df = arch_df[
            arch_df["metric"] == metric
        ]

        if metric_df.empty:
            continue

        benchmarks = metric_df["benchmark"].unique()
        if not config_order:
            configs = metric_df["config"].unique()
        else:
            configs = [c for c in config_order if c in metric_df["config"].unique()]

        x = np.arange(len(benchmarks))
        width = 0.8 / len(configs)

        plt.figure(figsize=(12, 6))
        ax = plt.gca()
        palette = sns.color_palette("Set2", len(configs))

        for i, config in enumerate(configs):
            sub = (
                metric_df[
                    metric_df["config"] == config
                ]
                .set_index("benchmark")
                .reindex(benchmarks)
                .reset_index()
            )

            xpos = (x + i * width - width * len(configs) / 2)

            ax.bar(
                xpos,
                sub["mean"],
                width=width,
                label=config,
                color=palette[i]
            )

            ax.errorbar(
                xpos,
                sub["mean"],
                yerr=sub["ci95"],
                fmt="none",
                ecolor="black",
                capsize=5,
                linewidth=1.5
            )

        ylabel_map = {
            "carbon": "gCO₂eq",
            "energy": "J",
            "carbon-per-second": "gCO₂eq/s"
        }

        ax.set_xticks(x)
        ax.set_xticklabels(benchmarks, rotation=20)
        ax.set_ylabel(ylabel_map.get(metric, metric))
        ax.set_xlabel("Benchmark")
        ax.set_yscale("log")

        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.15),
            ncol=len(configs),
            frameon=False
        )

        ax.set_title(
            f"{arch_name.upper()} - {metric.capitalize()}",
            pad=40
        )

        plt.tight_layout()
        plt.savefig(output_dir / f"{arch_name}_{metric}.pdf")
        plt.savefig(output_dir / f"{arch_name}_{metric}.eps")

        plt.close()