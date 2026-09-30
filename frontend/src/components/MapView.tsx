import {MapContainer,TileLayer,CircleMarker,Popup} from 'react-leaflet';
import type {ForecastPoint} from '../types';

function radius(p:number){return Math.max(7,Math.min(19,7+p*12))}
function color(p:number){if(p>=.7)return '#e35d3f';if(p>=.4)return '#f0a23a';return '#1c9a8a'}

export default function MapView({points,selected,onSelect}:{points:ForecastPoint[];selected:ForecastPoint|null;onSelect:(p:ForecastPoint)=>void}){
 return <div className="map-shell"><MapContainer center={[22,78]} zoom={4} scrollWheelZoom><TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>{points.map((p,i)=><CircleMarker key={i} center={[p.latitude,p.longitude]} radius={radius(p.bust_probability)} pathOptions={{color:color(p.bust_probability),fillColor:color(p.bust_probability),fillOpacity:.78,weight:selected===p?4:1.5}} eventHandlers={{click:()=>onSelect(p)}}><Popup><div className="popup"><b>{Math.round(p.bust_probability*100)}% bust probability</b><span>Day {p.lead_day} · {p.region}</span><span>{p.forecast_rainfall.toFixed(1)} mm forecast rainfall</span></div></Popup></CircleMarker>)}</MapContainer><div className="map-legend"><b>Bust Probability</b><span><i className="dot low"/>Low &lt; 40%</span><span><i className="dot moderate"/>Moderate 40–69%</span><span><i className="dot high"/>High ≥ 70%</span></div></div>
}
