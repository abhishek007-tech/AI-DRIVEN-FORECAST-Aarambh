from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.prediction import router as prediction_router
from app.api.training import router as training_router
from app.api.metrics import router as metrics_router
from app.api.forecast import router as forecast_router

app = FastAPI(title='Forecast Bust Detection MVP', version='0.2.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(health_router)
app.include_router(prediction_router)
app.include_router(training_router)
app.include_router(metrics_router)
app.include_router(forecast_router)
