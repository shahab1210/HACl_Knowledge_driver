import React from 'react';
import { Link } from 'react-router-dom';
import { AlertOctagon, Clock, ArrowRight, CheckCircle2, Cpu, Activity, Timer } from 'lucide-react';
import { formatTimestamp, formatDurationSeconds } from '../../utils/formatters';
import { ConfidenceBadge } from './ConfidenceBadge';

export function LatestDiagnosisCard({ diagnosis }) {
  if (!diagnosis) return null;

  const detail = diagnosis.diagnosis || {};
  const primaryFault = detail.primaryFault || {};
  const confidence = detail.confidence || {};

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-900/95 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
      {/* Background glow accent */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-xs uppercase font-bold tracking-wider text-cyan-400 bg-cyan-950/70 border border-cyan-800/50 px-2.5 py-0.5 rounded-md flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
              <span>Active Fault Assessment</span>
            </span>
            <span className="text-xs text-slate-400 font-mono">
              ID: {diagnosis.id}
            </span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-white mt-2 tracking-tight">
            {primaryFault.title || 'Undetermined Equipment State'}
          </h2>

          {primaryFault.faultId && (
            <div className="flex items-center gap-2 mt-1.5">
              <span className="text-xs font-mono text-cyan-300 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                Code: {primaryFault.faultId}
              </span>
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <ConfidenceBadge level={confidence.level} reason={confidence.reason} />
          <Link
            to={`/diagnosis/${encodeURIComponent(diagnosis.id)}`}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 text-xs font-bold border border-slate-700 shadow-md transition-colors"
          >
            <span>View Full Record</span>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
          </Link>
        </div>
      </div>

      {/* Structured Metric Metadata Bar */}
      <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Target Machine</span>
          <Link
            to={`/device/${encodeURIComponent(diagnosis.deviceId || 'ESP32_001')}`}
            className="text-sm font-bold text-cyan-400 font-mono mt-0.5 hover:underline flex items-center gap-1.5"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{diagnosis.deviceId || 'ESP32_001'}</span>
          </Link>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Diagnosis Time</span>
          <div className="mt-0.5 text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>{formatTimestamp(diagnosis.timestamp)}</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Generation Latency</span>
          <div className="mt-0.5 text-xs font-mono font-bold text-amber-300 flex items-center gap-1.5">
            <Timer className="w-3.5 h-3.5 text-amber-400" />
            <span>{formatDurationSeconds(diagnosis.latencySeconds)}</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Diagnostic Engine</span>
          <div className="mt-0.5 text-xs font-mono text-slate-200 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>{detail.model || 'qwen2.5:1.5b'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
