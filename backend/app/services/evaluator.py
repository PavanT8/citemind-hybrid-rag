import re
from typing import List, Dict, Any


class Evaluator:
    @staticmethod
    def calculate_citation_coverage(answer: str) -> float:
        """
        Calculates the proportion of declarative sentences in the answer that
        contain inline [Page X] citation tags.
        """
        if not answer or not answer.strip():
            return 0.0

        # Split into sentences based on punctuation (. ! ?)
        raw_sentences = re.split(r'(?<=[.!?])\s+', answer.strip())
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]

        if not sentences:
            return 1.0 if re.search(r'\[Page\s+\d+\]', answer) else 0.0

        cited_count = sum(1 for s in sentences if re.search(r'\[Page\s+\d+\]', s))
        coverage = cited_count / len(sentences)
        return round(min(1.0, coverage), 3)

    @staticmethod
    def calculate_faithfulness(
        question: str,
        answer: str,
        citations: List[Dict[str, Any]]
    ) -> float:
        """
        Computes the factual grounding / faithfulness score of the generated answer
        against the retrieved context chunks using lexical containment and n-gram overlap.
        """
        if not answer or not citations:
            return 0.0

        # If answer explicitly states lack of information, high faithfulness to reality
        if "not contain sufficient information" in answer.lower():
            return 1.0

        # Aggregate context tokens
        context_text = " ".join([c["excerpt"] for c in citations]).lower()
        context_tokens = set(re.findall(r'\b\w{3,}\b', context_text))

        if not context_tokens:
            return 0.5

        # Answer words (excluding citation tags like [Page 2])
        cleaned_answer = re.sub(r'\[Page\s+\d+\]', '', answer).lower()
        answer_tokens = [w for w in re.findall(r'\b\w{3,}\b', cleaned_answer)]

        if not answer_tokens:
            return 0.5

        # Overlap ratio: proportion of significant answer words grounded in context
        grounded_tokens = [w for w in answer_tokens if w in context_tokens]
        overlap_ratio = len(grounded_tokens) / len(answer_tokens)

        # Baseline bonus for properly formatted citations
        citation_bonus = 0.15 if re.search(r'\[Page\s+\d+\]', answer) else 0.0

        faithfulness = (overlap_ratio * 0.85) + citation_bonus
        return round(min(1.0, max(0.5, faithfulness)), 3)


# Global singleton
evaluator = Evaluator()
