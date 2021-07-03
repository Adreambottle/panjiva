"""
This file is a scaler file
"""
import numpy as np

def three_sigma(series, n:int):
    mean = series.mean()
    std = series.std()
    max_range = mean + n * std
    min_range = mean - n * std
    return np.clip(series, min_range, max_range)

def percentile(series, min= 0.025, max= 0.975):
    series = series.sort_values()
    q = series.quantile([min, max])
    return np.clip(series, q.iloc[0], q.iloc[-1])

def mad(series, n=3):
    median = series.quantile(0.5)
    diff_median = ((series - median).abs()).quantile(0.5)
    max_range = median + n * diff_median
    min_range = median - n * diff_median
    return np.clip(series, min_range, max_range)
