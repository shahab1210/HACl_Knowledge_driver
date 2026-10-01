import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, Cpu, Database, Server, Clock, Layers, ShieldCheck, Timer } from 'lucide-react';
import { formatTimestamp, formatDurationSeconds } from '../../utils/formatters';
import { getConfidenceStyle } from '../../utils/severity';

export function KpiSummaryGrid({ diagnosis, historyCount = 0, backendOnline = true }) {
  const detail = diagnosis?.diagnosis || {};
  const primaryFault = detail.primaryFault || {};
  const confidence = detail.confidence || {};
  const confStyle = getConfidenceStyle(confidence.level);
  const latency = diagnosis?.latencySeconds;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {/* 1. API Status */}
      <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">System API</span>
          <Server className="w-3.5 h-3.5 text-slate-400" />
        </div>
        <div className="mt-2 flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></span>
          <span className={`text-xs font-bold font-mono ${backendOnline ? 'text-emerald-400' : 'text-rose-400'}`}>
            {backendOnline ? 'ONLINE (8080)' : 'OFFLINE'}
          </span>
        </div>
      </div>

      {/* 2. Active Device */}
      <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Device ID</span>
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
        </div>
        <div className="mt-2">
          {diagnosis?.deviceId ? (
            <Link
              to={`/device/${encodeURIComponent(diagnosis.deviceId)}`}
              className="text-xs font-bold text-cyan-400 hover:underline font-mono truncate block"
              title={`View ${diagnosis.deviceId}`}
            >
              {diagnosis.deviceId}
            </Link>
          ) : (
            <span className="text-xs font-mono text-slate-500">N/A</span>
          )}
        </div>
      </div>

      {/* 3. Primary Fault ID */}
      <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Fault Code</span>
          <Layers className="w-3.5 h-3.5 text-indigo-400" />
        </div>
        <div className="mt-2">
          <span className="text-xs font-bold text-white font-mono truncate block" title={primaryFault.title || 'N/A'}>
            {primaryFault.faultId || (primaryFault.title ? 'DETECTED' : 'N/A')}
          </span>
        </div>
      </div>

      {/* 4. Confidence Level */}
      <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Confidence</span>
          <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
        </div>
        <div className="mt-2 flex items-center gap-1.5">
          {confidence.level ? (
            <span className={`text-xs font-extrabold font-mono px-2 py-0.5 rounded-md border ${confStyle.bg} ${confStyle.border} ${confStyle.text}`}>
              {confStyle.label}
            </span>
          ) : (
            <span className="text-xs font-mono text-slate-500">N/A</span>
          )}
        </div>
      </div>

      {/* 5. Diagnosis Latency */}
      <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">AI Latency</span>
          <Timer className="w-3.5 h-3.5 text-amber-400" />
        </div>
        <div className="mt-2">
          <span className="text-xs font-bold text-amber-300 font-mono">
            {latency !== null && latency !== undefined ? formatDurationSeconds(latency) : 'N/A'}
          </span>
        </div>
      </div>

      {/* 6. Total History Records */}
      <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Stored Diagnoses</span>
          <Database className="w-3.5 h-3.5 text-emerald-400" />
        </div>
        <div className="mt-2">
          <span className="text-xs font-bold text-emerald-400 font-mono">
            {historyCount > 0 ? `${historyCount} Records` : (diagnosis ? '1 Record' : '0 Records')}
          </span>
        </div>
      </div>
    </div>
  );
}
