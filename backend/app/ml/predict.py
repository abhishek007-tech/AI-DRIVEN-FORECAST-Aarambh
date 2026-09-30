import json
import joblib
import pandas as pd
from app.config import MODEL_PATH, METADATA_PATH, HIGH_RISK_THRESHOLD, MODERATE_RISK_THRESHOLD


def load_artifacts():
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError('Model artifacts not found. Run training first.')
    return joblib.load(MODEL_PATH), json.loads(METADATA_PATH.read_text())


def confidence_level(prob: float) -> str:
    if prob >= HIGH_RISK_THRESHOLD:
        return 'HIGH_RISK'
    if prob >= MODERATE_RISK_THRESHOLD:
        return 'MODERATE_RISK'
    return 'LOW_RISK'


def predict_one(row: dict, historical_stats: dict | None = None):
    model, metadata = load_artifacts()
    stats = historical_stats or {
        'historical_mean_abs_error': float(row.get('historical_mean_abs_error', 0.0)),
        'historical_bust_frequency': float(row.get('historical_bust_frequency', 0.0)),
        'history_records': int(row.get('history_records', 0)),
    }
    df = pd.DataFrame([row])
    df['historical_mean_abs_error'] = float(stats.get('historical_mean_abs_error', 0.0))
    df['historical_bust_frequency'] = float(stats.get('historical_bust_frequency', 0.0))
    df['region_code'] = df['region'].map(metadata['region_map']).fillna(-1).astype(float)
    feature_names = metadata['feature_names']
    X = df[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    prob = float(model.predict_proba(X)[:, 1][0])
    estimator = model.named_steps['model']
    importances = getattr(estimator, 'feature_importances_', None)
    factors = []
    if importances is not None:
        ranked = sorted(zip(metadata['feature_names'], importances), key=lambda x: x[1], reverse=True)
        factors = [name.replace('_', ' ').title() for name, _ in ranked[:3]]
    return {
        'bust_probability': prob,
        'confidence_level': confidence_level(prob),
        'top_factors': factors,
        'historical_mean_abs_error': float(stats.get('historical_mean_abs_error', 0.0)),
        'historical_bust_frequency': float(stats.get('historical_bust_frequency', 0.0)),
        'history_records': int(stats.get('history_records', 0)),
    }
