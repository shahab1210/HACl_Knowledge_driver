import React from 'react';

export function LoadingSkeleton({ lines = 3, className = '' }) {
  return (
    <div className={`space-y-3 animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-slate-800 rounded"
          style={{ width: `${85 - (i % 3) * 15}%` }}
        />
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="h-4 bg-slate-800 rounded w-1/4"></div>
        <div className="h-6 bg-slate-800 rounded-full w-20"></div>
      </div>
      <div className="h-8 bg-slate-800 rounded w-1/2"></div>
      <div className="space-y-2 pt-2">
        <div className="h-3 bg-slate-800 rounded w-3/4"></div>
        <div className="h-3 bg-slate-800 rounded w-5/6"></div>
      </div>
    </div>
  );
}
