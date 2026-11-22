'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Layers, Search, Zap, Loader2 } from 'lucide-react';
import { ChatMessage, CitationItem, QueryResponse } from '@/lib/types';
import { sendQuery } from '@/lib/api';

interface ResearchChatProps {
  selectedDocId: string | null;
  onCitationClick: (citation: CitationItem) => void;
  onQueryComplete: () => void;
}

const STARTER_QUESTIONS = [
  "What is the mathematical formulation of Reciprocal Rank Fusion?",
  "What are the benchmark results comparing BM25, Dense, and Hybrid?",
  "Why do large language models hallucinate in niche scientific domains?",
  "What is the memory consumption of CiteMind on Render free tier?",
];

export const ResearchChat: React.FC<ResearchChatProps> = ({
  selectedDocId,
  onCitationClick,
  onQueryComplete,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<'hybrid' | 'dense' | 'bm25'>('hybrid');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (questionText?: string) => {
    const q = (questionText || input).trim();
    if (!q || isLoading) return;

    setInput('');
    const userMsg: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res: QueryResponse = await sendQuery({
        question: q,
        doc_ids: selectedDocId ? [selectedDocId] : null,
        mode: mode,
        top_k: 4,
        run_eval: true,
      });

      const assistantMsg: ChatMessage = {
        id: `msg_a_${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        citations: res.citations,
        metrics: res.metrics,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      onQueryComplete();
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `msg_err_${Date.now()}`,
        sender: 'assistant',
        text: `Error: ${err.message || 'Failed to process query'}. Ensure backend is online and papers are indexed.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to render text with clickable [Page X] pills
  const renderFormattedText = (text: string, citations?: CitationItem[]) => {
    const parts = text.split(/(\[Page\s+\d+\])/g);
    return parts.map((part, idx) => {
      const match = part.match(/\[Page\s+(\d+)\]/);
      if (match) {
        const pageNum = parseInt(match[1], 10);
        // Find matching citation for this page
        const matchedCitation = citations?.find((c) => c.page === pageNum) || citations?.[0];

        return (
          <button
            key={idx}
            onClick={() => matchedCitation && onCitationClick(matchedCitation)}
            className="inline-flex items-center mx-1 px-1.5 py-0.5 rounded text-[11px] font-mono font-semibold bg-indigo-900/80 text-indigo-300 border border-indigo-700/60 hover:bg-indigo-700 hover:text-white transition shadow-sm"
            title={`Click to inspect verbatim source excerpt on Page ${pageNum}`}
          >
            {part}
          </button>
        );
      }
      return <span key={idx}>{part}</span>;
    });
  };

  return (
    <div className="flex flex-col h-full bg-slate-950">
      {/* Mode Selector Header */}
      <div className="px-6 py-3 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between">
        <div className="flex items-center space-x-1 bg-slate-800/80 p-1 rounded-lg border border-slate-700/80 text-xs">
          <button
            onClick={() => setMode('hybrid')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition font-medium ${
              mode === 'hybrid'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Hybrid (RRF)</span>
          </button>
          <button
            onClick={() => setMode('dense')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition font-medium ${
              mode === 'dense'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Dense Vector</span>
          </button>
          <button
            onClick={() => setMode('bm25')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition font-medium ${
              mode === 'bm25'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            <span>BM25 Keyword</span>
          </button>
        </div>

        <span className="text-xs text-slate-500 font-mono hidden sm:inline">
          RRF Formula: 1 / (60 + rank)
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center mb-3">
              <Layers className="w-6 h-6 text-indigo-400" />
            </div>
            <h3 className="text-base font-semibold text-slate-200 mb-1">
              Academic Research Synthesis
            </h3>
            <p className="text-xs text-slate-400 max-w-md mb-6">
              Ask questions across indexed research papers. Answers include verified inline <span className="text-indigo-400 font-mono">[Page X]</span> citations linking to source text.
            </p>

            <div className="w-full max-w-lg space-y-2">
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Suggested Research Queries:
              </p>
              {STARTER_QUESTIONS.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  className="w-full text-left p-2.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-600/60 hover:bg-slate-800/80 transition text-xs text-slate-300"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${
                msg.sender === 'user' ? 'items-end' : 'items-start'
              }`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                }`}
              >
                {msg.sender === 'assistant'
                  ? renderFormattedText(msg.text, msg.citations)
                  : msg.text}
              </div>

              {/* Metrics bar under assistant message */}
              {msg.sender === 'assistant' && msg.metrics && (
                <div className="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-400 font-mono px-1">
                  <span>Mode: {msg.metrics.mode}</span>
                  <span>•</span>
                  <span>Ret: {msg.metrics.retrieval_ms}ms</span>
                  <span>•</span>
                  <span>Gen: {msg.metrics.generation_ms}ms</span>
                  <span>•</span>
                  <span className="text-emerald-400">
                    Faithfulness: {Math.round(msg.metrics.faithfulness * 100)}%
                  </span>
                  <span>•</span>
                  <span>Coverage: {Math.round(msg.metrics.citation_coverage * 100)}%</span>
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex items-center space-x-2 text-indigo-400 text-xs py-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Fusing sparse & dense indices, synthesizing grounded answer...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/60">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your research papers..."
            className="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-lg px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 outline-none transition"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-medium text-sm transition flex items-center justify-center shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
