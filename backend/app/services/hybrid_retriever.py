import re
import time
import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from rank_bm25 import BM25Okapi

try:
    from app.config import settings
    from app.services.pdf_parser import Chunk
except ImportError:
    from backend.app.config import settings
    from backend.app.services.pdf_parser import Chunk

logger = logging.getLogger(__name__)


def tokenize(text: str) -> List[str]:
    return re.findall(r'\b\w+\b', text.lower())


class HybridRetriever:
    def __init__(self):
        # Cache chunk embeddings: chunk_id -> np.ndarray
        self.embedding_cache: Dict[str, np.ndarray] = {}

    def _get_embedding(self, text: str) -> np.ndarray:
        """Fetch dense embedding using Google GenAI or LM Studio."""
        if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                # Official google-genai embed syntax
                result = client.models.embed_content(
                    model=settings.GEMINI_EMBED_MODEL,
                    contents=text
                )
                embedding_values = result.embedding.values
                vec = np.array(embedding_values, dtype=np.float32)
                norm = np.linalg.norm(vec)
                return vec / (norm + 1e-9)
            except Exception as e:
                logger.warning(f"Google GenAI embedding failed ({e}), using pseudo-semantic fallback.")
                return self._pseudo_semantic_vector(text)
        elif settings.LLM_PROVIDER == "lmstudio":
            try:
                import httpx
                resp = httpx.post(
                    f"{settings.LMSTUDIO_BASE_URL}/embeddings",
                    json={"model": settings.LMSTUDIO_EMBED_MODEL, "input": text},
                    timeout=5.0
                )
                if resp.status_code == 200:
                    vec = np.array(resp.json()["data"][0]["embedding"], dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    return vec / (norm + 1e-9)
            except Exception as e:
                logger.warning(f"LM Studio embedding failed ({e}), using pseudo-semantic fallback.")
                return self._pseudo_semantic_vector(text)

        return self._pseudo_semantic_vector(text)

    def _pseudo_semantic_vector(self, text: str, dim: int = 128) -> np.ndarray:
        """Deterministic pseudo-semantic vector for fallback / offline test without quota."""
        np.random.seed(abs(hash(text[:100])) % (2**31))
        vec = np.random.randn(dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-9)

    def ensure_chunk_embeddings(self, chunks: List[Chunk]):
        for chunk in chunks:
            if chunk.chunk_id not in self.embedding_cache:
                self.embedding_cache[chunk.chunk_id] = self._get_embedding(chunk.text)

    def retrieve(
        self,
        query: str,
        chunks: List[Chunk],
        mode: str = "hybrid",
        top_k: int = 4,
        rrf_k: int = 60
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Executes BM25, Dense Cosine, or Hybrid RRF retrieval over the given chunks.
        Returns: (ranked_results, retrieval_latency_ms)
        """
        start_time = time.perf_counter()
        if not chunks:
            return [], 0.0

        self.ensure_chunk_embeddings(chunks)

        # 1. BM25 Search
        tokenized_corpus = [tokenize(c.text) for c in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = tokenize(query)
        bm25_scores = bm25.get_scores(tokenized_query)

        # Normalize BM25 scores to [0, 1] for display
        max_bm25 = np.max(bm25_scores) if len(bm25_scores) > 0 and np.max(bm25_scores) > 0 else 1.0
        norm_bm25 = [float(s / max_bm25) for s in bm25_scores]

        # BM25 rank order (0-indexed rank)
        bm25_ranked_indices = np.argsort(bm25_scores)[::-1]
        bm25_rank_map = {idx: rank + 1 for rank, idx in enumerate(bm25_ranked_indices)}

        # 2. Dense Vector Search
        query_vec = self._get_embedding(query)
        dense_scores = []
        for c in chunks:
            chunk_vec = self.embedding_cache.get(c.chunk_id)
            if chunk_vec is not None:
                sim = float(np.dot(query_vec, chunk_vec))
                dense_scores.append(max(0.0, sim))
            else:
                dense_scores.append(0.0)

        # Dense rank order (1-indexed rank)
        dense_ranked_indices = np.argsort(dense_scores)[::-1]
        dense_rank_map = {idx: rank + 1 for rank, idx in enumerate(dense_ranked_indices)}

        # 3. Fusion or Single-mode selection
        candidate_items = []
        for idx, chunk in enumerate(chunks):
            r_bm25 = bm25_rank_map[idx]
            r_dense = dense_rank_map[idx]

            # Reciprocal Rank Fusion: 1 / (k + rank)
            rrf_score = (1.0 / (rrf_k + r_bm25)) + (1.0 / (rrf_k + r_dense))

            candidate_items.append({
                "chunk": chunk,
                "bm25_score": round(norm_bm25[idx], 4),
                "dense_score": round(float(dense_scores[idx]), 4),
                "rrf_score": round(float(rrf_score), 5),
                "raw_bm25": float(bm25_scores[idx]),
                "raw_dense": float(dense_scores[idx]),
                "bm25_rank": r_bm25,
                "dense_rank": r_dense
            })

        # Sort according to selected mode
        if mode == "bm25":
            candidate_items.sort(key=lambda x: x["raw_bm25"], reverse=True)
        elif mode == "dense":
            candidate_items.sort(key=lambda x: x["raw_dense"], reverse=True)
        else:  # "hybrid"
            candidate_items.sort(key=lambda x: x["rrf_score"], reverse=True)

        top_candidates = candidate_items[:top_k]

        results = []
        for item in top_candidates:
            c = item["chunk"]
            results.append({
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "filename": c.filename,
                "page": c.page,
                "excerpt": c.text,
                "bm25_score": item["bm25_score"],
                "dense_score": item["dense_score"],
                "rrf_score": item["rrf_score"]
            })

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return results, round(latency_ms, 2)


# Global singleton
hybrid_retriever = HybridRetriever()
