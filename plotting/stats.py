from scipy import stats
import numpy as np

def compute_statistics(df):
    """
    Computes descriptive statistics for each
    benchmark/configuration pair.
    """

    summary = (
        df.groupby(
            ["arch", "metric", "benchmark", "config"],
            sort=False
        )["value"]
        .agg(
            mean="mean",
            median="median",
            std="std",
            min="min",
            max="max",
            n="count",
        )
        .reset_index()
    )

    # Standard error
    summary["sem"] = summary["std"] / np.sqrt(summary["n"])

    # Student-t 95% CI
    summary["t_value"] = summary["n"].apply(
        lambda n: stats.t.ppf(0.975, n - 1) if n > 1 else np.nan
    )

    summary["ci95"] = summary["sem"] * summary["t_value"]
    summary["ci95_lower"] = summary["mean"] - summary["ci95"]
    summary["ci95_upper"] = summary["mean"] + summary["ci95"]

    # Relative variability
    summary["cv_percent"] = (
        100 * summary["std"] / summary["mean"]
    )

    return summary