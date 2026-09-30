from fastapi import APIRouter, HTTPException
from app.config import DEMO_DATA_PATH
from app.ml.train import train_from_csv
from app.ml.evaluate import evaluate_model, save_metrics

router = APIRouter()


@router.post('/train')
def train():
    try:
        model, metadata, splits = train_from_csv(DEMO_DATA_PATH)
        metrics = evaluate_model(model, splits['test'], splits['train'])
        metrics['data_label'] = 'Illustrative demo-data evaluation'
        save_metrics(metrics)
        return {'status': 'trained', 'model': metadata['model_name'], 'metrics': metrics, 'metadata': metadata}
    except Exception as e:
        raise HTTPException(500, str(e))
