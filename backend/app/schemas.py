from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    status: str = "ok"
    provider: str
    documents_indexed: int
    version: str = "1.0.0"


class DocumentInfo(BaseModel):
    id: str
    filename: str
    page_count: int
    chunk_count: int
    created_at: str
    is_sample: Optional[bool] = False


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Research question to answer")
    doc_ids: Optional[List[str]] = Field(None, description="List of document IDs to query, or null for all")
    mode: str = Field("hybrid", pattern="^(hybrid|dense|bm25)$", description="Retrieval mode")
    top_k: int = Field(4, ge=1, le=20, description="Number of top chunks to retrieve")
    run_eval: bool = Field(True, description="Whether to log and compute evaluation metrics")


class CitationItem(BaseModel):
    chunk_id: str
    doc_id: str
    filename: str
    page: int
    excerpt: str
    bm25_score: float = 0.0
    dense_score: float = 0.0
    rrf_score: float = 0.0


class QueryMetrics(BaseModel):
    faithfulness: float
    citation_coverage: float
    retrieval_ms: float
    generation_ms: float
    total_ms: float
    mode: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[CitationItem]
    metrics: QueryMetrics


class EvalHistoryItem(BaseModel):
    id: int
    timestamp: str
    question: str
    mode: str
    faithfulness: float
    citation_coverage: float
    retrieval_ms: float
    generation_ms: float
    total_ms: float


class EvalSummary(BaseModel):
    count: int = 0
    avg_faithfulness: float = 0.0
    avg_citation_coverage: float = 0.0
    avg_total_ms: float = 0.0


class EvalHistoryResponse(BaseModel):
    total_queries: int
    history: List[EvalHistoryItem]
    summary_by_mode: Dict[str, EvalSummary]
