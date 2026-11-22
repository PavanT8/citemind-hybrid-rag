'use client';

import React from 'react';
import { BookOpen, Github, Cpu, Activity, RefreshCw } from 'lucide-react';
import { HealthResponse } from '@/lib/types';

interface NavbarProps {
  health: HealthResponse | null;
  backendWaking: boolean;
  onRefreshHealth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  backendWaking,
  onRefreshHealth,
}) => {
  return (
    <header className="h-14 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-4 flex items-center justify-between z-20">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <BookOpen className="w-4 h-4 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold text-white tracking-tight">CiteMind</h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800/60 font-mono">
              Hybrid RAG
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-3 text-xs">
        {/* Backend Cold-Start or Status Indicator */}
        {backendWaking ? (
          <div className="flex items-center space-x-2 px-2.5 py-1 rounded-md bg-amber-950/60 border border-amber-800/60 text-amber-300 animate-pulse">
            <Activity className="w-3.5 h-3.5 animate-spin" />
            <span>Render Free Tier Waking Up (~30s)...</span>
          </div>
        ) : health ? (
          <div className="flex items-center space-x-2 px-2.5 py-1 rounded-md bg-emerald-950/60 border border-emerald-800/60 text-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Online</span>
            <span className="text-slate-500">|</span>
            <span className="font-mono text-emerald-200 capitalize">{health.provider}</span>
            <span className="text-slate-500">|</span>
            <span>{health.documents_indexed} Docs</span>
          </div>
        ) : (
          <button
            onClick={onRefreshHealth}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-rose-950/60 border border-rose-800/60 text-rose-300 hover:bg-rose-900/60 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Backend Offline (Retry)</span>
          </button>
        )}

        {/* GitHub link */}
        <a
          href="https://github.com/PavanT8/citemind-hybrid-rag"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-1 px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
        >
          <Github className="w-4 h-4" />
          <span>GitHub</span>
        </a>
      </div>
    </header>
  );
};
