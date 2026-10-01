import React from 'react';
import { Layers } from 'lucide-react';
import { formatSimilarity } from '../../utils/formatters';

export function AlternativeFaultsList({ alternativeFaults }) {
  const list = alternativeFaults || [];

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Layers className="w-5 h-5 text-indigo-400" />
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">Alternative Fault Candidates</h3>
      </div>

      {list.length === 0 ? (
        <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/40 text-xs text-slate-400 italic">
          No alternative faults identified. Primary fault diagnosis has dominant confidence.
        </div>
      ) : (
        <div className="space-y-3">
          {list.map((alt, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition-colors flex items-center justify-between gap-4"
            >
              <div>
                <h4 className="text-sm font-semibold text-slate-200">{alt.title || 'Candidate Fault'}</h4>
                {alt.faultId && (
                  <span className="text-xs font-mono text-slate-400">Code: {alt.faultId}</span>
                )}
              </div>
              {alt.similarity && (
                <span className="text-xs font-mono text-indigo-300 bg-indigo-950/50 border border-indigo-800/40 px-2.5 py-1 rounded">
                  {formatSimilarity(alt.similarity)}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
