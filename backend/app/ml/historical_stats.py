import pandas as pd

from app.config import BUST_THRESHOLD


class HistoricalStatsStore:
    """Leakage-safe lookup of statistics available before a forecast date."""

    def __init__(self, df: pd.DataFrame, bust_threshold: float = BUST_THRESHOLD):
        required = {'date', 'region', 'lead_day', 'forecast_rainfall', 'observed_rainfall'}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f'Missing historical-stat columns: {sorted(missing)}')
        data = df.copy()
        data['date'] = pd.to_datetime(data['date'])
        data['absolute_error'] = (data['forecast_rainfall'] - data['observed_rainfall']).abs()
        data['bust'] = (data['absolute_error'] >= bust_threshold).astype(int)
        self.df = data.sort_values('date').reset_index(drop=True)
        self.bust_threshold = bust_threshold

    def for_prediction(self, forecast_date, region: str, lead_day: int) -> dict:
        date = pd.Timestamp(forecast_date)
        prior = self.df[self.df['date'] < date]
        exact = prior[(prior['region'].astype(str) == str(region)) & (prior['lead_day'] == lead_day)]
        lead = prior[prior['lead_day'] == lead_day]
        pool = exact if not exact.empty else lead
        if pool.empty:
            return {'historical_mean_abs_error': 0.0, 'historical_bust_frequency': 0.0, 'history_records': 0}
        return {
            'historical_mean_abs_error': float(pool['absolute_error'].mean()),
            'historical_bust_frequency': float(pool['bust'].mean()),
            'history_records': int(len(pool)),
        }

    def summary(self) -> dict:
        return {
            'records': int(len(self.df)),
            'date_start': str(self.df['date'].min().date()),
            'date_end': str(self.df['date'].max().date()),
            'regions': sorted(self.df['region'].astype(str).unique().tolist()),
            'lead_days': sorted(self.df['lead_day'].astype(int).unique().tolist()),
        }
