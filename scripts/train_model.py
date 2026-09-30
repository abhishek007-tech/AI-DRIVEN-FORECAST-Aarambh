from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
sys.path.insert(0, str(BACKEND))
from app.config import DEMO_DATA_PATH
from app.ml.train import train_from_csv
from app.ml.evaluate import evaluate_model, save_metrics

model, metadata, splits = train_from_csv(DEMO_DATA_PATH)
metrics = evaluate_model(model, splits['test'], splits['train'])
metrics['data_label'] = 'Illustrative demo-data evaluation'
save_metrics(metrics)
print('Model:', metadata['model_name'])
print('Test period:', metadata['test_start'], 'to', metadata['test_end'])
print('Classification:', metrics['classification'])
print('Forecast error:', metrics['forecast_error'])
print('DEMO DATA - NOT REAL WEATHER FORECAST PERFORMANCE')
