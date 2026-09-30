export type ForecastPoint = {
  date: string; latitude: number; longitude: number; lead_day: number;
  forecast_rainfall: number; temperature: number; humidity: number;
  pressure: number; wind_speed: number; ensemble_spread: number; region: string;
  bust_probability: number; confidence_level: string; top_factors: string[];
  historical_mean_abs_error: number; historical_bust_frequency: number; history_records: number;
};

export type LeadRow = { lead_day:number; mean_bust_probability:number; historical_mean_absolute_error:number; observed_bust_frequency:number };
export type Metrics = {
  classification:{accuracy:number;precision:number;recall:number;f1:number;roc_auc:number|null;confusion_matrix:number[][]};
  forecast_error:{mae:number;rmse:number};
  baseline:{accuracy:number;precision:number;recall:number;f1:number;roc_auc:number|null;confusion_matrix:number[][]};
  baseline_description:string; evaluation_method:string; data_label:string; by_lead_day:LeadRow[];
};
export type ModelInfo = {model_name:string;model_version:string;feature_names:string[];train_start:string;train_end:string;validation_start:string;validation_end:string;test_start:string;test_end:string;data_mode:string;bust_threshold:number;risk_thresholds:{moderate:number;high:number};validation_method:string};
export type DataStatus = {mode:string;data_available:boolean;records:number;date_start:string;date_end:string;regions:string[];lead_days:number[];model_version:string;scientific_validation:string;label:string};
