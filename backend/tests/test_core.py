import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from app.data.validation import validate_schema
from app.ml.features import add_bust_label, prepare_features
from app.ml.evaluate import _classification
from app.ml.historical_stats import HistoricalStatsStore
from app.ml.predict import confidence_level


def sample():
    return pd.DataFrame({
        'date': pd.to_datetime(['2026-01-01','2026-01-02','2026-01-03','2026-01-04']),
        'latitude':[20]*4,'longitude':[75]*4,'lead_day':[1,2,1,2],
        'forecast_rainfall':[10,40,11,41],'observed_rainfall':[12,10,13,10],
        'temperature':[25]*4,'humidity':[70]*4,'pressure':[1010]*4,'wind_speed':[5]*4,
        'ensemble_spread':[2,3,2,3],'region':['A']*4})


def test_schema_and_label():
    df=sample(); validate_schema(df); out=add_bust_label(df, threshold=20); assert out['bust'].sum()==2


def test_features_have_no_observation_column():
    X,names,_=prepare_features(sample()); assert 'observed_rainfall' not in names; assert X.shape[0]==4


def test_classification_metrics():
    m=_classification([0,1,1,0],[0,1,0,0],[.1,.9,.4,.2]); assert 0 <= m['accuracy'] <= 1; assert m['confusion_matrix']==[[2,0],[1,1]]


def test_historical_stats_excludes_current_observation():
    s=HistoricalStatsStore(sample(), bust_threshold=20)
    stats=s.for_prediction('2026-01-03','A',1)
    assert stats['history_records']==1
    assert stats['historical_mean_abs_error']==2.0


def test_risk_categories_are_configurable_boundaries():
    assert confidence_level(.10)=='LOW_RISK'; assert confidence_level(.50)=='MODERATE_RISK'; assert confidence_level(.90)=='HIGH_RISK'


def test_no_observation_in_prediction_features():
    _,names,_=prepare_features(sample()); assert all('observed' not in n for n in names)
