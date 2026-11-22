import {
  HealthResponse,
  DocumentInfo,
  QueryResponse,
  EvalHistoryResponse,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_BASE}/api/documents`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to fetch documents: ${res.statusText}`);
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed: ${res.statusText}`);
  }
  return res.json();
}

export async function loadSampleDocument(): Promise<DocumentInfo> {
  const res = await fetch(`${API_BASE}/api/documents/load-sample`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Sample loading failed: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteDocument(docId: string): Promise<{ status: string; doc_id: string }> {
  const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`Delete failed: ${res.statusText}`);
  }
  return res.json();
}

export async function sendQuery(params: {
  question: string;
  doc_ids?: string[] | null;
  mode: 'hybrid' | 'dense' | 'bm25';
  top_k?: number;
  run_eval?: boolean;
}): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Query failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEvalHistory(): Promise<EvalHistoryResponse> {
  const res = await fetch(`${API_BASE}/api/eval/history`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to fetch eval history: ${res.statusText}`);
  }
  return res.json();
}
