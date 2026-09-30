import type {DataStatus, ForecastPoint, Metrics, ModelInfo} from '../types';
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
async function getJson<T>(url:string):Promise<T>{const r=await fetch(url);if(!r.ok)throw new Error(await r.text());return r.json() as Promise<T>}
export const getRegions=()=>getJson<{regions:string[]}>(`${API}/regions`);
export const getForecast=(date:string,lead:number,region:string)=>{const q=new URLSearchParams({lead_day:String(lead)});if(region!=='ALL')q.set('region',region);return getJson<{forecasts:ForecastPoint[];warning:string;data_mode:string}>(`${API}/forecast/${date}?${q}`)};
export const getMetrics=()=>getJson<Metrics>(`${API}/metrics`);
export const getModelInfo=()=>getJson<ModelInfo>(`${API}/model/info`);
export const getDataStatus=()=>getJson<DataStatus>(`${API}/data/status`);
