import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export function ErrorAlert({ title = 'Error Loading Data', message, onRetry }) {
  return (
    <div className="bg-rose-950/40 border border-rose-800/60 rounded-xl p-5 text-rose-200">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-rose-400 mt-0.5 shrink-0" />
        <div className="flex-1">
          <h4 className="font-semibold text-rose-100 text-sm">{title}</h4>
          <p className="text-xs text-rose-300/90 mt-1 leading-relaxed">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-900/50 hover:bg-rose-900 text-rose-100 rounded-lg text-xs font-medium border border-rose-700/50 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Request</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
