import React from 'react';
import { Link } from 'react-router-dom';
import { History, ArrowRight, Clock, Cpu, ShieldCheck } from 'lucide-react';
import { formatTimestamp, formatDurationSeconds, formatTelemetryValue } from '../../utils/formatters';
import { ConfidenceBadge } from './ConfidenceBadge';

export function DiagnosisHistoryTable({ history = [], title = 'Diagnosis History Records' }) {
  if (!history || history.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-center">
        <span className="text-xs text-slate-400 italic">No historical diagnosis records found.</span>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
            {title} ({history.length})
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">Persisted in PostgreSQL</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
              <th className="pb-3">Diagnosis ID & Timestamp</th>
              <th className="pb-3">Detected Primary Fault</th>
              <th className="pb-3">Confidence</th>
              <th className="pb-3">Telemetry Snapshot</th>
              <th className="pb-3">AI Latency</th>
              <th className="pb-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {history.map((record) => {
              const det = record.diagnosis || {};
              const pf = det.primaryFault || {};
              const conf = det.confidence || {};
              const tel = record.telemetry || {};

              return (
                <tr key={record.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3.5 pr-4">
                    <div className="font-mono font-bold text-cyan-400 text-xs">{record.id}</div>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                      <Clock className="w-3 h-3 text-slate-500" />
                      <span>{formatTimestamp(record.timestamp)}</span>
                    </div>
                  </td>

                  <td className="py-3.5 pr-4">
                    <div className="font-semibold text-white text-xs">{pf.title || 'Undetermined Fault'}</div>
                    {pf.faultId && (
                      <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                        Code: {pf.faultId}
                      </div>
                    )}
                  </td>

                  <td className="py-3.5 pr-4">
                    <ConfidenceBadge level={conf.level} />
                  </td>

                  <td className="py-3.5 pr-4 font-mono text-[11px] text-slate-300">
                    <div className="flex items-center gap-2">
                      <span className="text-rose-400">T: {formatTelemetryValue(tel.temperature, '°C')}</span>
                      <span className="text-amber-400">V: {formatTelemetryValue(tel.vibration, 'mm/s')}</span>
                      <span className="text-cyan-400">I: {formatTelemetryValue(tel.current, 'A')}</span>
                    </div>
                  </td>

                  <td className="py-3.5 pr-4 font-mono text-slate-300">
                    {formatDurationSeconds(record.latencySeconds)}
                  </td>

                  <td className="py-3.5 text-right">
                    <Link
                      to={`/diagnosis/${encodeURIComponent(record.id)}`}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold border border-slate-700 transition-colors"
                    >
                      <span>View</span>
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
