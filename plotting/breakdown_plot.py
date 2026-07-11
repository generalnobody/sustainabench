import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib.ticker import MaxNLocator

# Old plotting logic, the one used for the presentation.
# def plot_energy_breakdown_grouped(
#     stats_df,
#     arch_name,
#     output_dir,
#     config_order=None,
# ):
#     sns.set_theme(
#         style="whitegrid",
#         context="talk",
#     )

#     arch_df = stats_df[
#         stats_df["arch"] == arch_name
#     ]

#     benchmarks = arch_df["benchmark"].unique()

#     if config_order:
#         configs = [
#             c
#             for c in config_order
#             if c in arch_df["config"].unique()
#         ]
#     else:
#         configs = arch_df["config"].unique()

#     components = arch_df["component"].unique()

#     # benchmark/config/component -> mean
#     pivot = (
#         arch_df
#         .pivot_table(
#             index=["benchmark", "config"],
#             columns="component",
#             values="mean",
#             fill_value=0,
#         )
#     )

#     group_gap = 1.0

#     bar_positions = []
#     bar_labels = []
#     benchmark_centers = {}

#     current_y = 0

#     for benchmark in benchmarks:

#         start = current_y

#         for config in configs:

#             bar_positions.append(current_y)
#             bar_labels.append(config)

#             current_y += 1

#         end = current_y - 1

#         benchmark_centers[benchmark] = (
#             start + end
#         ) / 2

#         current_y += group_gap
#     height = 0.8 / len(configs)

#     fig, ax = plt.subplots(
#         figsize=(12, max(6, len(benchmarks) * 0.6))
#     )

#     colors = sns.color_palette(
#         "Set2",
#         len(components)
#     )

#     for benchmark in benchmarks:

#         try:
#             sub = (
#                 pivot
#                 .loc[benchmark]
#                 .reindex(configs)
#                 .fillna(0)
#             )
#         except KeyError:
#             continue

#         start_idx = (
#             list(benchmark_centers.keys())
#             .index(benchmark)
#             * len(configs)
#         )

#         ypos = bar_positions[
#             start_idx:
#             start_idx + len(configs)
#         ]

#         left = np.zeros(len(configs))

#         for j, component in enumerate(components):

#             values = sub[component].values

#             ax.barh(
#                 ypos,
#                 values,
#                 left=left,
#                 height=0.8,
#                 color=colors[j],
#                 label=component if benchmark == benchmarks[0] else None,
#             )

#             left += values

#     ax.set_yticks(bar_positions)
#     ax.yaxis.grid(False)
#     ax.set_yticklabels(bar_labels)

#     xmin, xmax = ax.get_xlim()
#     benchmark_labels_x = xmin + 0.01 * (xmax - xmin)

#     for benchmark, center in benchmark_centers.items():

#         ax.text(
#             benchmark_labels_x,                  # x-position
#             center + 1.3,       # slightly above group
#             benchmark,
#             fontweight="bold",
#             fontsize=13,
#             ha="left",
#             va="bottom",
#         )

#     current_y = 0

#     # ax.set_xscale("log")
#     ax.set_xlabel("Joule")
#     ax.set_ylabel("Benchmark")

#     title = f"{arch_name.upper()} Energy Breakdown"
#     ax.set_title(title, pad=40)

#     ax.legend(
#         loc="upper center",
#         bbox_to_anchor=(0.5, 1.15),
#         ncol=len(components),
#         frameon=False,
#     )

#     plt.tight_layout()

#     plt.savefig(
#         output_dir /
#         f"{arch_name}_energy_breakdown_grouped.pdf"
#     )

#     plt.savefig(
#         output_dir /
#         f"{arch_name}_energy_breakdown_grouped.jpg"
#     )

#     plt.close()

def plot_energy_breakdown_grouped(
    stats_df,
    arch_name,
    output_dir,
    config_order=None,
):

    sns.set_theme(style="whitegrid", context="talk")

    arch_df = stats_df[stats_df["arch"] == arch_name]

    benchmarks = arch_df["benchmark"].unique()

    if config_order:
        configs = [
            c for c in config_order
            if c in arch_df["config"].unique()
        ]
    else:
        configs = arch_df["config"].unique()

    pivot = arch_df.pivot_table(
        index=["benchmark", "config"],
        columns="component",
        values="mean",
        fill_value=0,
    )

    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(benchmarks),
        figsize=(3 * len(benchmarks), 7),
        sharey=False,
    )

    if len(benchmarks) == 1:
        axes = [axes]

    components = pivot.columns
    colors = sns.color_palette("Set2", len(components))

    for ax, benchmark in zip(axes, benchmarks):

        try:
            sub = (
                pivot.loc[benchmark]
                .reindex(configs)
                .fillna(0)
            )
        except KeyError:
            ax.set_visible(False)
            continue

        xpos = np.arange(len(configs))
        bottom = np.zeros(len(configs))

        for i, component in enumerate(components):

            values = sub[component].values

            ax.bar(
                xpos,
                values,
                bottom=bottom,
                width=0.6,
                color=colors[i],
                label=component,
            )

            bottom += values

        ax.set_xticks(xpos)
        ax.set_xticklabels(
            configs,
            rotation=45,
            ha="right",
        )

        ax.set_title(benchmark)

        if ax is axes[0]:
            ax.set_ylabel("Energy (J)")
        else:
            ax.set_ylabel("")

        ax.grid(axis="x", visible=False)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    handles, labels = axes[0].get_legend_handles_labels()

    ncols = min(5, len(components))

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.94),
        ncol=ncols,
        frameon=False,
    )

    fig.suptitle(f"{arch_name.upper()} Energy Breakdown")

    plt.tight_layout(rect=(0, 0, 1, 0.92))

    plt.savefig(
        output_dir /
        f"{arch_name}_energy_breakdown_grouped.pdf"
    )

    plt.savefig(
        output_dir /
        f"{arch_name}_energy_breakdown_grouped.jpg"
    )

    plt.close()


