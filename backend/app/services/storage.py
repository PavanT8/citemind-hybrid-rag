import os
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timezone
try:
    from app.schemas import DocumentInfo, EvalHistoryItem, EvalSummary
    from app.services.pdf_parser import Chunk
except ImportError:
    from backend.app.schemas import DocumentInfo, EvalHistoryItem, EvalSummary
    from backend.app.services.pdf_parser import Chunk


class StorageService:
    def __init__(self, data_dir: str = "backend/data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "citemind.db")
        
        # In-memory document & chunk registry
        self.documents: Dict[str, DocumentInfo] = {}
        self.chunks: Dict[str, Chunk] = {}
        
        self._init_sqlite()

    def _init_sqlite(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eval_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    question TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    faithfulness REAL NOT NULL,
                    citation_coverage REAL NOT NULL,
                    retrieval_ms REAL NOT NULL,
                    generation_ms REAL NOT NULL,
                    total_ms REAL NOT NULL
                )
            """)
            conn.commit()

    # Document management
    def add_document(self, doc_info: DocumentInfo, doc_chunks: List[Chunk]):
        self.documents[doc_info.id] = doc_info
        for chunk in doc_chunks:
            self.chunks[chunk.chunk_id] = chunk

    def get_document(self, doc_id: str) -> Optional[DocumentInfo]:
        return self.documents.get(doc_id)

    def list_documents(self) -> List[DocumentInfo]:
        return list(self.documents.values())

    def delete_document(self, doc_id: str) -> bool:
        if doc_id not in self.documents:
            return False
        del self.documents[doc_id]
        # Remove chunks
        chunk_keys_to_del = [cid for cid, c in self.chunks.items() if c.doc_id == doc_id]
        for cid in chunk_keys_to_del:
            del self.chunks[cid]
        return True

    def get_all_chunks(self, doc_ids: Optional[List[str]] = None) -> List[Chunk]:
        if not doc_ids:
            return list(self.chunks.values())
        doc_set = set(doc_ids)
        return [c for c in self.chunks.values() if c.doc_id in doc_set]

    # Evaluation persistence
    def log_evaluation(
        self,
        question: str,
        mode: str,
        faithfulness: float,
        citation_coverage: float,
        retrieval_ms: float,
        generation_ms: float,
        total_ms: float
    ) -> int:
        timestamp = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO eval_logs (
                    timestamp, question, mode, faithfulness, citation_coverage,
                    retrieval_ms, generation_ms, total_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, question, mode, faithfulness, citation_coverage, retrieval_ms, generation_ms, total_ms))
            conn.commit()
            return cursor.lastrowid

    def get_eval_history(self, limit: int = 50) -> List[EvalHistoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, question, mode, faithfulness, citation_coverage,
                       retrieval_ms, generation_ms, total_ms
                FROM eval_logs
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

        items = []
        for r in rows:
            items.append(EvalHistoryItem(
                id=r[0],
                timestamp=r[1],
                question=r[2],
                mode=r[3],
                faithfulness=round(r[4], 3),
                citation_coverage=round(r[5], 3),
                retrieval_ms=round(r[6], 1),
                generation_ms=round(r[7], 1),
                total_ms=round(r[8], 1)
            ))
        return items

    def get_summary_by_mode(self) -> Dict[str, EvalSummary]:
        summaries = {
            "hybrid": EvalSummary(),
            "dense": EvalSummary(),
            "bm25": EvalSummary()
        }
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mode, COUNT(*), AVG(faithfulness), AVG(citation_coverage), AVG(total_ms)
                FROM eval_logs
                GROUP BY mode
            """)
            rows = cursor.fetchall()

        for r in rows:
            mode = r[0]
            if mode in summaries:
                summaries[mode] = EvalSummary(
                    count=r[1],
                    avg_faithfulness=round(r[2] or 0.0, 3),
                    avg_citation_coverage=round(r[3] or 0.0, 3),
                    avg_total_ms=round(r[4] or 0.0, 1)
                )
        return summaries


# Global singleton
storage_service = StorageService()
