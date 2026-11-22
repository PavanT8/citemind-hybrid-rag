import time
import logging
from typing import List, Dict, Any, Tuple
import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)


STRICT_SYSTEM_INSTRUCTION = (
    "You are CiteMind, an academic research assistant. Answer the user's question using ONLY the "
    "provided retrieved context chunks below.\n"
    "CRITICAL RULES:\n"
    "1. You MUST cite your sources inline using `[Page X]` notation at the end of each sentence making a claim "
    "(where X is the actual page number from the context chunk header).\n"
    "2. If the question cannot be answered from the provided chunks, state clearly: 'The provided documents "
    "do not contain sufficient information to answer this question.'\n"
    "3. Never fabricate facts, formulas, numbers, or page citations."
)


class LLMClient:
    def generate_grounded_answer(
        self,
        question: str,
        citations: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """
        Generates a grounded answer with [Page X] citations from retrieved chunks.
        Returns: (answer_text, generation_latency_ms)
        """
        start_time = time.perf_counter()

        if not citations:
            return (
                "No relevant document sections were found. Please upload or index a research paper to query.",
                0.0
            )

        # Build context prompt
        context_blocks = []
        for c in citations:
            header = f"--- [Document: {c['filename']}, Page {c['page']}] ---"
            context_blocks.append(f"{header}\n{c['excerpt']}\n")
        context_str = "\n".join(context_blocks)

        user_prompt = (
            f"Retrieved Context:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            "Provide a comprehensive, factual answer citing source pages using `[Page X]` notation:"
        )

        # 1. Google Gemini via official google-genai SDK
        if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                full_prompt = f"{STRICT_SYSTEM_INSTRUCTION}\n\n{user_prompt}"
                response = client.models.generate_content(
                    model=settings.GEMINI_CHAT_MODEL,
                    contents=full_prompt
                )
                answer = response.text.strip()
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                return answer, round(latency_ms, 2)
            except Exception as e:
                logger.error(f"Gemini generation error: {e}. Falling back to deterministic extractor.")

        # 2. Local LM Studio via OpenAI-compatible endpoint
        elif settings.LLM_PROVIDER == "lmstudio":
            try:
                resp = httpx.post(
                    f"{settings.LMSTUDIO_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {settings.LMSTUDIO_API_KEY}"},
                    json={
                        "model": settings.LMSTUDIO_CHAT_MODEL,
                        "messages": [
                            {"role": "system", "content": STRICT_SYSTEM_INSTRUCTION},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.2
                    },
                    timeout=30.0
                )
                if resp.status_code == 200:
                    answer = resp.json()["choices"][0]["message"]["content"].strip()
                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    return answer, round(latency_ms, 2)
            except Exception as e:
                logger.error(f"LM Studio generation error: {e}. Falling back to deterministic extractor.")

        # 3. Deterministic Grounded Fallback (for offline test / zero API quota)
        answer = self._deterministic_grounded_fallback(question, citations)
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return answer, round(latency_ms, 2)

    def _deterministic_grounded_fallback(self, question: str, citations: List[Dict[str, Any]]) -> str:
        """Synthesizes a grounded answer from the top retrieved chunks with genuine [Page X] tags."""
        top_c = citations[0]
        page = top_c["page"]
        excerpt = top_c["excerpt"]

        sentences = [s.strip() for s in excerpt.split(". ") if len(s.strip()) > 15]
        selected_sentences = sentences[:2] if sentences else [excerpt[:150]]
        
        grounded_statements = [f"{s} [Page {page}]." for s in selected_sentences if not s.endswith(".")]
        if not grounded_statements:
            grounded_statements = [f"{s} [Page {page}]" for s in selected_sentences]

        answer = " ".join(grounded_statements)
        if len(citations) > 1:
            second_c = citations[1]
            answer += f" Additionally, related scientific principles and benchmarks are detailed in the document [Page {second_c['page']}]."
        return answer


# Global singleton
llm_client = LLMClient()
