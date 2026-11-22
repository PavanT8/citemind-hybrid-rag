'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/Navbar';
import { DocumentLibrary } from '@/components/DocumentLibrary';
import { ResearchChat } from '@/components/ResearchChat';
import { SourceInspector } from '@/components/SourceInspector';
import { EvalDashboard } from '@/components/EvalDashboard';
import { HealthResponse, DocumentInfo, CitationItem } from '@/lib/types';
import { fetchHealth, fetchDocuments } from '@/lib/api';
import { FileSearch, BarChart2 } from 'lucide-react';

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [backendWaking, setBackendWaking] = useState(false);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [activeCitation, setActiveCitation] = useState<CitationItem | null>(null);
  const [rightTab, setRightTab] = useState<'inspector' | 'eval'>('inspector');
  const [evalUpdateCounter, setEvalUpdateCounter] = useState(0);

  const checkHealth = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
      setBackendWaking(false);
    } catch {
      setBackendWaking(true);
    }
  };

  const loadDocuments = async () => {
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch (e) {
      console.warn('Failed to fetch documents', e);
    }
  };

  useEffect(() => {
    checkHealth();
    loadDocuments();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleCitationClick = (citation: CitationItem) => {
    setActiveCitation(citation);
    setRightTab('inspector');
  };

  const handleQueryComplete = () => {
    setEvalUpdateCounter((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950 text-slate-100">
      <Navbar
        health={health}
        backendWaking={backendWaking}
        onRefreshHealth={() => {
          checkHealth();
          loadDocuments();
        }}
      />

      {/* Main 3-Panel Workspace */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Panel: Document Library (25%) */}
        <section className="w-1/4 min-w-[260px] max-w-[340px] h-full hidden md:block">
          <DocumentLibrary
            documents={documents}
            onDocumentsChange={loadDocuments}
            selectedDocId={selectedDocId}
            onSelectDoc={setSelectedDocId}
          />
        </section>

        {/* Center Panel: Research Chat (45%) */}
        <section className="flex-1 h-full border-r border-slate-800 flex flex-col">
          <ResearchChat
            selectedDocId={selectedDocId}
            onCitationClick={handleCitationClick}
            onQueryComplete={handleQueryComplete}
          />
        </section>

        {/* Right Panel: Source Inspector & Eval Dashboard (30%) */}
        <section className="w-[380px] h-full flex flex-col bg-slate-900 hidden lg:flex">
          {/* Tabs */}
          <div className="flex border-b border-slate-800 bg-slate-950/60 p-1">
            <button
              onClick={() => setRightTab('inspector')}
              className={`flex-1 py-2 flex items-center justify-center space-x-1.5 rounded-md text-xs font-medium transition ${
                rightTab === 'inspector'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileSearch className="w-3.5 h-3.5 text-indigo-400" />
              <span>Source Inspector</span>
            </button>
            <button
              onClick={() => setRightTab('eval')}
              className={`flex-1 py-2 flex items-center justify-center space-x-1.5 rounded-md text-xs font-medium transition ${
                rightTab === 'eval'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BarChart2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Eval Dashboard</span>
            </button>
          </div>

          <div className="flex-1 overflow-hidden">
            {rightTab === 'inspector' ? (
              <SourceInspector citation={activeCitation} />
            ) : (
              <EvalDashboard lastUpdated={evalUpdateCounter} />
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
