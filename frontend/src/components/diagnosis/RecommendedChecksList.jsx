import React from 'react';
import { CheckSquare } from 'lucide-react';

export function RecommendedChecksList({ recommendedChecks, additionalInfo }) {
  const checks = recommendedChecks || [];
  const addInfo = additionalInfo || [];

  if (checks.length === 0 && addInfo.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <CheckSquare className="w-5 h-5 text-emerald-400" />
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
          Recommended Actions & Considerations
        </h3>
      </div>

      <div className="space-y-3">
        {checks.map((check, idx) => (
          <div key={`chk-${idx}`} className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="w-5 h-5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shrink-0 text-xs font-bold mt-0.5">
              ✓
            </span>
            <p className="text-xs text-slate-200 leading-relaxed">{check}</p>
          </div>
        ))}

        {addInfo.map((info, idx) => (
          <div key={`info-${idx}`} className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="w-5 h-5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center shrink-0 text-xs font-bold mt-0.5">
              i
            </span>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">{info}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
