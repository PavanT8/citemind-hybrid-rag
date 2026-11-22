import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_sample_pdf(output_path: str = "backend/app/sample_data/sample_paper.pdf") -> str:
    """Generates a realistic 4-page scientific research paper for 1-click hybrid RAG demo."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=12
    )
    author_style = ParagraphStyle(
        'DocAuthors',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=18
    )
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )
    abstract_style = ParagraphStyle(
        'DocAbstract',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=24,
        rightIndent=24,
        spaceAfter=14
    )

    story = []

    # ================= PAGE 1 =================
    story.append(Paragraph("Hybrid Retrieval-Augmented Generation with Reciprocal Rank Fusion for Scientific Literature Synthesis", title_style))
    story.append(Paragraph("Dr. Elena Vance, Dr. Marcus Reynolds, Dr. Sophia Chen<br/>Center for Artificial Intelligence & Scientific Computing", author_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Abstract</b>", ParagraphStyle('AbsH', parent=body_style, fontName='Helvetica-Bold', alignment=1)))
    story.append(Paragraph(
        "Scientific literature synthesis requires retrieval-augmented generation systems that possess both high lexical precision for exact technical terminology and dense semantic understanding for abstract research concepts. In this paper, we evaluate a multi-stage Hybrid RAG architecture combining sparse BM25 indexing with dense neural embeddings fused through Reciprocal Rank Fusion (RRF). Our empirical findings demonstrate that Hybrid RRF achieves a 94.2% retrieval recall@4 and reduces citation hallucination by 38% compared to single-retriever baselines. We provide open-source implementations designed for resource-constrained production deployment under 512MB RAM.",
        abstract_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Introduction", h1_style))
    story.append(Paragraph(
        "Large language models (LLMs) have demonstrated impressive capabilities across natural language synthesis, yet they remain vulnerable to factual hallucinations when querying niche scientific literature. Standard dense vector retrieval often fails to capture precise technical identifiers, gene sequences, mathematical symbols, or algorithm names due to tokenization artifacts and semantic embedding compression.",
        body_style
    ))
    story.append(Paragraph(
        "Conversely, sparse lexical retrieval such as BM25 excels at exact keyword matching but struggles with semantic paraphrasing, vocabulary mismatch, and multi-disciplinary synthesis. To resolve this duality, hybrid retrieval structures combine lexical inverted indexes with dense vector embeddings.",
        body_style
    ))
    story.append(Paragraph(
        "In this study, we propose CiteMind, an academic research architecture that guarantees inline page-level citations [Page 1]. The system incorporates sliding-window chunking that preserves strict boundary page metadata, enabling users to verify assertions directly against source literature without manual cross-referencing.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Paragraph("2. Methodology & Mathematical Formulation", h1_style))
    story.append(Paragraph(
        "The CiteMind ingestion pipeline parses research PDFs into sliding windows of 500 characters with a 100-character overlap. Crucially, each chunk retains its 1-indexed document page number, filename, and unique chunk identifier. These chunks are indexed concurrently into an inverted BM25 index and a dense vector repository.",
        body_style
    ))
    story.append(Paragraph("2.1 Sparse Lexical Retrieval (BM25)", ParagraphStyle('DocH2', parent=h1_style, fontSize=11, spaceBefore=8)))
    story.append(Paragraph(
        "For query Q composed of terms q_i, the BM25 score for chunk D is defined as:<br/>"
        "BM25(D, Q) = sum_{i=1}^n IDF(q_i) * (f(q_i, D) * (k1 + 1)) / (f(q_i, D) + k1 * (1 - b + b * (|D| / avgdl)))<br/>"
        "where k1 is calibrated to 1.5 and b is calibrated to 0.75. This rewards exact keyword frequency while penalizing length discrepancies.",
        body_style
    ))
    story.append(Paragraph("2.2 Dense Vector Embeddings", ParagraphStyle('DocH2', parent=h1_style, fontSize=11, spaceBefore=8)))
    story.append(Paragraph(
        "Dense vectors are generated via API-based embedding models (such as gemini-embedding-001 or nomic-embed-text). For query vector v_q and chunk vector v_d, semantic relevance is calculated using cosine similarity:<br/>"
        "Sim(v_q, v_d) = (v_q . v_d) / (||v_q|| * ||v_d||)<br/>"
        "This identifies conceptually aligned passages even when vocabulary disjointness occurs.",
        body_style
    ))
    story.append(Paragraph("2.3 Reciprocal Rank Fusion (RRF)", ParagraphStyle('DocH2', parent=h1_style, fontSize=11, spaceBefore=8)))
    story.append(Paragraph(
        "To combine sparse BM25 scores and dense semantic vectors without requiring fragile score normalization or tuning arbitrary weighting hyperparameters, we employ Reciprocal Rank Fusion. For each chunk d in the candidate pool:<br/>"
        "<b>RRF(d) = sum_{m in M} 1 / (k + r_m(d))</b><br/>"
        "where M = {bm25, dense}, r_m(d) represents the 1-indexed rank position of chunk d in retriever m, and k is a smoothing constant set to 60 [Page 2]. If a chunk is not retrieved by retriever m, its rank r_m(d) is treated as infinity (contributing 0 to the sum).",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 3 =================
    story.append(Paragraph("3. Experimental Evaluation & Benchmarks", h1_style))
    story.append(Paragraph(
        "We evaluated CiteMind against a curated corpus of 200 peer-reviewed scientific papers spanning biomedical science, diffusion restoration models, and quantum optics. We compared three retrieval modes: pure BM25, pure Dense Vector, and Hybrid RRF. Queries were evaluated across three primary metrics: Faithfulness (LLM verification), Citation Coverage (declarative claims supported by [Page X] tags), and Retrieval Latency (ms).",
        body_style
    ))

    # Benchmark Table
    data = [
        ["Retrieval Mode", "Recall@4", "Faithfulness", "Citation Coverage", "Avg Latency"],
        ["BM25 Keyword", "76.4%", "0.760", "78.2%", "14.2 ms"],
        ["Dense Vector", "82.1%", "0.814", "84.5%", "185.0 ms"],
        ["Hybrid (RRF k=60)", "94.2%", "0.938", "96.4%", "196.4 ms"]
    ]
    t = Table(data, colWidths=[120, 75, 85, 110, 85])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#f1f5f9")),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3.1 Analysis of Experimental Results", ParagraphStyle('DocH2', parent=h1_style, fontSize=11, spaceBefore=8)))
    story.append(Paragraph(
        "The empirical data in Table 1 illustrates that Hybrid RRF outperforms both single-retriever approaches across all quality indicators [Page 3]. Pure BM25 exhibits the lowest latency (14.2 ms) but suffers in semantic questions where users do not know specific terminology. Conversely, pure Dense search occasionally misses exact numerical equations or author names. Hybrid RRF achieves the highest Recall@4 (94.2%) and Faithfulness (0.938) while keeping total retrieval time under 200 ms.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 4 =================
    story.append(Paragraph("4. Discussion & Implementation Efficiency", h1_style))
    story.append(Paragraph(
        "A critical design requirement of modern academic tools is cloud accessibility on free tiers. Many state-of-the-art neural retrieval architectures demand multi-gigabyte GPU instances or exceed 2GB of host RAM due to local PyTorch and transformer checkpoints. CiteMind deliberately eliminates local torch dependencies, relying on vectorized NumPy operations for cosine similarity and remote embedding APIs [Page 4].",
        body_style
    ))
    story.append(Paragraph(
        "Our runtime profiler confirms that the entire backend consumes less than 180MB of active RAM under steady-state query loads, comfortably operating within Render's 512MB free tier allocation without memory thrashing or process termination.",
        body_style
    ))
    story.append(Paragraph("5. Conclusion", h1_style))
    story.append(Paragraph(
        "CiteMind demonstrates that rigorous, page-grounded scientific synthesis can be achieved with lightweight, hybrid retrieval architectures. By merging BM25 and dense neural rankings through Reciprocal Rank Fusion, the framework delivers superior retrieval fidelity, verifiable citations, and real-time evaluation metrics on zero-cost infrastructure [Page 4].",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("References", h1_style))
    story.append(Paragraph("[1] Robertson, S., & Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Information Retrieval, 3(4), 333-389.", body_style))
    story.append(Paragraph("[2] Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods. SIGIR '09, 758-759.", body_style))
    story.append(Paragraph("[3] Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.", body_style))

    doc.build(story)
    return output_path


if __name__ == "__main__":
    generate_sample_pdf()
