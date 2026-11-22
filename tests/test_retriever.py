import pytest
from backend.app.services.pdf_parser import Chunk
from backend.app.services.hybrid_retriever import HybridRetriever


def test_rrf_scoring_math():
    retriever = HybridRetriever()

    chunks = [
        Chunk("c1", "doc1", "paper.pdf", 1, "Reciprocal Rank Fusion combines sparse BM25 scores and dense vectors."),
        Chunk("c2", "doc1", "paper.pdf", 2, "Dense retrieval uses neural embeddings and cosine similarity."),
        Chunk("c3", "doc1", "paper.pdf", 3, "BM25 is a term matching algorithm based on term frequency and IDF."),
    ]

    # Test Hybrid mode
    results, latency = retriever.retrieve(
        query="Reciprocal Rank Fusion BM25",
        chunks=chunks,
        mode="hybrid",
        top_k=2
    )

    assert len(results) == 2
    assert latency >= 0.0
    for r in results:
        assert "chunk_id" in r
        assert "page" in r
        assert "rrf_score" in r
        assert "bm25_score" in r
        assert "dense_score" in r
        assert r["rrf_score"] > 0


def test_retrieval_modes():
    retriever = HybridRetriever()
    chunks = [
        Chunk("c1", "doc1", "paper.pdf", 1, "Quantum computing uses superposition and qubits."),
        Chunk("c2", "doc1", "paper.pdf", 2, "Convolutional neural networks process image matrices."),
    ]

    # BM25 mode
    res_bm25, _ = retriever.retrieve("qubits superposition", chunks, mode="bm25", top_k=1)
    assert len(res_bm25) == 1
    assert res_bm25[0]["chunk_id"] == "c1"

    # Dense mode
    res_dense, _ = retriever.retrieve("qubits superposition", chunks, mode="dense", top_k=1)
    assert len(res_dense) == 1
