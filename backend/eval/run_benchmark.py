import os
import sys
import json
import time

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import index_sample_paper
from backend.app.services.storage import storage_service
from backend.app.services.hybrid_retriever import hybrid_retriever
from backend.app.services.llm_client import llm_client
from backend.app.services.evaluator import evaluator

BENCHMARK_QUESTIONS = [
    "What is the mathematical formulation of Reciprocal Rank Fusion?",
    "Why do large language models hallucinate in niche scientific domains?",
    "What are the benchmark results comparing BM25, Dense Vector, and Hybrid RRF?",
    "What is the memory consumption of CiteMind on Render free tier?",
    "How does the sliding-window chunking preserve page numbers?"
]

MODES = ["bm25", "dense", "hybrid"]


def run_benchmark():
    print("=" * 70)
    print("CITEMIND HYBRID RAG — MULTI-MODE EVALUATION BENCHMARK")
    print("=" * 70)
    print("Initializing document corpus and pre-indexing sample paper...")
    index_sample_paper()
    chunks = storage_service.get_all_chunks(["doc_sample_paper"])
    print(f"Corpus loaded: {len(chunks)} chunks across 4 pages.\n")

    results_by_mode = {m: [] for m in MODES}

    for q_idx, question in enumerate(BENCHMARK_QUESTIONS, 1):
        print(f"Query {q_idx}/5: '{question}'")
        for mode in MODES:
            citations, ret_ms = hybrid_retriever.retrieve(
                query=question,
                chunks=chunks,
                mode=mode,
                top_k=4
            )
            answer, gen_ms = llm_client.generate_grounded_answer(question, citations)
            cov = evaluator.calculate_citation_coverage(answer)
            faith = evaluator.calculate_faithfulness(question, answer, citations)
            total_ms = ret_ms + gen_ms

            results_by_mode[mode].append({
                "question": question,
                "retrieval_ms": ret_ms,
                "generation_ms": gen_ms,
                "total_ms": total_ms,
                "citation_coverage": cov,
                "faithfulness": faith,
                "citations_count": len(citations)
            })

    # Summary table
    print("\n" + "=" * 70)
    print(f"{'Retrieval Mode':<18} | {'Faithfulness':<12} | {'Coverage':<10} | {'Ret. Latency':<12} | {'Total Latency'}")
    print("-" * 70)

    summary_metrics = {}
    for mode in MODES:
        runs = results_by_mode[mode]
        avg_faith = sum(r["faithfulness"] for r in runs) / len(runs)
        avg_cov = sum(r["citation_coverage"] for r in runs) / len(runs)
        avg_ret = sum(r["retrieval_ms"] for r in runs) / len(runs)
        avg_tot = sum(r["total_ms"] for r in runs) / len(runs)

        summary_metrics[mode] = {
            "avg_faithfulness": round(avg_faith, 3),
            "avg_citation_coverage": round(avg_cov, 3),
            "avg_retrieval_ms": round(avg_ret, 1),
            "avg_total_ms": round(avg_tot, 1)
        }

        print(f"{mode.upper():<18} | {avg_faith:<12.3f} | {avg_cov*100:<9.1f}% | {avg_ret:<10.1f} ms | {avg_tot:<10.1f} ms")
    print("=" * 70)

    # Save to .agent/logs/benchmark_results.json
    output_log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/logs"))
    os.makedirs(output_log_dir, exist_ok=True)
    output_log_file = os.path.join(output_log_dir, "benchmark_results.json")
    with open(output_log_file, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "summary": summary_metrics,
            "detailed": results_by_mode
        }, f, indent=2)

    print(f"\nReal benchmark results saved to: {output_log_file}\n")
    return summary_metrics


if __name__ == "__main__":
    run_benchmark()
