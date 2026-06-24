import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np


def plot_energy_breakdown_grouped(
    stats_df,
    arch_name,
    output_dir,
    config_order=None,
):
    sns.set_theme(
        style="whitegrid",
        context="talk",
    )

    arch_df = stats_df[
        stats_df["arch"] == arch_name
    ]

    benchmarks = arch_df["benchmark"].unique()

    if config_order:
        configs = [
            c
            for c in config_order
            if c in arch_df["config"].unique()
        ]
    else:
        configs = arch_df["config"].unique()

    components = arch_df["component"].unique()

    # benchmark/config/component -> mean
    pivot = (
        arch_df
        .pivot_table(
            index=["benchmark", "config"],
            columns="component",
            values="mean",
            fill_value=0,
        )
    )

    group_gap = 1.0

    bar_positions = []
    bar_labels = []
    benchmark_centers = {}

    current_y = 0

    for benchmark in benchmarks:

        start = current_y

        for config in configs:

            bar_positions.append(current_y)
            bar_labels.append(config)

            current_y += 1

        end = current_y - 1

        benchmark_centers[benchmark] = (
            start + end
        ) / 2

        current_y += group_gap
    height = 0.8 / len(configs)

    fig, ax = plt.subplots(
        figsize=(12, max(6, len(benchmarks) * 0.6))
    )

    colors = sns.color_palette(
        "Set2",
        len(components)
    )

    for benchmark in benchmarks:

        try:
            sub = (
                pivot
                .loc[benchmark]
                .reindex(configs)
                .fillna(0)
            )
        except KeyError:
            continue

        start_idx = (
            list(benchmark_centers.keys())
            .index(benchmark)
            * len(configs)
        )

        ypos = bar_positions[
            start_idx:
            start_idx + len(configs)
        ]

        left = np.zeros(len(configs))

        for j, component in enumerate(components):

            values = sub[component].values

            ax.barh(
                ypos,
                values,
                left=left,
                height=0.8,
                color=colors[j],
                label=component if benchmark == benchmarks[0] else None,
            )

            left += values

    ax.set_yticks(bar_positions)
    ax.set_yticklabels(bar_labels)

    xmin, xmax = ax.get_xlim()
    benchmark_labels_x = xmin + 0.05 * (xmax - xmin)

    for benchmark, center in benchmark_centers.items():

        ax.text(
            benchmark_labels_x,                  # x-position
            center + 1.3,       # slightly above group
            benchmark,
            fontweight="bold",
            fontsize=13,
            ha="left",
            va="bottom",
        )

    current_y = 0

    # ax.set_xscale("log")
    ax.set_xlabel("Energy (J)")
    ax.set_ylabel("Benchmark")

    title = f"{arch_name.upper()} Energy Breakdown"
    ax.set_title(title, pad=40)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=len(components),
        frameon=False,
    )

    plt.tight_layout()

    plt.savefig(
        output_dir /
        f"{arch_name}_energy_breakdown_grouped.pdf"
    )

    plt.savefig(
        output_dir /
        f"{arch_name}_energy_breakdown_grouped.jpg"
    )

    plt.close()