import React from 'react';
import { Database, FileText, CheckCircle } from 'lucide-react';
import { formatTelemetryValue } from '../../utils/formatters';

export function EvidenceSection({ evidence }) {
  const list = evidence || [];

  if (list.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">Telemetry Evidence</h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {list.map((item, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between"
          >
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                {item.parameter || 'Parameter'}
              </span>
              <span className="text-base font-extrabold text-white font-mono mt-0.5 block">
                {formatTelemetryValue(item.value, item.unit)}
              </span>
            </div>
            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-800/40">
              {item.type || 'Telemetry'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
