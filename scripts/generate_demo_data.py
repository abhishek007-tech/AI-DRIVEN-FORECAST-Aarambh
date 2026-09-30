from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'backend/data/demo/weather_demo.csv'

rng = np.random.default_rng(42)
regions = {
    'North': (30.9, 76.8), 'Central': (23.3, 78.4), 'West': (19.1, 73.0),
    'East': (22.6, 88.4), 'South': (13.1, 80.3)
}
dates = pd.date_range('2026-01-01', periods=180, freq='D')
rows=[]
for d_i, date in enumerate(dates):
    seasonal = 4 + 6*np.sin(2*np.pi*d_i/180)
    for region, (lat0, lon0) in regions.items():
        for p in range(4):
            lat = lat0 + (p-1.5)*0.18
            lon = lon0 + (p-1.5)*0.18
            base_rain = max(0, rng.gamma(2.0, 10.0) + seasonal)
            humidity = np.clip(58 + base_rain*0.8 + rng.normal(0, 8), 25, 98)
            temp = 28 - base_rain*0.05 + rng.normal(0, 3)
            pressure = 1012 - base_rain*0.35 + rng.normal(0, 4)
            wind = max(0, 9 + rng.normal(0, 4) + base_rain*0.05)
            for lead in range(1, 11):
                spread = max(0.2, 2 + 0.65*lead + rng.normal(0, 1.1))
                # Synthetic relationship: longer lead/spread and unstable humidity increase error.
                error_scale = 2.5 + 0.9*lead + 0.8*spread + max(0, humidity-75)*0.12
                signed_error = rng.normal(0, error_scale)
                if rng.random() < 0.09 + lead*0.008:
                    signed_error += rng.choice([-1, 1]) * (22 + rng.random()*35)
                forecast = max(0, base_rain + signed_error)
                observed = max(0, base_rain)
                rows.append([date, lat, lon, lead, forecast, observed, temp, humidity, pressure, wind, spread, region])

df = pd.DataFrame(rows, columns=['date','latitude','longitude','lead_day','forecast_rainfall','observed_rainfall','temperature','humidity','pressure','wind_speed','ensemble_spread','region'])
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f'Wrote {len(df):,} synthetic rows to {OUT}')
print('DEMO DATA - NOT REAL WEATHER FORECAST PERFORMANCE')
