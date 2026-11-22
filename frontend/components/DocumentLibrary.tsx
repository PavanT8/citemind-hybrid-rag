'use client';

import React, { useState, useRef } from 'react';
import { Upload, FileText, Trash2, Sparkles, Loader2, CheckCircle2 } from 'lucide-react';
import { DocumentInfo } from '@/lib/types';
import { uploadDocument, loadSampleDocument, deleteDocument } from '@/lib/api';

interface DocumentLibraryProps {
  documents: DocumentInfo[];
  onDocumentsChange: () => void;
  selectedDocId: string | null;
  onSelectDoc: (id: string | null) => void;
}

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({
  documents,
  onDocumentsChange,
  selectedDocId,
  onSelectDoc,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingSample, setIsLoadingSample] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErrorMsg('Only PDF files are supported.');
      return;
    }
    setErrorMsg(null);
    setIsUploading(true);
    try {
      await uploadDocument(file);
      onDocumentsChange();
    } catch (err: any) {
      setErrorMsg(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleLoadSample = async () => {
    setErrorMsg(null);
    setIsLoadingSample(true);
    try {
      await loadSampleDocument();
      onDocumentsChange();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load sample paper');
    } finally {
      setIsLoadingSample(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, docId: string) => {
    e.stopPropagation();
    try {
      await deleteDocument(docId);
      if (selectedDocId === docId) {
        onSelectDoc(null);
      }
      onDocumentsChange();
    } catch (err: any) {
      setErrorMsg(err.message || 'Delete failed');
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 p-4">
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-slate-200 tracking-wide uppercase flex items-center justify-between">
          <span>Document Library</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
            {documents.length}
          </span>
        </h2>
      </div>

      {/* 1-Click Sample Paper Button */}
      <button
        onClick={handleLoadSample}
        disabled={isLoadingSample}
        className="w-full mb-3 flex items-center justify-center space-x-2 py-2.5 px-3 rounded-lg bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium text-xs shadow-md shadow-indigo-950 transition disabled:opacity-50"
      >
        {isLoadingSample ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Sparkles className="w-4 h-4 text-amber-300" />
        )}
        <span>Load Sample Paper (1-Click)</span>
      </button>

      {/* Drag & Drop Upload Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-lg p-3 text-center cursor-pointer transition mb-4 bg-slate-950/40"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileUpload(e.target.files[0]);
            }
          }}
        />
        {isUploading ? (
          <div className="flex items-center justify-center space-x-2 py-2 text-indigo-400 text-xs">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Chunking & indexing pages...</span>
          </div>
        ) : (
          <div className="py-2">
            <Upload className="w-5 h-5 mx-auto text-slate-400 mb-1" />
            <p className="text-xs text-slate-300 font-medium">Upload Research PDF</p>
            <p className="text-[10px] text-slate-500">Extracts pages & builds BM25 + dense index</p>
          </div>
        )}
      </div>

      {errorMsg && (
        <div className="mb-3 p-2 bg-rose-950/60 border border-rose-800/80 rounded text-rose-300 text-xs">
          {errorMsg}
        </div>
      )}

      {/* Document List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {documents.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            No papers indexed yet.<br />Click the sample button above or upload a PDF.
          </div>
        ) : (
          documents.map((doc) => {
            const isSelected = selectedDocId === doc.id;
            return (
              <div
                key={doc.id}
                onClick={() => onSelectDoc(isSelected ? null : doc.id)}
                className={`p-2.5 rounded-lg border text-left cursor-pointer transition ${
                  isSelected
                    ? 'bg-indigo-950/60 border-indigo-500/80 shadow-sm'
                    : 'bg-slate-800/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-2 overflow-hidden">
                    <FileText className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    <div className="truncate">
                      <p className="text-xs font-medium text-slate-200 truncate">
                        {doc.filename}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                          {doc.page_count} {doc.page_count === 1 ? 'Page' : 'Pages'}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                          {doc.chunk_count} Chunks
                        </span>
                        {doc.is_sample && (
                          <span className="text-[9px] px-1 py-0.2 rounded bg-amber-950/80 text-amber-300 font-medium border border-amber-800/50">
                            Sample
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, doc.id)}
                    title="Delete document"
                    className="p-1 text-slate-500 hover:text-rose-400 rounded transition shrink-0"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="mt-3 pt-3 border-t border-slate-800 text-[11px] text-slate-500 text-center">
        {selectedDocId ? 'Filtering queries to selected doc' : 'Querying all indexed papers'}
      </div>
    </div>
  );
};
