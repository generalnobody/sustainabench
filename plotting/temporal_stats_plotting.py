from __future__ import annotations

from collections import defaultdict
from typing import Dict
from sustainabench.schemas.results.benchmark import BenchmarkResult, NodeResult
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import json

import numpy as np
from scipy.stats import t

def summarize(df):
    # Remove NaNs and flatten to one vector
    values = df.to_numpy().ravel()
    values = values[~np.isnan(values)]

    n = len(values)
    mean = values.mean()
    std = values.std(ddof=1)

    sem = std / np.sqrt(n)
    ci = sem * t.ppf(0.975, n - 1)

    q1 = np.percentile(values, 25)
    median = np.median(values)
    q3 = np.percentile(values, 75)

    return {
        "n": n,
        "min": values.min(),
        "q1": q1,
        "median": median,
        "mean": mean,
        "q3": q3,
        "max": values.max(),
        "std": std,
        "ci95_lower": mean - ci,
        "ci95_upper": mean + ci,
    }

def collect_timeseries(benchmark_result: BenchmarkResult):
    """
    Returns two DataFrames:
        intensity_df
        output_df

    rows = dates
    cols = runs
    """

    intensity = defaultdict(dict)
    output = defaultdict(dict)

    run_idx = 0

    for run_name, node_results in benchmark_result.results.items():
        for node in node_results:

            ts = node.metrics.get("carbon_timeseries")
            if ts is None:
                continue

            intensity_ts = ts.get("daily_carbon_intensity", {})
            output_ts = ts.get("daily_carbon_output_g", {})

            run_label = f"{run_name}_{run_idx}"

            for date, value in intensity_ts.items():
                intensity[date][run_label] = value

            for date, value in output_ts.items():
                output[date][run_label] = value

            run_idx += 1

    intensity_df = pd.DataFrame.from_dict(intensity, orient="index")
    output_df = pd.DataFrame.from_dict(output, orient="index")

    intensity_df.index = pd.to_datetime(
        intensity_df.index,
        format="%Y_%m_%d",
    )
    output_df.index = pd.to_datetime(
        output_df.index,
        format="%Y_%m_%d",
    )

    intensity_df = intensity_df.sort_index()
    output_df = output_df.sort_index()

    return intensity_df, output_df

def compute_statistics(df: pd.DataFrame):
    n = df.count(axis=1)

    mean = df.mean(axis=1)
    std = df.std(axis=1)

    sem = std / n.pow(0.5)

    ci95 = sem * t.ppf(0.975, n - 1)

    return pd.DataFrame(
        {
            "mean": mean,
            "lower": mean - ci95,
            "upper": mean + ci95,
        }
    )

def plot_statistic(output_dir, stats, summary, ylabel, title, filename):
    sns.set_theme(style="whitegrid", context="talk")

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.vlines(
        stats.index,
        0,
        stats["mean"],
        lw=0.7,
        alpha=0.6,
    )

    ax.scatter(
        stats.index,
        stats["mean"],
        s=8,
        label=ylabel
    )

    ax.axhspan( # Interquartile range
        summary["q1"],
        summary["q3"],
        alpha=0.15,
        color="red",
        label="Interquartile range (Q1-Q3)",
    )

    ax.axhline( # Median
        summary["median"],
        linestyle=":",
        linewidth=1.5,
        color="red",
        label="Median (Q2)",
    )

    ax.axhline( # Mean
        summary["mean"],
        color="black",
        linestyle="--",
        linewidth=1.5,
        label="Yearly mean",
    )

    ax.set_title(title)
    ax.set_ylabel(ylabel)

    # monthly ticks
    import matplotlib.dates as mdates

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    fig.autofmt_xdate()

    ax.legend()

    plt.tight_layout()
    plt.savefig(output_dir / f"{filename}.pdf")
    plt.savefig(output_dir / f"{filename}.jpg")

def compute_monthly_statistics(df: pd.DataFrame):
    """
    Aggregate daily carbon intensity into monthly statistics.

    Returns a DataFrame indexed by month with:
        mean
        lower
        upper
    """
    monthly = []

    for month, month_df in df.groupby(pd.Grouper(freq="MS")):
        values = month_df.to_numpy().ravel()
        values = values[~np.isnan(values)]

        if len(values) == 0:
            continue

        n = len(values)
        mean = values.mean()
        std = values.std(ddof=1) if n > 1 else 0.0
        sem = std / np.sqrt(n) if n > 1 else 0.0
        ci95 = sem * t.ppf(0.975, n - 1) if n > 1 else 0.0

        monthly.append(
            {
                "month": month,
                "mean": mean,
                "lower": mean - ci95,
                "upper": mean + ci95,
            }
        )

    return pd.DataFrame(monthly).set_index("month")


filepath = Path("scripts/snellius/gpu/a100/experiments/results/gpu-burn.json")
OUTPUT_DIR = Path("experiments/plots/")

result_json = json.loads(filepath.read_text(encoding="utf-8"))

result = BenchmarkResult.model_validate(result_json)

intensity_df, output_df = collect_timeseries(result)

intensity_stats = compute_statistics(intensity_df)
output_stats = compute_statistics(output_df)

intensity_summary = summarize(intensity_df)
output_summary = summarize(output_df)

Path(OUTPUT_DIR / "carbon_stats.json").write_text(json.dumps({
    "workload": result.workload,
    "carbon_intensity": intensity_summary,
    "carbon_output": output_summary
}, indent=4), encoding="utf-8")

plot_statistic(
    OUTPUT_DIR,
    intensity_stats,
    intensity_summary,
    ylabel="Carbon intensity (gCO2eq/kWh)",
    title="Daily carbon intensity",
    filename="daily_carbon_intensity"
)

plot_statistic(
    OUTPUT_DIR,
    output_stats,
    output_summary,
    ylabel="Carbon output (gCO2eq)",
    title=f"Daily carbon output - {result.workload}",
    filename=f"{result.workload}-daily_carbon_output"
)

monthly_intensity_stats = compute_monthly_statistics(intensity_df.iloc[1:])
monthly_intensity_stats.to_csv(OUTPUT_DIR / "supplementary" / "monthly-carbon-intensity.csv", index=True)
