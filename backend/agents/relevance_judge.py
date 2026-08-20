import re
from typing import List

from models import JudgeResult


class RelevanceJudge:
    """Judge whether the response answers the user's question based on retrieved context."""

    def evaluate(self, question: str, response: str, context: List[str]) -> JudgeResult:
        """Return a relevance score and reasoning using retrieved context."""
        if not response.strip():
            return JudgeResult(score=0.0, reasoning="The response is empty.")

        if not context or context[0].startswith("No relevant"):
            return JudgeResult(score=2.0, reasoning="No retrieved context is available to judge relevance.")

        question_keywords = [w.lower() for w in re.findall(r"\w+", question) if len(w) > 2]
        context_text = " ".join(context).lower()
        response_lower = response.lower()

        keyword_overlap = sum(1 for w in question_keywords if w in response_lower)
        context_match = sum(1 for w in question_keywords if w in context_text)

        if context_match == 0:
            return JudgeResult(score=1.0, reasoning="Retrieved context does not appear related to the question.")

        coverage = keyword_overlap / max(len(question_keywords), 1)
        context_support = sum(1 for w in question_keywords if w in response_lower and w in context_text) / max(context_match, 1)

        score = round((coverage * 4 + context_support * 6), 2)
        score = max(0.0, min(10.0, score))

        if score >= 8.0:
            reasoning = "The response directly addresses the question and is well supported by the retrieved context."
        elif score >= 5.0:
            reasoning = "The response partially addresses the question using the retrieved context."
        else:
            reasoning = "The response barely addresses the question or lacks support from the retrieved context."

        return JudgeResult(score=score, reasoning=reasoning)
