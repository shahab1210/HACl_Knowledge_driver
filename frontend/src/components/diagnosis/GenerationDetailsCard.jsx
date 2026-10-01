import React from 'react';
import { Cpu, Zap, Timer, Layers } from 'lucide-react';
import { formatDurationNanos } from '../../utils/formatters';

export function GenerationDetailsCard({ generationDetails, model }) {
  if (!generationDetails) return null;

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
            AI Inference Metadata
          </h3>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 px-2 py-0.5 rounded">
          {model || 'qwen2.5:1.5b'}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-sans">Prompt Tokens</span>
          <span className="text-sm font-bold text-white mt-1 block">
            {generationDetails.promptEvalCount ?? 'N/A'}
          </span>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-sans">Eval Tokens</span>
          <span className="text-sm font-bold text-white mt-1 block">
            {generationDetails.evalCount ?? 'N/A'}
          </span>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-sans">Eval Duration</span>
          <span className="text-sm font-bold text-cyan-300 mt-1 block">
            {formatDurationNanos(generationDetails.evalDuration)}
          </span>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-sans">Total Latency</span>
          <span className="text-sm font-bold text-emerald-400 mt-1 block">
            {formatDurationNanos(generationDetails.totalDuration)}
          </span>
        </div>
      </div>
    </div>
  );
}
