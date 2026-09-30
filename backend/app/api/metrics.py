import json
from fastapi import APIRouter, HTTPException
from app.config import METRICS_PATH, METADATA_PATH, DEMO_DATA_PATH, MODEL_VERSION
from app.data.loader import DemoDataLoader

router = APIRouter()


@router.get('/metrics')
def metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(404, 'Train the model first')
    return json.loads(METRICS_PATH.read_text())


@router.get('/model/info')
def model_info():
    if not METADATA_PATH.exists():
        raise HTTPException(404, 'Train the model first')
    data = json.loads(METADATA_PATH.read_text())
    data['model_version'] = data.get('model_version', MODEL_VERSION)
    data['risk_thresholds'] = {
        'moderate': data.get('moderate_risk_threshold'),
        'high': data.get('high_risk_threshold'),
    }
    return data


@router.get('/data/status')
def data_status():
    if not DEMO_DATA_PATH.exists():
        return {'mode': 'DEMO', 'data_available': False, 'scientific_validation': 'NOT YET ESTABLISHED'}
    df = DemoDataLoader(DEMO_DATA_PATH).load()
    return {
        'mode': 'DEMO',
        'data_available': True,
        'records': int(len(df)),
        'date_start': str(df['date'].min().date()),
        'date_end': str(df['date'].max().date()),
        'regions': sorted(df['region'].astype(str).unique().tolist()),
        'lead_days': sorted(df['lead_day'].astype(int).unique().tolist()),
        'model_version': MODEL_VERSION,
        'scientific_validation': 'NOT YET ESTABLISHED',
        'label': 'Synthetic forecast/observation pairs for software validation only',
    }
