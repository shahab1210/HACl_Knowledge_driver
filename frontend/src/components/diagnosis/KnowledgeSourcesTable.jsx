import React from 'react';
import { BookOpen, HelpCircle } from 'lucide-react';
import { formatSimilarity } from '../../utils/formatters';

export function KnowledgeSourcesTable({ knowledgeSources }) {
  const sources = knowledgeSources || [];

  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
            RAG Grounding Knowledge Sources ({sources.length})
          </h3>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>ChromaDB Vector Store (nomic-embed-text)</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
              <th className="pb-3 w-12 text-center">Rank</th>
              <th className="pb-3">Knowledge Document</th>
              <th className="pb-3">Source Markdown Path</th>
              <th className="pb-3 text-right">Cosine Similarity Metric</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {sources.map((ks, idx) => {
              const sim = ks.similarity !== null && ks.similarity !== undefined ? Number(ks.similarity) : 0;
              const pct = Math.min(100, Math.max(0, sim * 100));

              return (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 text-center font-mono font-bold text-slate-400">
                    #{ks.rank || idx + 1}
                  </td>
                  <td className="py-3 pr-4">
                    <div className="font-semibold text-slate-100">{ks.title || ks.documentId}</div>
                    {ks.chunkId && (
                      <div className="text-[10px] font-mono text-cyan-400/90 mt-0.5">
                        Chunk: {ks.chunkId}
                      </div>
                    )}
                  </td>
                  <td className="py-3 pr-4 font-mono text-slate-400 text-[11px]">
                    {ks.source || 'knowledge-base'}
                  </td>
                  <td className="py-3 text-right">
                    <div className="flex flex-col items-end gap-1">
                      <span className="font-mono font-bold text-emerald-400 text-xs">
                        {sim > 0 ? sim.toFixed(4) : 'N/A'}
                      </span>
                      {sim > 0 && (
                        <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5">
          <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
          <span>Cosine similarity reflects semantic vector proximity between telemetry observations and manual chunks.</span>
        </div>
        <span className="font-mono text-slate-500">Ordered by Rank</span>
      </div>
    </div>
  );
}
