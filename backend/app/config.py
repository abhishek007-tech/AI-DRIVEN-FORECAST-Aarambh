import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
DEMO_DATA_PATH = DATA_DIR / 'demo' / 'weather_demo.csv'
MODELS_DIR = ROOT / 'models'
MODEL_PATH = MODELS_DIR / 'bust_model.joblib'
FEATURE_NAMES_PATH = MODELS_DIR / 'feature_names.json'
METADATA_PATH = MODELS_DIR / 'model_metadata.json'
METRICS_PATH = MODELS_DIR / 'metrics.json'

BUST_THRESHOLD = float(os.getenv('BUST_THRESHOLD', '20.0'))
HIGH_RISK_THRESHOLD = float(os.getenv('HIGH_RISK_THRESHOLD', '0.70'))
MODERATE_RISK_THRESHOLD = float(os.getenv('MODERATE_RISK_THRESHOLD', '0.40'))
RANDOM_STATE = 42
MODEL_VERSION = os.getenv('MODEL_VERSION', '0.2.0-mvp')

REQUIRED_COLUMNS = [
    'date', 'latitude', 'longitude', 'lead_day', 'forecast_rainfall',
    'observed_rainfall', 'temperature', 'humidity', 'pressure',
    'wind_speed', 'ensemble_spread', 'region'
]

MODELS_DIR.mkdir(parents=True, exist_ok=True)
