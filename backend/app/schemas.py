from datetime import date
from pydantic import BaseModel, Field


class ForecastInput(BaseModel):
    date: date
    latitude: float
    longitude: float
    lead_day: int = Field(ge=1, le=10)
    forecast_rainfall: float = Field(ge=0)
    temperature: float
    humidity: float = Field(ge=0, le=100)
    pressure: float
    wind_speed: float = Field(ge=0)
    ensemble_spread: float = Field(ge=0)
    region: str


class PredictionResponse(BaseModel):
    bust_probability: float
    confidence_level: str
    lead_day: int
    region: str
    top_factors: list[str]
    historical_mean_abs_error: float = 0.0
    historical_bust_frequency: float = 0.0
    history_records: int = 0


class BatchInput(BaseModel):
    forecasts: list[ForecastInput]
