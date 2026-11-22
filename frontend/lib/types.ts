export interface HealthResponse {
  status: string;
  provider: string;
  documents_indexed: number;
  version: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  page_count: number;
  chunk_count: number;
  created_at: string;
  is_sample?: boolean;
}

export interface CitationItem {
  chunk_id: string;
  doc_id: string;
  filename: string;
  page: number;
  excerpt: string;
  bm25_score: number;
  dense_score: number;
  rrf_score: number;
}

export interface QueryMetrics {
  faithfulness: number;
  citation_coverage: number;
  retrieval_ms: number;
  generation_ms: number;
  total_ms: number;
  mode: string;
}

export interface QueryResponse {
  question: string;
  answer: string;
  citations: CitationItem[];
  metrics: QueryMetrics;
}

export interface EvalHistoryItem {
  id: number;
  timestamp: string;
  question: string;
  mode: string;
  faithfulness: number;
  citation_coverage: number;
  retrieval_ms: number;
  generation_ms: number;
  total_ms: number;
}

export interface EvalSummary {
  count: number;
  avg_faithfulness: number;
  avg_citation_coverage: number;
  avg_total_ms: number;
}

export interface EvalHistoryResponse {
  total_queries: number;
  history: EvalHistoryItem[];
  summary_by_mode: Record<string, EvalSummary>;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: CitationItem[];
  metrics?: QueryMetrics;
  timestamp: string;
}
