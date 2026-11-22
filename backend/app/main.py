import os
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.schemas import (
    HealthResponse,
    DocumentInfo,
    QueryRequest,
    QueryResponse,
    QueryMetrics,
    CitationItem,
    EvalHistoryResponse
)
from backend.app.services.pdf_parser import parse_and_chunk_pdf
from backend.app.services.storage import storage_service
from backend.app.services.hybrid_retriever import hybrid_retriever
from backend.app.services.llm_client import llm_client
from backend.app.services.evaluator import evaluator
from backend.app.sample_data.generate_sample_pdf import generate_sample_pdf


SAMPLE_PDF_PATH = os.path.join(
    os.path.dirname(__file__), "sample_data", "sample_paper.pdf"
)


def index_sample_paper() -> DocumentInfo:
    """Ensures sample paper exists on disk and is indexed in storage."""
    if not os.path.exists(SAMPLE_PDF_PATH):
        generate_sample_pdf(SAMPLE_PDF_PATH)

    existing = storage_service.get_document("doc_sample_paper")
    if existing:
        return existing

    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    page_count, chunks = parse_and_chunk_pdf(
        pdf_bytes=pdf_bytes,
        doc_id="doc_sample_paper",
        filename="sample_paper.pdf"
    )

    doc_info = DocumentInfo(
        id="doc_sample_paper",
        filename="sample_paper.pdf",
        page_count=page_count,
        chunk_count=len(chunks),
        created_at=datetime.now(timezone.utc).isoformat(),
        is_sample=True
    )
    storage_service.add_document(doc_info, chunks)
    hybrid_retriever.ensure_chunk_embeddings(chunks)
    return doc_info


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure sample paper is pre-indexed for 1-click zero-setup testing
    try:
        index_sample_paper()
    except Exception as e:
        print(f"[Warning] Failed to pre-index sample paper on startup: {e}")
    yield


app = FastAPI(
    title="CiteMind Hybrid RAG API",
    description="Academic Hybrid RAG Assistant with inline citations and real-time evaluation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def get_health():
    return HealthResponse(
        status="ok",
        provider=settings.LLM_PROVIDER,
        documents_indexed=len(storage_service.list_documents()),
        version="1.0.0"
    )


@app.get("/api/documents", response_model=List[DocumentInfo])
def list_documents():
    return storage_service.list_documents()


@app.post("/api/documents/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported."
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    page_count, chunks = parse_and_chunk_pdf(
        pdf_bytes=content,
        doc_id=doc_id,
        filename=file.filename
    )

    doc_info = DocumentInfo(
        id=doc_id,
        filename=file.filename,
        page_count=page_count,
        chunk_count=len(chunks),
        created_at=datetime.now(timezone.utc).isoformat(),
        is_sample=False
    )
    storage_service.add_document(doc_info, chunks)
    hybrid_retriever.ensure_chunk_embeddings(chunks)
    return doc_info


@app.post("/api/documents/load-sample", response_model=DocumentInfo)
def load_sample():
    doc_info = index_sample_paper()
    return doc_info


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str):
    success = storage_service.delete_document(doc_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found."
        )
    return {"status": "deleted", "doc_id": doc_id}


@app.post("/api/query", response_model=QueryResponse)
def query_rag(req: QueryRequest):
    chunks = storage_service.get_all_chunks(req.doc_ids)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No indexed documents found. Please index a document or load the sample paper first."
        )

    # 1. Retrieval
    citations_data, retrieval_ms = hybrid_retriever.retrieve(
        query=req.question,
        chunks=chunks,
        mode=req.mode,
        top_k=req.top_k
    )

    # 2. Generation with inline [Page X]
    answer, generation_ms = llm_client.generate_grounded_answer(
        question=req.question,
        citations=citations_data
    )

    # 3. Evaluation Metrics
    total_ms = round(retrieval_ms + generation_ms, 1)
    citation_coverage = evaluator.calculate_citation_coverage(answer)
    faithfulness = evaluator.calculate_faithfulness(req.question, answer, citations_data)

    if req.run_eval and settings.ENABLE_EVAL_LOGGING:
        storage_service.log_evaluation(
            question=req.question,
            mode=req.mode,
            faithfulness=faithfulness,
            citation_coverage=citation_coverage,
            retrieval_ms=retrieval_ms,
            generation_ms=generation_ms,
            total_ms=total_ms
        )

    citations = [
        CitationItem(
            chunk_id=c["chunk_id"],
            doc_id=c["doc_id"],
            filename=c["filename"],
            page=c["page"],
            excerpt=c["excerpt"],
            bm25_score=c["bm25_score"],
            dense_score=c["dense_score"],
            rrf_score=c["rrf_score"]
        ) for c in citations_data
    ]

    metrics = QueryMetrics(
        faithfulness=faithfulness,
        citation_coverage=citation_coverage,
        retrieval_ms=retrieval_ms,
        generation_ms=generation_ms,
        total_ms=total_ms,
        mode=req.mode
    )

    return QueryResponse(
        question=req.question,
        answer=answer,
        citations=citations,
        metrics=metrics
    )


@app.get("/api/eval/history", response_model=EvalHistoryResponse)
def get_eval_history(limit: int = 50):
    history = storage_service.get_eval_history(limit=limit)
    summary = storage_service.get_summary_by_mode()
    return EvalHistoryResponse(
        total_queries=len(history),
        history=history,
        summary_by_mode=summary
    )
