'use client';

import React from 'react';
import { BookOpen, Hash, BarChart3, FileText, CheckCircle2 } from 'lucide-react';
import { CitationItem } from '@/lib/types';

interface SourceInspectorProps {
  citation: CitationItem | null;
}

export const SourceInspector: React.FC<SourceInspectorProps> = ({ citation }) => {
  if (!citation) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
        <BookOpen className="w-10 h-10 mb-3 text-slate-700" />
        <h4 className="text-sm font-semibold text-slate-300 mb-1">Source Inspector</h4>
        <p className="text-xs max-w-xs text-slate-500">
          Click any <span className="text-indigo-400 font-mono">[Page X]</span> citation pill in the chat to inspect its verbatim passage and score breakdown.
        </p>
      </div>
    );
  }

  const bm25Percent = Math.min(100, Math.round(citation.bm25_score * 100));
  const densePercent = Math.min(100, Math.round(citation.dense_score * 100));

  return (
    <div className="p-4 space-y-4 overflow-y-auto h-full">
      {/* Header Info */}
      <div className="border-b border-slate-800 pb-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded-md bg-indigo-950 text-indigo-300 border border-indigo-800/60 font-mono text-xs font-semibold">
              Page {citation.page}
            </span>
            <span className="text-xs text-slate-400 font-medium truncate max-w-[150px]">
              {citation.filename}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            {citation.chunk_id}
          </span>
        </div>
      </div>

      {/* Verbatim Excerpt */}
      <div>
        <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5 flex items-center space-x-1">
          <FileText className="w-3.5 h-3.5 text-indigo-400" />
          <span>Verbatim Source Passage</span>
        </label>
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs leading-relaxed text-slate-300 font-serif italic border-l-4 border-l-indigo-500">
          "{citation.excerpt}"
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="space-y-3 pt-2">
        <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block flex items-center space-x-1">
          <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Retrieval Score Breakdown</span>
        </label>

        {/* BM25 */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400 font-medium">BM25 Lexical Relevance</span>
            <span className="font-mono text-slate-200">{citation.bm25_score.toFixed(3)}</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-sky-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${bm25Percent}%` }}
            />
          </div>
        </div>

        {/* Dense */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400 font-medium">Dense Semantic Similarity</span>
            <span className="font-mono text-slate-200">{citation.dense_score.toFixed(3)}</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-violet-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${densePercent}%` }}
            />
          </div>
        </div>

        {/* RRF Fused */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-300 font-medium">Reciprocal Rank Fusion</p>
            <p className="text-[10px] text-slate-500 font-mono">1 / (60 + r_bm25) + 1 / (60 + r_dense)</p>
          </div>
          <span className="px-2.5 py-1 rounded-md bg-indigo-950 text-indigo-300 border border-indigo-800/60 font-mono text-xs font-bold">
            {citation.rrf_score.toFixed(5)}
          </span>
        </div>
      </div>
    </div>
  );
};
