import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import app


def client(): return TestClient(app)


def test_health():
    r=client().get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'


def test_prediction_api():
    payload={"date":"2026-06-29","latitude":23.3,"longitude":78.4,"lead_day":5,"forecast_rainfall":30,"temperature":25,"humidity":80,"pressure":1008,"wind_speed":10,"ensemble_spread":5,"region":"Central"}
    r=client().post('/predict',json=payload); assert r.status_code==200; body=r.json(); assert 0 <= body['bust_probability'] <= 1; assert body['lead_day']==5; assert 'historical_mean_abs_error' in body


def test_batch_prediction_api():
    payload={"forecasts":[{"date":"2026-06-29","latitude":23.3,"longitude":78.4,"lead_day":5,"forecast_rainfall":30,"temperature":25,"humidity":80,"pressure":1008,"wind_speed":10,"ensemble_spread":5,"region":"Central"}]}
    r=client().post('/predict/batch',json=payload); assert r.status_code==200; assert len(r.json()['predictions'])==1


def test_data_status():
    r=client().get('/data/status'); assert r.status_code==200; assert r.json()['mode']=='DEMO'; assert r.json()['scientific_validation']=='NOT YET ESTABLISHED'


def test_model_info():
    r=client().get('/model/info'); assert r.status_code==200; body=r.json(); assert body['validation_method'].startswith('Chronological'); assert 'risk_thresholds' in body


def test_forecast_endpoint():
    r=client().get('/forecast/2026-06-29?lead_day=5'); assert r.status_code==200; body=r.json(); assert body['data_mode']=='DEMO/SYNTHETIC'; assert body['forecasts']
