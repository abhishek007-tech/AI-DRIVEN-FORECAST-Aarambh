import pandas as pd
from app.config import REQUIRED_COLUMNS


def validate_schema(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    if df.empty:
        raise ValueError('Dataset is empty')
    if (df['lead_day'] < 1).any():
        raise ValueError('lead_day must be >= 1')
    if not df['date'].notna().all():
        raise ValueError('date contains missing values')
