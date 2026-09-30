# Forecast Bust Detection MVP

AI-based forecast bust detection for medium-range weather forecasts, built as an incremental SIH 2026 MVP for **SIH26079**.

## 1. Problem

Given a weather forecast and historical forecast-error behaviour, estimate how likely the current forecast is to be a **forecast bust**.

For this MVP:

```text
absolute_error = abs(forecast_rainfall - observed_rainfall)
bust = 1 if absolute_error >= BUST_THRESHOLD else 0
```

The default threshold is `20.0 mm` only as a configurable software-demo setting. It is **not a universal meteorological threshold**.

## 2. What the MVP does

The existing application has been improved incrementally. Its core architecture remains:

```text
Forecast / Observation Pairs
        ↓
Data Loader Abstraction
        ↓
Feature Preparation
        ↓
Historical Error Statistics
        ↓
Bust Label
        ↓
Temporal ML Training
        ↓
Predicted Bust Probability
        ↓
Risk Category
        ↓
Regional Map
        ↓
Model-derived Factors
        ↓
Verification Metrics
```

The frontend is designed for an approximately 10-second technical overview rather than a generic SaaS dashboard.

## 3. Data modes

### Demo mode

The repository contains a synthetic generator so the entire software pipeline can run without external weather-data access.

**DEMO DATA - NOT REAL WEATHER FORECAST PERFORMANCE**

The generated data is intentionally synthetic and is used for:

- software validation
- API testing
- model-pipeline testing
- UI demonstration

The resulting metrics must not be presented as real weather forecast skill.

### Real-data mode

The ingestion layer now exposes a compatible abstraction:

```text
Synthetic CSV → DemoDataLoader ┐
                               ├→ common feature / ML pipeline
Real NWP + observations → RealWeatherDataLoader interface
```

The real loader is intentionally an integration contract, not a fabricated data source.

## 4. Data schema

The normalized schema is:

| Column | Description |
|---|---|
| `date` | Forecast/verification date |
| `latitude` | Grid/point latitude |
| `longitude` | Grid/point longitude |
| `lead_day` | Forecast lead, 1-10 |
| `forecast_rainfall` | Forecast rainfall |
| `observed_rainfall` | Verifying observation, used only for labels/evaluation |
| `temperature` | Forecast temperature |
| `humidity` | Forecast humidity |
| `pressure` | Forecast pressure |
| `wind_speed` | Forecast wind speed |
| `ensemble_spread` | Ensemble uncertainty proxy |
| `region` | Region identifier |

## 5. Bust definition

The threshold is configured through environment variables:

```text
BUST_THRESHOLD=20.0
MODERATE_RISK_THRESHOLD=0.40
HIGH_RISK_THRESHOLD=0.70
```

Risk categories are UI/model-output categories. They are **not official meteorological warning levels and not confidence intervals**.

The final SIH implementation should determine the operational bust definition from historical forecast-error distributions and domain validation.

## 6. Historical statistics and leakage protection

The application now has a reusable `HistoricalStatsStore`.

It calculates, using only records strictly earlier than the forecast date:

- historical mean absolute error
- historical bust frequency
- lead-day statistics
- region + lead-day statistics when available

The current verifying observation is never passed into the prediction feature vector.

This same concept is used by the demo forecast endpoint and can later be backed by real NWP + observation archives.

## 7. Feature engineering

Current model features include:

- forecast rainfall
- lead day
- temperature
- humidity
- pressure
- wind speed
- ensemble spread
- latitude / longitude
- historical mean absolute error
- historical bust frequency
- region identifier

Observed rainfall is not a current-prediction feature.

## 8. ML model

Primary model:

`XGBoostClassifier`

Fallback:

`RandomForestClassifier`

The model outputs a **predicted bust probability**, not certainty.

Probability categories are configurable:

- `< 0.40` → LOW RISK
- `0.40–0.69` → MODERATE RISK
- `>= 0.70` → HIGH RISK

These thresholds are configurable and are not scientific warning thresholds.

Probability calibration was intentionally not forced into this MVP because reliability of the existing pipeline takes priority. It should be evaluated after real data is available.

## 9. Temporal validation

The primary evaluation does not randomly shuffle the weather time series.

The application uses:

```text
Earlier dates  → Training
Later dates    → Validation
Latest dates   → Held-out test
```

