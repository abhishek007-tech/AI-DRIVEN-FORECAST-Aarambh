import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, mean_absolute_error, mean_squared_error
from app.config import METRICS_PATH, BUST_THRESHOLD
from app.ml.features import add_bust_label, prepare_features


def _classification(y, p, proba):
    result = {
        'accuracy': float(accuracy_score(y, p)),
        'precision': float(precision_score(y, p, zero_division=0)),
        'recall': float(recall_score(y, p, zero_division=0)),
        'f1': float(f1_score(y, p, zero_division=0)),
        'confusion_matrix': confusion_matrix(y, p).tolist(),
    }
    result['roc_auc'] = float(roc_auc_score(y, proba)) if len(np.unique(y)) == 2 else None
    return result


def evaluate_model(model, test_df: pd.DataFrame, baseline_train_df: pd.DataFrame):
    test_df = add_bust_label(test_df, BUST_THRESHOLD)
    regions = sorted(baseline_train_df['region'].astype(str).unique())
    X, _, _ = prepare_features(pd.concat([baseline_train_df, test_df]), regions)
    X = X.iloc[len(baseline_train_df):]
    y = test_df['bust'].to_numpy()
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= 0.5).astype(int)
    classification = _classification(y, pred, proba)

    # Forecast-error metrics are about rainfall forecasts, not bust classification.
    weather_metrics = {
        'mae': float(mean_absolute_error(test_df['observed_rainfall'], test_df['forecast_rainfall'])),
        'rmse': float(np.sqrt(mean_squared_error(test_df['observed_rainfall'], test_df['forecast_rainfall'])))
    }
    baseline = baseline_train_df.groupby('lead_day')['bust'].mean().to_dict()
    base_prob = test_df['lead_day'].map(baseline).fillna(baseline_train_df['bust'].mean()).to_numpy()
    base_pred = (base_prob >= 0.5).astype(int)
    baseline_metrics = _classification(y, base_pred, base_prob)
    lead_rows = []
    for lead, grp in test_df.assign(_prob=proba).groupby('lead_day'):
        lead_rows.append({
            'lead_day': int(lead),
            'mean_bust_probability': float(grp['_prob'].mean()),
            'historical_mean_absolute_error': float(baseline_train_df[baseline_train_df['lead_day'] == lead]['absolute_error'].mean()),
            'observed_bust_frequency': float(grp['bust'].mean())
        })
    result = {
        'classification': classification,
        'forecast_error': weather_metrics,
        'baseline': baseline_metrics,
        'baseline_description': 'Historical bust frequency by lead day, estimated from training period',
        'evaluation_method': 'Chronological held-out test period; no random shuffle',
        'by_lead_day': lead_rows
    }
    return result


def save_metrics(metrics):
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