def plot_memory_grouped(
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

    pivot = (
        arch_df
        .pivot_table(
            index=["benchmark", "config"],
            columns="node",
            values="mean",
            fill_value=0,
        )
    )

    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(benchmarks),
        figsize=(3 * len(benchmarks), 6),
        sharey=False,
    )

    if len(benchmarks) == 1:
        axes = [axes]

    nodes = pivot.columns
    colors = sns.color_palette("Set2", len(nodes))

    for ax, benchmark in zip(axes, benchmarks):

        try:
            sub = (
                pivot
                .loc[benchmark]
                .reindex(configs)
                .fillna(0)
            )
        except KeyError:
            ax.set_visible(False)
            continue

        xpos = np.arange(len(configs))

        bottom = np.zeros(len(configs))

        for i, node in enumerate(nodes):
            values = sub[node].values

            ax.bar(
                xpos,
                values,
                bottom=bottom,
                width=0.6,
                color=colors[i],
                label=node,
            )

            bottom += values

        ax.set_xticks(xpos)
        ax.set_xticklabels(configs, rotation=45, ha="right")
        ax.set_title(benchmark)
        # ax.set_ylabel("Average RSS (MB)")
        if ax is axes[0]:
            ax.set_ylabel("Average RSS (MiB)")
        else:
            ax.set_ylabel("")
        ax.grid(axis="x", visible=False)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    handles, labels = axes[0].get_legend_handles_labels()

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.9),
        ncol=len(nodes),
        frameon=False,
    )

    fig.suptitle(f"{arch_name.upper()} Average Memory Usage")
    plt.tight_layout(rect=(0, 0, 1, 0.92))

    plt.savefig(
        output_dir /
        f"{arch_name}_memory_grouped.pdf"
    )

    plt.savefig(
        output_dir /
        f"{arch_name}_memory_grouped.jpg"
    )

    plt.close()


def plot_gpu_memory_grouped(
    stats_df,
    arch_name,
    output_dir,
    config_order=None,
):

    sns.set_theme(style="whitegrid", context="talk")

    arch_df = stats_df[stats_df["arch"] == arch_name]

    benchmarks = arch_df["benchmark"].unique()

    if config_order:
        configs = [c for c in config_order if c in arch_df["config"].unique()]
    else:
        configs = arch_df["config"].unique()

    # pivot: benchmark/config × gpu → mean memory
    pivot = arch_df.pivot_table(
        index=["benchmark", "config"],
        columns="gpu",
        values="mean",
        fill_value=0,
    )

    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(benchmarks),
        figsize=(3 * len(benchmarks), 7),
        sharey=False,
    )

    if len(benchmarks) == 1:
        axes = [axes]

    gpu_cols = pivot.columns
    colors = sns.color_palette("Set2", len(gpu_cols))

    for ax, benchmark in zip(axes, benchmarks):

        try:
            sub = (
                pivot.loc[benchmark]
                .reindex(configs)
                .fillna(0)
            )
        except KeyError:
            ax.set_visible(False)
            continue

        xpos = np.arange(len(configs))
        bottom = np.zeros(len(configs))

        for i, gpu in enumerate(gpu_cols):
            values = sub[gpu].values

            ax.bar(
                xpos,
                values,
                bottom=bottom,
                width=0.6,
                color=colors[i],
                label=gpu,
            )

            bottom += values

        ax.set_xticks(xpos)
        ax.set_xticklabels(configs, rotation=45, ha="right")
        ax.set_title(benchmark)

        if ax is axes[0]:
            ax.set_ylabel("Average GPU Memory (MiB)")
        else:
            ax.set_ylabel("")

        ax.grid(axis="x", visible=False)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    handles, labels = axes[0].get_legend_handles_labels()

    ncols = min(4, len(gpu_cols))
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.94),
        ncol=ncols,
        frameon=False,
    )

    fig.suptitle(f"{arch_name.upper()} Average GPU Memory Usage")
    plt.tight_layout(rect=(0, 0, 1, 0.92))

    plt.savefig(output_dir / f"{arch_name}_gpu_memory_grouped.pdf")
    plt.savefig(output_dir / f"{arch_name}_gpu_memory_grouped.jpg")
    plt.close()