The `/model/info` endpoint exposes these date ranges and explicitly reports:

`Chronological train / validation / test split`

## 10. Evaluation

### Classification metrics

- Accuracy
- Precision
- Recall
- F1
- ROC-AUC
- Confusion matrix

### Forecast-error metrics

- MAE
- RMSE

These measure different things and are displayed separately.

### Baseline

The MVP includes a simple historical baseline based on bust frequency by lead day from the training period.

The dashboard displays ML and baseline metrics side by side without declaring a winner. This matters because the synthetic baseline can outperform the ML model on some metrics, and hiding that would be dishonest.

All current results are labelled:

**Illustrative demo-data evaluation**

## 11. API

Existing endpoints are preserved:

- `GET /health`
- `POST /train`
- `POST /predict`
- `POST /predict/batch`
- `GET /metrics`
- `GET /regions`
- `GET /forecast/{date}?lead_day=5&region=Central`
- `GET /model/info`

Added:

- `GET /data/status`

`/data/status` reports mode, record count, date range, regions, lead days, model version, and scientific-validation status.

## 12. Dashboard

The redesigned dashboard includes:

1. **Main dashboard**
   - KPI row
   - regional risk map
   - demo-mode provenance

2. **Selected location**
   - bust probability
   - risk category
   - lead day
   - region
   - forecast rainfall
   - ensemble spread
   - historical error
   - prior historical records
   - model-derived importance signals

3. **Lead-day analysis**
   - bust probability by Day 1-10
   - historical forecast error by lead day

4. **Model verification**
   - classification metrics
   - MAE / RMSE
   - confusion matrix
   - baseline comparison

5. **Data status**
   - DEMO mode
   - record count
   - lead-time coverage
   - region count
   - `SCIENTIFIC VALIDATION: NOT YET ESTABLISHED`

## 13. Run locally

From the repository root:

### Backend environment

```bash
python -m venv backend/.venv
```

Windows PowerShell:

```powershell
backend\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Linux/macOS:

```bash
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### Generate demo data

```bash
python scripts/generate_demo_data.py
```

### Train the model

```bash
python scripts/train_model.py
```

### Start FastAPI

```bash
cd backend
uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

### Start frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

### Run tests

```bash
cd backend
pytest -q
```

## 14. PPT-ready views

Use these five views for the SIH presentation:

1. **Main dashboard**: map + KPI row + demo badge.
2. **Selected location**: probability + risk + forecast details + model-derived factors.
3. **Day 1-10 analysis**: lead-time risk and historical-error charts.
4. **Model verification**: classification metrics + confusion matrix + baseline comparison.
5. **Data status**: DEMO mode and `SCIENTIFIC VALIDATION: NOT YET ESTABLISHED`.

The fifth screenshot is important. It prevents the demo from accidentally looking like a claim of operational forecasting skill.

## 15. Limitations

- Current data is synthetic.
- Rainfall-only bust labeling is intentionally narrow.
- No operational NWP/observation ingestion is connected yet.
- Spatial modeling is point-based, not a learned spatial field model.
- Feature importance is not causal explanation.
- Probability calibration has not been added to the MVP.
- No authentication, cloud deployment, alerting, database, or complex MLOps is included.

## 16. Real-data integration plan

When approved real datasets become available:

1. Implement `RealWeatherDataLoader` for the supplied NWP and observation format.
2. Normalize it to the documented schema.
3. Preserve the same `HistoricalStatsStore` contract.
4. Re-run temporal training/evaluation.
5. Validate the bust definition with domain experts.
6. Evaluate by lead day, region, event intensity, and weather regime.
7. Calibrate probabilities if the held-out real-data results justify it.
8. Only then discuss real-world forecast-bust performance.

Potential future sources may include approved IMD/NCMRWF/ECMWF data access, subject to actual availability and licensing. The current MVP does not claim access to any of them.

## 17. Future SIH implementation

Possible extensions without replacing this architecture:

- ensemble member features
- spatial grids and regional aggregation
- weather-regime features
- SHAP-based case explanations
- Day 1-10 verification by region/event type
- automated data refresh
- retraining and drift monitoring
- operational data-quality checks

## 18. Honest status

> **Current MVP demonstrates the complete software pipeline using synthetic data. Real NWP and observation datasets are required before claiming operational forecasting skill.**
