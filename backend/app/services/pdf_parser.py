import io
import re
from typing import List, Dict, Any
from pypdf import PdfReader


class Chunk:
    def __init__(self, chunk_id: str, doc_id: str, filename: str, page: int, text: str):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.filename = filename
        self.page = page
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "filename": self.filename,
            "page": self.page,
            "text": self.text,
        }


def parse_and_chunk_pdf(
    pdf_bytes: bytes,
    doc_id: str,
    filename: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> (int, List[Chunk]):
    """
    Parses PDF bytes, extracts text per page, and splits into sliding-window chunks
    while strictly retaining 1-indexed page numbers.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    page_count = len(reader.pages)
    chunks: List[Chunk] = []

    for page_idx, page in enumerate(reader.pages):
        page_number = page_idx + 1
        raw_text = page.extract_text() or ""
        # Normalize whitespace
        cleaned_text = re.sub(r'\s+', ' ', raw_text).strip()
        if not cleaned_text:
            continue

        if len(cleaned_text) <= chunk_size:
            chunk_id = f"chunk_{doc_id}_p{page_number}_c0"
            chunks.append(Chunk(chunk_id, doc_id, filename, page_number, cleaned_text))
            continue

        # Sliding window chunking
        start = 0
        chunk_sub_idx = 0
        while start < len(cleaned_text):
            end = start + chunk_size
            chunk_slice = cleaned_text[start:end]

            # Try to break at a sentence or word boundary if not at the very end
            if end < len(cleaned_text):
                last_space = chunk_slice.rfind(' ')
                if last_space > chunk_size // 2:
                    end = start + last_space
                    chunk_slice = cleaned_text[start:end]

            chunk_id = f"chunk_{doc_id}_p{page_number}_c{chunk_sub_idx}"
            chunks.append(Chunk(chunk_id, doc_id, filename, page_number, chunk_slice.strip()))
            chunk_sub_idx += 1

            start += (chunk_size - chunk_overlap)
            if start >= len(cleaned_text):
                break

    return page_count, chunks
