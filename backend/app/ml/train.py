import json
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None
from app.config import (MODEL_PATH, FEATURE_NAMES_PATH, METADATA_PATH, BUST_THRESHOLD,
                        RANDOM_STATE, MODEL_VERSION, HIGH_RISK_THRESHOLD, MODERATE_RISK_THRESHOLD)
from app.data.loader import ForecastDataLoader
from app.ml.features import add_bust_label, prepare_features


def build_model():
    if XGBClassifier is not None:
        return XGBClassifier(
            n_estimators=220, max_depth=5, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.9, random_state=RANDOM_STATE,
            eval_metric='logloss', n_jobs=2
        ), 'XGBoostClassifier'
    return RandomForestClassifier(
        n_estimators=250, max_depth=10, min_samples_leaf=3,
        random_state=RANDOM_STATE, class_weight='balanced', n_jobs=2
    ), 'RandomForestClassifier'


def train_from_csv(path: str | Path, train_frac=0.70, val_frac=0.15):
    df = ForecastDataLoader(path).load()
    df = add_bust_label(df, BUST_THRESHOLD).sort_values('date').reset_index(drop=True)
    dates = sorted(df['date'].dt.normalize().unique())
    if len(dates) < 10:
        raise ValueError('Need at least 10 distinct dates for temporal train/validation/test split')
    train_end = max(1, int(len(dates) * train_frac))
    val_end = max(train_end + 1, int(len(dates) * (train_frac + val_frac)))
    train_dates = set(dates[:train_end])
    val_dates = set(dates[train_end:val_end])
    test_dates = set(dates[val_end:])
    if not test_dates:
        raise ValueError('Temporal split produced no test period')

    train_df = df[df.date.dt.normalize().isin(train_dates)].copy()
    val_df = df[df.date.dt.normalize().isin(val_dates)].copy()
    test_df = df[df.date.dt.normalize().isin(test_dates)].copy()
    regions = sorted(train_df['region'].astype(str).unique())
    X_train, feature_names, region_map = prepare_features(train_df, regions, BUST_THRESHOLD)
    X_val, _, _ = prepare_features(pd.concat([train_df, val_df]), regions, BUST_THRESHOLD)
    X_val = X_val.iloc[len(train_df):]
    X_test, _, _ = prepare_features(pd.concat([train_df, val_df, test_df]), regions, BUST_THRESHOLD)
    X_test = X_test.iloc[len(train_df) + len(val_df):]
    y_train, y_val, y_test = train_df['bust'].values, val_df['bust'].values, test_df['bust'].values

    estimator, model_name = build_model()
    if model_name == 'XGBoostClassifier':
        positives = max(1, int(y_train.sum()))
        negatives = max(1, len(y_train) - positives)
        estimator.set_params(scale_pos_weight=negatives / positives)
    pipe = Pipeline([('imputer', SimpleImputer(strategy='median')), ('model', estimator)])
    pipe.fit(X_train, y_train)

    metadata = {
        'model_name': model_name,
        'model_version': MODEL_VERSION,
        'bust_threshold': BUST_THRESHOLD,
        'moderate_risk_threshold': MODERATE_RISK_THRESHOLD,
        'high_risk_threshold': HIGH_RISK_THRESHOLD,
        'feature_names': feature_names,
        'region_map': region_map,
        'train_start': str(min(train_dates)), 'train_end': str(max(train_dates)),
        'validation_start': str(min(val_dates)) if val_dates else None,
        'validation_end': str(max(val_dates)) if val_dates else None,
        'test_start': str(min(test_dates)), 'test_end': str(max(test_dates)),
        'data_mode': 'DEMO/SYNTHETIC' if 'demo' in str(path).lower() else 'REAL_DATA',
        'validation_method': 'Chronological train / validation / test split',
    }
    import joblib
    joblib.dump(pipe, MODEL_PATH)
    FEATURE_NAMES_PATH.write_text(json.dumps(feature_names, indent=2))
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    return pipe, metadata, {'train': train_df, 'validation': val_df, 'test': test_df}
