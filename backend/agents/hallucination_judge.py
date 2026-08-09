import re
from typing import List

from backend.models import JudgeResult


class HallucinationJudge:
    """Detect unsupported claims or fabricated information using retrieved context."""

    def evaluate(self, question: str, response: str, context: List[str]) -> JudgeResult:
        """Return a hallucination score, unsupported claims, and reasoning using retrieved context."""
        if not response.strip():
            return JudgeResult(score=0.0, reasoning="The response is empty.", unsupported_claims=[])

        if not context or context[0].startswith("No relevant"):
            return JudgeResult(score=10.0, reasoning="No retrieved context is available. All claims are unsupported.", unsupported_claims=["No supporting context available."])

        context_text = " ".join(context).lower()
        context_tokens = set(re.findall(r"\w+", context_text))
        response_tokens = re.findall(r"\w+", response)
        sentence_boundaries = re.split(r'(?<=[.!?])\s+', response)
        sentences = [s.strip() for s in sentence_boundaries if s.strip()]

        unsupported_claims: List[str] = []
        for sentence in sentences:
            sentence_tokens = set(re.findall(r"\w+", sentence.lower()))
            if len(sentence_tokens) == 0:
                continue
            supported = sentence_tokens & context_tokens
            if len(supported) / len(sentence_tokens) < 0.5:
                unsupported_claims.append(sentence)

        if not sentences:
            unsupported_score = 10.0
        else:
            unsupported_ratio = len(unsupported_claims) / len(sentences)
            unsupported_score = round(unsupported_ratio * 10, 2)

        unsupported_score = max(0.0, min(10.0, unsupported_score))

        if unsupported_score == 0.0:
            reasoning = "All statements in the response are supported by the retrieved context."
        elif unsupported_score <= 4.0:
            reasoning = "Most statements are supported by the retrieved context, with minor unsupported claims."
        elif unsupported_score <= 7.0:
            reasoning = "Several statements lack support from the retrieved context."
        else:
            reasoning = "Most or all statements in the response are unsupported by the retrieved context."

        return JudgeResult(score=unsupported_score, reasoning=reasoning, unsupported_claims=unsupported_claims)
