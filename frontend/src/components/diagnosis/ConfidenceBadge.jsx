import React from 'react';
import { getConfidenceStyle } from '../../utils/severity';

export function ConfidenceBadge({ level, reason }) {
  const style = getConfidenceStyle(level);

  return (
    <div className="inline-flex items-center gap-2">
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${style.bg} ${style.border} ${style.text}`}>
        <span className={`w-2 h-2 rounded-full ${style.dot}`}></span>
        <span>{style.label} CONFIDENCE</span>
      </span>
      {reason && (
        <span className="text-xs text-slate-400 font-medium hidden sm:inline truncate max-w-xs">
          {reason}
        </span>
      )}
    </div>
  );
}
