from fastapi import APIRouter, HTTPException
from app.schemas import ForecastInput, BatchInput, PredictionResponse
from app.ml.predict import predict_one
from app.ml.historical_stats import HistoricalStatsStore
from app.config import DEMO_DATA_PATH
from app.data.loader import DemoDataLoader

router = APIRouter()


def _stats_store():
    if not DEMO_DATA_PATH.exists():
        return None
    return HistoricalStatsStore(DemoDataLoader(DEMO_DATA_PATH).load())


@router.post('/predict', response_model=PredictionResponse)
def predict(payload: ForecastInput):
    try:
        store = _stats_store()
        stats = store.for_prediction(payload.date, payload.region, payload.lead_day) if store else None
        result = predict_one(payload.model_dump(), stats)
        result.update({'lead_day': payload.lead_day, 'region': payload.region})
        return result
    except FileNotFoundError as e:
        raise HTTPException(503, str(e))


@router.post('/predict/batch')
def predict_batch(payload: BatchInput):
    try:
        store = _stats_store()
        out = []
        for item in payload.forecasts:
            stats = store.for_prediction(item.date, item.region, item.lead_day) if store else None
            r = predict_one(item.model_dump(), stats)
            r.update({'date': str(item.date), 'latitude': item.latitude, 'longitude': item.longitude,
                      'lead_day': item.lead_day, 'region': item.region, 'forecast_rainfall': item.forecast_rainfall})
            out.append(r)
        return {'predictions': out}
    except FileNotFoundError as e:
        raise HTTPException(503, str(e))
