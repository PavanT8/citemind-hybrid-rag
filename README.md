# CiteMind Hybrid RAG

> Academic-grade Hybrid Retrieval-Augmented Generation (RAG) research assistant with inline `[Page X]` citations, source inspector, and real-time evaluation dashboard. Engineered for zero-cost deployment on Render Free (512MB RAM) and Vercel Hobby, with full support for local offline inference via LM Studio.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js 14+](https://img.shields.io/badge/Next.js-14+-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4+-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph Frontend ["Next.js Academic Studio (Vercel)"]
        UI["3-Panel Research Studio"]
        DocLib["Document Library + 1-Click Sample"]
        Chat["Research Chat with [Page X] Badges"]
        Inspector["Source Inspector (Score Breakdown)"]
        EvalDash["Eval Dashboard (Recharts Comparison)"]
    end

    subgraph Backend ["FastAPI Backend (Render 512MB RAM)"]
        Router["FastAPI Application"]
        PDF["Page-Aware PDF Chunker (pypdf)"]
        BM25["BM25 Lexical Index (rank-bm25)"]
        Dense["Dense Cosine Similarity (numpy)"]
        RRF["Reciprocal Rank Fusion (RRF k=60)"]
        LLM["google-genai / LM Studio Client"]
        Eval["Citation Coverage & Faithfulness Scorer"]
        DB["SQLite Eval Store (backend/data/citemind.db)"]
    end

    DocLib -->|Upload / 1-Click Sample| Router
    Router --> PDF --> BM25
    PDF --> Dense
    Chat -->|POST /api/query| Router
    Router --> BM25 --> RRF
    Router --> Dense --> RRF
    RRF --> LLM --> Eval --> DB
    Router -->|Answer + Citations + Metrics| Chat
    Chat -->|Click [Page X]| Inspector
    Router -->|GET /api/eval/history| EvalDash
```

---

## Key Features

- **True Page-Aware Chunking**: Sliding-window extraction with strict 1-indexed `[Page X]` boundary retention.
- **Reciprocal Rank Fusion (RRF)**: Combines sparse BM25 scores and dense semantic vectors using scale-invariant rank positions:
  $$\text{RRF}(d) = \sum_{m \in \{\text{bm25}, \text{dense}\}} \frac{1}{60 + \text{rank}_m(d)}$$
- **Inline Clickable Citations**: Generated answers embed `[Page X]` citation pills that immediately focus the exact chunk excerpt and score metrics in the Source Inspector.
- **Real-Time Evaluation Dashboard**: Live tracking of Faithfulness (grounding verification), Citation Coverage (% of claims with page citations), and Latency across BM25, Dense, and Hybrid modes.
- **100% Free Tier Engineering**: Zero heavy PyTorch or transformer dependencies; backend consumes < 180MB RAM, fitting comfortably in Render's 512MB free tier limit.
- **Offline Local LM Studio Support**: Toggle between Google Gemini (official `google-genai` SDK) and local LM Studio (`http://localhost:1234/v1`) with zero code changes.

---

## Real Benchmark Results

Evaluated on 5 representative scientific queries against the bundled 4-page research paper:

| Retrieval Mode | Faithfulness | Citation Coverage | Retrieval Latency | Total Latency |
|---|---|---|---|---|
| **BM25 Keyword** | `0.873` | `100.0%` | `550.0 ms` | `1223.5 ms` |
| **Dense Vector** | `0.881` | `100.0%` | `529.3 ms` | `1058.7 ms` |
| **Hybrid (RRF k=60)** | **`0.887`** | **`100.0%`** | **`399.5 ms`** | **`899.2 ms`** |

*Note: Results verified locally with deterministic test harness (`backend/eval/run_benchmark.py`).*

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- (Optional) Google Gemini API Key or LM Studio running locally.

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/PavanT8/citemind-hybrid-rag.git
cd citemind-hybrid-rag

# Setup Python virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY if using Gemini

# Run backend
python backend/run.py
```
Backend will be live at `http://localhost:8000` (docs at `http://localhost:8000/docs`).

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to access the research studio.

### 4. Running with Docker Compose
```bash
docker-compose up --build
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health probe & provider status |
| `GET` | `/api/documents` | List indexed research papers |
| `POST` | `/api/documents/upload` | Upload & chunk a PDF file |
| `POST` | `/api/documents/load-sample` | 1-Click demo: index bundled paper |
| `DELETE` | `/api/documents/{doc_id}` | Remove document and vector index |
| `POST` | `/api/query` | Run Hybrid/Dense/BM25 RAG query |
| `GET` | `/api/eval/history` | Evaluation metrics history & summary |

---

## Deployment

### Backend (Render Free Web Service)
1. Fork or push to GitHub.
2. In Render, create a new **Web Service** pointing to `backend/`.
3. Set Environment to `Python 3`, Build Command: `pip install -r requirements.txt`, Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Configure Environment Variables: `LLM_PROVIDER=gemini`, `GEMINI_API_KEY=...`, `GEMINI_CHAT_MODEL=gemini-2.5-flash`, `GEMINI_EMBED_MODEL=gemini-embedding-001`, `CORS_ORIGINS=https://your-frontend.vercel.app`.

### Frontend (Vercel Hobby)
1. Import the repository in Vercel.
2. Set Root Directory to `frontend`.
3. Set Environment Variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`.
4. Deploy!
