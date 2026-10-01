import React from 'react';

export function StatusBadge({ status = 'ONLINE', type = 'system' }) {
  const isOnline = status.toUpperCase() === 'ONLINE' || status.toUpperCase() === 'COMPLETED';
  const isError = status.toUpperCase() === 'ERROR' || status.toUpperCase() === 'OFFLINE' || status.toUpperCase() === 'CRITICAL';
  const isWarning = status.toUpperCase() === 'WARNING' || status.toUpperCase() === 'DEGRADED';

  let bg = 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
  let dot = 'bg-emerald-500';

  if (isError) {
    bg = 'bg-rose-500/10 border-rose-500/30 text-rose-400';
    dot = 'bg-rose-500 animate-pulse';
  } else if (isWarning) {
    bg = 'bg-amber-500/10 border-amber-500/30 text-amber-400';
    dot = 'bg-amber-500';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${bg}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`}></span>
      <span>{status}</span>
    </span>
  );
}
