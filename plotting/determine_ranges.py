from pathlib import Path
import pandas as pd

def determine_metric_ranges(stats_files, padding=0.05):
    dfs = [pd.read_csv(f) for f in stats_files]
    stats_df = pd.concat(dfs, ignore_index=True)

    metric_ranges = {}

    for metric, group in stats_df.groupby("metric"):
        ymax = group["ci95_upper"].max()
        ymin = group["ci95_lower"].min()
        # add some headroom
        ymax *= (1 + padding)
        ymin *= (1 - padding)

        metric_ranges[metric] = (ymin, ymax)

    return metric_ranges
