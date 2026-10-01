import React from 'react';
import { TelemetryCard } from './TelemetryCard';
import { CardSkeleton } from '../common/LoadingSkeleton';
import { formatTimestamp } from '../../utils/formatters';

export function TelemetryGrid({ telemetry, isLoading, isLive = false }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  const tel = telemetry || {};
  const timestamp = tel.recordedAt || tel.timestamp;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            {isLive ? 'Live IoT Telemetry' : 'IoT Telemetry'}
          </h3>
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1.5 border ${
              isLive
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            {isLive ? 'LIVE STREAM' : 'DIAGNOSIS SNAPSHOT'}
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs">
          {timestamp && (
            <span className="text-[11px] text-slate-400 font-mono">
              Updated: {formatTimestamp(timestamp)}
            </span>
          )}
          {tel.deviceId && (
            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 px-2 py-0.5 rounded">
              Device: {tel.deviceId}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <TelemetryCard
          type="temperature"
          label="Temperature"
          value={tel.temperature}
          unit="°C"
          precision={1}
        />
        <TelemetryCard
          type="vibration"
          label="Vibration"
          value={tel.vibration}
          unit="mm/s"
          precision={1}
        />
        <TelemetryCard
          type="current"
          label="Current"
          value={tel.current}
          unit="A"
          precision={1}
        />
        <TelemetryCard
          type="pressure"
          label="Pressure"
          value={tel.pressure}
          unit="bar"
          precision={1}
        />
      </div>
    </div>
  );
}
