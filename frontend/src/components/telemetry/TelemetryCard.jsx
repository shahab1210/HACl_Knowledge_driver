import React from 'react';
import { Thermometer, Activity, Zap, Gauge, Droplets } from 'lucide-react';
import { formatTelemetryValue } from '../../utils/formatters';
import { getSensorStatus } from '../../utils/severity';

const ICON_MAP = {
  temperature: Thermometer,
  vibration: Activity,
  current: Zap,
  pressure: Gauge,
  humidity: Droplets,
};

export function TelemetryCard({ type, label, value, unit, precision = 1 }) {
  const Icon = ICON_MAP[type.toLowerCase()] || Activity;
  const status = getSensorStatus(type, value);
  const formattedVal = formatTelemetryValue(value, '', precision);

  let badgeColor = 'bg-slate-800 text-slate-400 border-slate-700';
  if (status.color === 'red') badgeColor = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
  if (status.color === 'amber') badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  if (status.color === 'emerald') badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 hover:border-slate-700/80 rounded-2xl p-5 shadow-lg shadow-black/20 backdrop-blur-sm transition-all">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{label}</span>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${badgeColor}`}>
          {status.label}
        </span>
      </div>

      <div className="flex items-baseline justify-between mt-4">
        <div className="flex items-baseline gap-1.5">
          <span className="text-3xl font-extrabold tracking-tight text-white font-mono">{formattedVal}</span>
          {value !== null && value !== undefined && (
            <span className="text-sm font-semibold text-slate-400">{unit}</span>
          )}
        </div>
        <div className="w-10 h-10 rounded-xl bg-slate-800/80 border border-slate-700/50 flex items-center justify-center text-slate-300">
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 flex items-center justify-between">
        <span>{status.text}</span>
      </div>
    </div>
  );
}
