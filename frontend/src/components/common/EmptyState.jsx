import React from 'react';
import { Activity, PlusCircle } from 'lucide-react';

export function EmptyState({
  title = 'No Diagnoses Available',
  message = 'The database does not contain any diagnosis records yet. Submit telemetry or stream data via MQTT to generate an AI diagnosis.',
  onAction,
  actionLabel = 'Run Manual Diagnosis'
}) {
  return (
    <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-10 text-center flex flex-col items-center justify-center max-w-xl mx-auto my-8">
      <div className="w-14 h-14 rounded-2xl bg-cyan-950/40 border border-cyan-800/40 flex items-center justify-center text-cyan-400 mb-4 shadow-inner">
        <Activity className="w-7 h-7" />
      </div>
      <h3 className="text-lg font-bold text-slate-100">{title}</h3>
      <p className="text-sm text-slate-400 mt-2 max-w-md leading-relaxed">{message}</p>
      {onAction && (
        <button
          onClick={onAction}
          className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-cyan-950/50 transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <PlusCircle className="w-4 h-4" />
          <span>{actionLabel}</span>
        </button>
      )}
    </div>
  );
}
