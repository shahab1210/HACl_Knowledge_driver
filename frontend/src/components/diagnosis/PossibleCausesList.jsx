import React from 'react';
import { HelpCircle } from 'lucide-react';

export function PossibleCausesList({ possibleCauses }) {
  const causes = possibleCauses || [];

  if (causes.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <HelpCircle className="w-5 h-5 text-amber-400" />
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
          Possible Root Causes
        </h3>
      </div>

      <ol className="space-y-2.5 list-decimal list-inside text-xs text-slate-300">
        {causes.map((cause, idx) => (
          <li key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 leading-relaxed">
            {cause}
          </li>
        ))}
      </ol>
    </div>
  );
}
