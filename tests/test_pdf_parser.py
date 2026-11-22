import os
from backend.app.sample_data.generate_sample_pdf import generate_sample_pdf
from backend.app.services.pdf_parser import parse_and_chunk_pdf


def test_pdf_parsing_and_page_retention(tmp_path):
    pdf_path = str(tmp_path / "test_doc.pdf")
    generate_sample_pdf(pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    page_count, chunks = parse_and_chunk_pdf(
        pdf_bytes=pdf_bytes,
        doc_id="test_doc_1",
        filename="test_doc.pdf",
        chunk_size=400,
        chunk_overlap=80
    )

    assert page_count == 4
    assert len(chunks) >= 4

    # Verify every chunk has proper page_number (1 to 4)
    pages_seen = set()
    for c in chunks:
        assert c.doc_id == "test_doc_1"
        assert c.filename == "test_doc.pdf"
        assert 1 <= c.page <= 4
        assert len(c.text) > 0
        pages_seen.add(c.page)

    assert 1 in pages_seen
    assert 2 in pages_seen
    assert 3 in pages_seen
    assert 4 in pages_seen
