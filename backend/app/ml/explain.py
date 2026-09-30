def explain_prediction(feature_names, importances, top_n=3):
    if importances is None:
        return []
    pairs = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:top_n]
    return [{'feature': f.replace('_', ' ').title(), 'importance': float(v)} for f, v in pairs]
