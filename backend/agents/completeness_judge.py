import re
from typing import List

from backend.models import JudgeResult


class CompletenessJudge:
    """Judge whether the response addresses every important part of the user's question using retrieved context."""

    def evaluate(self, question: str, response: str, context: List[str]) -> JudgeResult:
        """Return a completeness score, missing points, and reasoning using retrieved context."""
        if not response.strip():
            return JudgeResult(score=0.0, reasoning="The response is empty.", missing_points=["No response provided"])

        if not context or context[0].startswith("No relevant"):
            return JudgeResult(score=2.0, reasoning="No retrieved context is available to judge completeness.", missing_points=["No context available"])

        context_text = " ".join(context).lower()
        response_lower = response.lower()

        question_aspects = self._extract_question_aspects(question, context_text)
        if not question_aspects:
            question_aspects = [question.strip()]

        covered_aspects = []
        missing_aspects = []
        for aspect in question_aspects:
            aspect_tokens = set(re.findall(r"\w+", aspect.lower()))
            if not aspect_tokens:
                continue
            response_tokens = set(re.findall(r"\w+", response_lower))
            overlap = aspect_tokens & response_tokens
            coverage = len(overlap) / len(aspect_tokens) if aspect_tokens else 0
            if coverage >= 0.4:
                covered_aspects.append(aspect)
            else:
                missing_aspects.append(aspect)

        if not missing_aspects:
            score = 10.0
            reasoning = "The response addresses all key aspects of the question based on the retrieved context."
        elif len(missing_aspects) == len(question_aspects):
            score = 1.0
            reasoning = "The response fails to address any key aspects of the question."
        else:
            coverage_ratio = len(covered_aspects) / len(question_aspects)
            score = round(coverage_ratio * 10, 2)
            score = max(2.0, min(9.0, score))
            reasoning = (
                f"The response covers {len(covered_aspects)} of {len(question_aspects)} key aspects. "
                f"Missing: {'; '.join(missing_aspects)}."
            )

        score = max(0.0, min(10.0, score))

        missing_points = missing_aspects if missing_aspects else ["None detected"]

        return JudgeResult(score=score, reasoning=reasoning, missing_points=missing_points)

    def _extract_question_aspects(self, question: str, context: str) -> List[str]:
        """Break a question into distinct aspects based on conjunctions and context."""
        aspects: List[str] = []
        split_pattern = r'\b(?:and|or|also|additionally|furthermore|moreover|what about|how about)\b'
        parts = re.split(split_pattern, question, flags=re.IGNORECASE)
        for part in parts:
            part = part.strip().rstrip('?.,;:')
            if part and len(part) > 2:
                aspects.append(part)

        seen = set()
        unique_aspects = []
        for a in aspects:
            key = a.lower()
            if key not in seen:
                seen.add(key)
                unique_aspects.append(a)
        return unique_aspects
