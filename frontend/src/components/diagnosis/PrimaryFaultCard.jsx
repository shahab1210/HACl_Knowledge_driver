import React from 'react';
import { AlertCircle, Target, CheckCircle } from 'lucide-react';
import { formatSimilarity } from '../../utils/formatters';

export function PrimaryFaultCard({ primaryFault, query, rawLlmResponse }) {
  if (!primaryFault && !rawLlmResponse && !query) {
    return null;
  }

  const fault = primaryFault || {};

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-cyan-400" />
          <h3 className="text-base font-bold text-white">Diagnostic Analysis & Explanation</h3>
        </div>
        {fault.similarity !== undefined && fault.similarity !== null && (
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
            Grounding Similarity: {formatSimilarity(fault.similarity)}
          </span>
        )}
      </div>

      {fault.title && (
        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-white">{fault.title}</span>
            {fault.faultId && (
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/50 px-2 py-0.5 rounded">
                {fault.faultId}
              </span>
            )}
          </div>
          {(fault.explanation || fault.description) && (
            <p className="text-xs text-slate-300 mt-2 leading-relaxed">
              {fault.explanation || fault.description}
            </p>
          )}
        </div>
      )}

      {query && (
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/60">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Telemetry Observation Query
          </span>
          <p className="text-xs font-mono text-cyan-200/90 leading-relaxed">{query}</p>
        </div>
      )}

      {rawLlmResponse && (
        <div className="prose prose-invert max-w-none text-xs text-slate-300 leading-relaxed space-y-3 whitespace-pre-line bg-slate-950/40 p-4 rounded-xl border border-slate-800/40 font-sans">
          {rawLlmResponse}
        </div>
      )}
    </div>
  );
}

