import numpy as np
import pandas as pd
from app.config import BUST_THRESHOLD

BASE_FEATURES = [
    'forecast_rainfall', 'lead_day', 'temperature', 'humidity', 'pressure',
    'wind_speed', 'ensemble_spread', 'latitude', 'longitude',
    'historical_mean_abs_error', 'historical_bust_frequency', 'region_code'
]


def add_bust_label(df: pd.DataFrame, threshold: float = BUST_THRESHOLD) -> pd.DataFrame:
    out = df.copy()
    out['absolute_error'] = (out['forecast_rainfall'] - out['observed_rainfall']).abs()
    out['bust'] = (out['absolute_error'] >= threshold).astype(int)
    return out


def add_historical_features(df: pd.DataFrame, threshold: float = BUST_THRESHOLD) -> pd.DataFrame:
    """For each row, statistics use only observations from earlier dates."""
    out = df.sort_values('date').copy()
    out['absolute_error'] = (out['forecast_rainfall'] - out['observed_rainfall']).abs()
    out['_bust_tmp'] = (out['absolute_error'] >= threshold).astype(int)
    group = out.groupby(['region', 'lead_day'], sort=False)
    out['historical_mean_abs_error'] = group['absolute_error'].transform(
        lambda s: s.shift(1).expanding(min_periods=1).mean()
    ).fillna(0.0)
    out['historical_bust_frequency'] = group['_bust_tmp'].transform(
        lambda s: s.shift(1).expanding(min_periods=1).mean()
    ).fillna(0.0)
    return out.drop(columns=['_bust_tmp'])


def prepare_features(df: pd.DataFrame, fit_regions=None, threshold: float = BUST_THRESHOLD) -> tuple[pd.DataFrame, list[str], dict]:
    out = add_historical_features(df.copy(), threshold)
    regions = sorted(out['region'].astype(str).unique()) if fit_regions is None else list(fit_regions)
    region_map = {name: i for i, name in enumerate(regions)}
    out['region_code'] = out['region'].astype(str).map(region_map).fillna(-1).astype(float)
    for col in BASE_FEATURES:
        out[col] = pd.to_numeric(out[col], errors='coerce')
    return out[BASE_FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0.0), BASE_FEATURES, region_map
