from datetime import date
import pandas as pd
from fastapi import APIRouter, HTTPException
from app.config import DEMO_DATA_PATH
from app.ml.predict import load_artifacts, predict_one
from app.ml.historical_stats import HistoricalStatsStore
from app.data.loader import DemoDataLoader

router = APIRouter()


def _load_demo():
    if not DEMO_DATA_PATH.exists():
        raise HTTPException(404, 'Demo data not found. Run generate_demo_data.py')
    return DemoDataLoader(DEMO_DATA_PATH).load()


@router.get('/regions')
def regions():
    df = _load_demo()
    return {'regions': sorted(df['region'].astype(str).unique().tolist())}


@router.get('/forecast/{forecast_date}')
def forecast(forecast_date: date, lead_day: int = 1, region: str | None = None):
    df = _load_demo()
    df = df[df['date'].dt.date == forecast_date]
    df = df[df['lead_day'] == lead_day]
    if region:
        df = df[df['region'].astype(str) == region]
    if df.empty:
        raise HTTPException(404, 'No forecast records for the selected filters')
    try:
        load_artifacts()
    except FileNotFoundError as e:
        raise HTTPException(503, str(e))
    store = HistoricalStatsStore(_load_demo())
    out = []
    for _, r in df.iterrows():
        payload = {k: r[k] for k in ['date', 'latitude', 'longitude', 'lead_day', 'forecast_rainfall',
                                      'temperature', 'humidity', 'pressure', 'wind_speed', 'ensemble_spread', 'region']}
        stats = store.for_prediction(r['date'], str(r['region']), int(r['lead_day']))
        p = predict_one(payload, stats)
        out.append({**payload, **p})
    return {
        'data_mode': 'DEMO/SYNTHETIC',
        'warning': 'DEMO DATA - NOT REAL WEATHER FORECAST PERFORMANCE',
        'forecasts': out,
    }
