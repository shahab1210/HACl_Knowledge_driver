import React, { useState, useEffect } from 'react';
import { TrendingUp, Info, Database } from 'lucide-react';
import { formatTimestamp } from '../../utils/formatters';

export function TelemetryTrendChart({ history = [], liveHistory = [] }) {
  const [selectedMetric, setSelectedMetric] = useState('all');

  const hasLive = Array.isArray(liveHistory) && liveHistory.length > 0;
  const hasDiag = Array.isArray(history) && history.some((d) => d && d.telemetry);

  // Default to 'raw' if liveHistory is provided, else 'diagnosis'
  const [sourceMode, setSourceMode] = useState(hasLive ? 'raw' : 'diagnosis');

  useEffect(() => {
    if (hasLive && sourceMode === 'diagnosis' && !hasDiag) {
      setSourceMode('raw');
    }
  }, [hasLive, hasDiag]);

  const isRaw = sourceMode === 'raw' && hasLive;

  // Extract strictly real telemetry data points sorted chronologically
  const validPoints = isRaw
    ? liveHistory.map((pt, idx) => ({
        id: pt.id || `live-${idx}`,
        timestamp: pt.recordedAt,
        temperature: pt.temperature !== null && pt.temperature !== undefined ? Number(pt.temperature) : null,
        vibration: pt.vibration !== null && pt.vibration !== undefined ? Number(pt.vibration) : null,
        current: pt.current !== null && pt.current !== undefined ? Number(pt.current) : null,
        pressure: pt.pressure !== null && pt.pressure !== undefined ? Number(pt.pressure) : null,
      }))
    : (history || [])
        .filter((d) => d && d.telemetry)
        .map((d) => ({
          id: d.id,
          timestamp: d.timestamp || d.telemetry?.recordedAt,
          temperature: d.telemetry?.temperature !== null && d.telemetry?.temperature !== undefined ? Number(d.telemetry.temperature) : null,
          vibration: d.telemetry?.vibration !== null && d.telemetry?.vibration !== undefined ? Number(d.telemetry.vibration) : null,
          current: d.telemetry?.current !== null && d.telemetry?.current !== undefined ? Number(d.telemetry.current) : null,
          pressure: d.telemetry?.pressure !== null && d.telemetry?.pressure !== undefined ? Number(d.telemetry.pressure) : null,
        }))
        .reverse(); // Chronological (oldest to newest for left-to-right chart)

  if (validPoints.length === 0) {
    return (
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-center">
        <span className="text-xs text-slate-400 italic">
          Historical telemetry trend visualization requires at least one recorded sensor reading or diagnosis.
        </span>
      </div>
    );
  }

  // Determine min/max values for scaling
  const temps = validPoints.map((p) => p.temperature).filter((v) => v !== null);
  const vibs = validPoints.map((p) => p.vibration).filter((v) => v !== null);
  const currents = validPoints.map((p) => p.current).filter((v) => v !== null);

  const maxTemp = temps.length > 0 ? Math.max(...temps, 100) : 100;
  const minTemp = temps.length > 0 ? Math.min(...temps, 20) : 20;

  const maxVib = vibs.length > 0 ? Math.max(...vibs, 20) : 20;
  const minVib = 0;

  const maxCurr = currents.length > 0 ? Math.max(...currents, 40) : 40;
  const minCurr = 0;

  const width = 600;
  const height = 180;
  const padding = 35;

  const getX = (idx) => {
    if (validPoints.length === 1) return width / 2;
    return padding + (idx / (validPoints.length - 1)) * (width - 2 * padding);
  };

  const getYTemp = (val) => {
    if (val === null) return height - padding;
    return height - padding - ((val - minTemp) / (maxTemp - minTemp || 1)) * (height - 2 * padding);
  };

  const getYVib = (val) => {
    if (val === null) return height - padding;
    return height - padding - ((val - minVib) / (maxVib - minVib || 1)) * (height - 2 * padding);
  };

  const getYCurr = (val) => {
    if (val === null) return height - padding;
    return height - padding - ((val - minCurr) / (maxCurr - minCurr || 1)) * (height - 2 * padding);
  };

  // Build SVG path strings
  const tempPath = validPoints
    .filter((p) => p.temperature !== null)
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getYTemp(p.temperature)}`)
    .join(' ');

  const vibPath = validPoints
    .filter((p) => p.vibration !== null)
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getYVib(p.vibration)}`)
    .join(' ');

  const currPath = validPoints
    .filter((p) => p.current !== null)
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getYCurr(p.current)}`)
    .join(' ');

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Telemetry Progression Trends
            </h3>
            <span className="text-[11px] text-slate-400">
              {isRaw
                ? `Extracted from ${validPoints.length} real sensor reading${validPoints.length > 1 ? 's' : ''} in PostgreSQL (sensor_readings)`
                : `Extracted from ${validPoints.length} real diagnosis record${validPoints.length > 1 ? 's' : ''} in PostgreSQL`}
            </span>
          </div>
        </div>

        {/* Controls: Source Mode & Metric Selector */}
        <div className="flex flex-wrap items-center gap-2">
          {hasLive && hasDiag && (
            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
              <button
                type="button"
                onClick={() => setSourceMode('raw')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-colors flex items-center gap-1.5 ${
                  sourceMode === 'raw'
                    ? 'bg-cyan-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                Live Raw ({liveHistory.length})
              </button>
              <button
                type="button"
                onClick={() => setSourceMode('diagnosis')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                  sourceMode === 'diagnosis'
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Diagnosis Records ({history.filter((d) => d?.telemetry).length})
              </button>
            </div>
          )}

          {/* Metric Selector Tabs */}
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setSelectedMetric('all')}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                selectedMetric === 'all' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All Channels
            </button>
            <button
              onClick={() => setSelectedMetric('temp')}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                selectedMetric === 'temp' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Temp (°C)
            </button>
            <button
              onClick={() => setSelectedMetric('vib')}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                selectedMetric === 'vib' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Vib (mm/s)
            </button>
            <button
              onClick={() => setSelectedMetric('curr')}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                selectedMetric === 'curr' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Curr (A)
            </button>
          </div>
        </div>
      </div>

      {/* SVG Multi-Series Trend Chart */}
      <div className="relative w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-44 overflow-visible font-mono">
          {/* Background grid lines */}
          <line x1={padding} y1={padding} x2={width - padding} y2={padding} stroke="#334155" strokeDasharray="3 3" strokeWidth="0.5" />
          <line x1={padding} y1={height / 2} x2={width - padding} y2={height / 2} stroke="#334155" strokeDasharray="3 3" strokeWidth="0.5" />
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#475569" strokeWidth="1" />

          {/* Lines */}
          {(selectedMetric === 'all' || selectedMetric === 'temp') && tempPath && (
            <path d={tempPath} fill="none" stroke="#f43f5e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          )}
          {(selectedMetric === 'all' || selectedMetric === 'vib') && vibPath && (
            <path d={vibPath} fill="none" stroke="#f59e0b" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          )}
          {(selectedMetric === 'all' || selectedMetric === 'curr') && currPath && (
            <path d={currPath} fill="none" stroke="#06b6d4" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          )}

          {/* Data point dots & value labels */}
          {validPoints.map((pt, idx) => {
            const x = getX(idx);
            return (
              <g key={pt.id || idx}>
                {(selectedMetric === 'all' || selectedMetric === 'temp') && pt.temperature !== null && (
                  <>
                    <circle cx={x} cy={getYTemp(pt.temperature)} r="4" fill="#f43f5e" stroke="#0f172a" strokeWidth="2" />
                    <text x={x} y={getYTemp(pt.temperature) - 8} fill="#fda4af" fontSize="9" textAnchor="middle" fontWeight="bold">
                      {pt.temperature.toFixed(1)}°C
                    </text>
                  </>
                )}
                {(selectedMetric === 'all' || selectedMetric === 'vib') && pt.vibration !== null && (
                  <>
                    <circle cx={x} cy={getYVib(pt.vibration)} r="4" fill="#f59e0b" stroke="#0f172a" strokeWidth="2" />
                    <text x={x} y={getYVib(pt.vibration) - 8} fill="#fde68a" fontSize="9" textAnchor="middle" fontWeight="bold">
                      {pt.vibration.toFixed(1)}
                    </text>
                  </>
                )}
                {(selectedMetric === 'all' || selectedMetric === 'curr') && pt.current !== null && (
                  <>
                    <circle cx={x} cy={getYCurr(pt.current)} r="4" fill="#06b6d4" stroke="#0f172a" strokeWidth="2" />
                    <text x={x} y={getYCurr(pt.current) + 14} fill="#a5f3fc" fontSize="9" textAnchor="middle" fontWeight="bold">
                      {pt.current.toFixed(1)}A
                    </text>
                  </>
                )}

                {/* X-axis point label */}
                <text x={x} y={height - 10} fill="#94a3b8" fontSize="8" textAnchor="middle">
                  #{idx + 1}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend & Note */}
      <div className="flex flex-wrap items-center justify-between gap-4 mt-3 pt-3 border-t border-slate-800/60 text-xs">
        <div className="flex items-center gap-4 text-[11px] font-semibold">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span className="text-slate-300">Temperature (°C)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span className="text-slate-300">Vibration (mm/s)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
            <span className="text-slate-300">Current (A)</span>
          </div>
        </div>

        <div className="flex items-center gap-1 text-[11px] text-slate-400">
          <Info className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <span>
            {isRaw
              ? 'Historical points derived from sensor_readings table via GET /api/v1/telemetry/history'
              : 'Historical points derived from persisted PostgreSQL diagnosis records'}
          </span>
        </div>
      </div>
    </div>
  );
}
