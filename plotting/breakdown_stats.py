from scipy import stats
import numpy as np


def compute_breakdown_statistics(df):
    summary = (
        df.groupby(
            [
                "arch",
                "benchmark",
                "config",
                "component"
            ],
            sort=False
        )["value"]
        .agg(
            mean="mean",
            std="std",
            n="count"
        )
        .reset_index()
    )

    summary["sem"] = summary["std"] / np.sqrt(summary["n"])

    summary["t_value"] = summary["n"].apply(
        lambda n: stats.t.ppf(0.975, n - 1)
        if n > 1 else np.nan
    )

    summary["ci95"] = summary["sem"] * summary["t_value"]

    return summary