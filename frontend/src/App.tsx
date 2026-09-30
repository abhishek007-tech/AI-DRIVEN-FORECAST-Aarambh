import {useEffect,useMemo,useState} from 'react';
import MapView from './components/MapView';
import MetricsPanel from './components/MetricsPanel';
import {getDataStatus,getForecast,getMetrics,getModelInfo,getRegions} from './services/api';
import type {DataStatus,ForecastPoint,Metrics,ModelInfo} from './types';

function riskLabel(level:string){return level.replace('_',' ')}
function pct(n:number){return `${Math.round(n*100)}%`}

export default function App(){
 const [date,setDate]=useState('2026-06-29'),[lead,setLead]=useState(5),[region,setRegion]=useState('ALL');
 const [regions,setRegions]=useState<string[]>([]),[points,setPoints]=useState<ForecastPoint[]>([]),[selected,setSelected]=useState<ForecastPoint|null>(null);
 const [metrics,setMetrics]=useState<Metrics|null>(null),[model,setModel]=useState<ModelInfo|null>(null),[status,setStatus]=useState<DataStatus|null>(null),[error,setError]=useState('');
 async function load(){try{setError('');const [f,m,mi,ds]=await Promise.all([getForecast(date,lead,region),getMetrics(),getModelInfo(),getDataStatus()]);setPoints(f.forecasts);setSelected(prev=>prev&&f.forecasts.find(x=>x.latitude===prev.latitude&&x.longitude===prev.longitude&&x.region===prev.region)||f.forecasts[0]||null);setMetrics(m);setModel(mi);setStatus(ds)}catch(e){setError(String(e))}}
 useEffect(()=>{getRegions().then(x=>setRegions(x.regions)).catch(e=>setError(String(e)));load()},[]);useEffect(()=>{load()},[date,lead,region]);
 const selectedLabel=selected?riskLabel(selected.confidence_level):'No selection';
 const summary=useMemo(()=>selected||points[0], [selected,points]);
 return <main>
  <header className="hero"><div><div className="brand"><span className="brand-mark">FD</span><span>Forecast Intelligence</span></div><h1>Forecast Bust Detection</h1><p>AI-based identification of high-risk conditions in medium-range weather forecasts</p></div><div className="mode-stack"><span className="demo-badge">DEMO MODE</span><span>Synthetic data · Software validation only</span></div></header>
  <div className="notice"><b>Demo data:</b> synthetic forecast/observation pairs validate the software pipeline. They are <strong>not real weather forecast performance</strong>.</div>
  <section className="controls card"><label>Date<input type="date" value={date} onChange={e=>setDate(e.target.value)}/></label><label>Lead time<select value={lead} onChange={e=>setLead(+e.target.value)}>{Array.from({length:10},(_,i)=><option key={i+1} value={i+1}>Day {i+1}</option>)}</select></label><label>Region<select value={region} onChange={e=>setRegion(e.target.value)}><option>ALL</option>{regions.map(r=><option key={r}>{r}</option>)}</select></label></section>
  {error&&<div className="error">{error}</div>}
  <section className="kpis">
   <div className="kpi"><span>LEAD TIME</span><b>Day {summary?.lead_day??lead}</b><small>Selected forecast horizon</small></div>
   <div className="kpi"><span>BUST PROBABILITY</span><b>{summary?pct(summary.bust_probability):'--'}</b><small>Predicted probability</small></div>
   <div className="kpi"><span>RISK LEVEL</span><b className={`risk-${summary?.confidence_level?.toLowerCase()||'low'}`}>{summaryLabel(selectedLabel)}</b><small>UI risk category, not a warning</small></div>
   <div className="kpi"><span>REGION</span><b>{summary?.region||region}</b><small>Selected location</small></div>
  </section>
  <section className="story"><span>NWP FORECAST</span><i>→</i><span>FEATURES</span><i>→</i><span>HISTORICAL ERRORS</span><i>→</i><span>AI BUST DETECTION</span><i>→</i><span>RISK MAP</span><i>→</i><span>VERIFICATION</span></section>
  <section className="main-grid"><div><div className="section-head map-head"><div><span className="eyebrow">REGIONAL RISK MAP</span><h2>Where the forecast is most at risk</h2></div><span className="map-count">{points.length} forecast points</span></div><MapView points={points} selected={selected} onSelect={setSelected}/></div>
   <aside className="detail card"><span className="eyebrow">SELECTED LOCATION</span>{selected?<><div className="detail-prob">{pct(selected.bust_probability)}</div><div className={`risk-pill ${selected.confidence_level.toLowerCase()}`}>{riskLabel(selected.confidence_level)}</div><div className="detail-grid"><span>Lead day<b>Day {selected.lead_day}</b></span><span>Region<b>{selected.region}</b></span><span>Forecast rainfall<b>{selected.forecast_rainfall.toFixed(1)} mm</b></span><span>Ensemble spread<b>{selected.ensemble_spread.toFixed(1)}</b></span><span>Historical error<b>{selected.historical_mean_abs_error.toFixed(1)} mm</b></span><span>Prior records<b>{selected.history_records}</b></span></div><div className="explain"><span className="eyebrow">WHY THIS LOCATION IS FLAGGED</span><p>Elevated bust risk is associated with the model's learned importance signals for this forecast case. This is not a causal weather explanation.</p><h3>Model-derived importance signals</h3><ul>{selected.top_factors.map(x=><li key={x}>{x}</li>)}</ul></div></>:<p>No forecast point selected.</p>}</aside>
  </section>
  <section className="data-strip card"><div><span className="eyebrow">DATA STATUS</span><h2>Transparent demo provenance</h2></div><div><span>Mode<b>DEMO</b></span><span>Records<b>{status?.records??'--'}</b></span><span>Lead times<b>Day 1–10</b></span><span>Regions<b>{status?.regions?.length??'--'}</b></span><span>Scientific validation<b className="not-established">NOT YET ESTABLISHED</b></span></div></section>
  <section className="model-strip card"><div><span className="eyebrow">MODEL INFORMATION</span><h2>{model?.model_name||'Model'}</h2></div><div><span>Validation<b>Chronological train / validation / test split</b></span><span>Train<b>{model?.train_start} → {model?.train_end}</b></span><span>Validation<b>{model?.validation_start} → {model?.validation_end}</b></span><span>Test<b>{model?.test_start} → {model?.test_end}</b></span><span>Bust threshold<b>{model?.bust_threshold} mm</b></span></div></section>
  <MetricsPanel m={metrics}/>
 </main>
}
function summaryLabel(v:string){return v==='No selection'?'--':v}
