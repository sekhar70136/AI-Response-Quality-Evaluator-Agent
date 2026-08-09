import re
from difflib import SequenceMatcher
from typing import List

from backend.models import JudgeResult


class AccuracyJudge:
    """Judge whether the response is factually correct compared to retrieved reference answers."""

    def evaluate(self, question: str, response: str, context: List[str]) -> JudgeResult:
        """Return an accuracy score and reasoning using retrieved context."""
        if not response.strip():
            return JudgeResult(score=0.0, reasoning="The response is empty.")

        if not context or context[0].startswith("No relevant"):
            return JudgeResult(score=2.0, reasoning="No retrieved context is available to judge accuracy.")

        reference_answers: List[str] = []
        for chunk in context:
            match = re.search(r"A:\s*(.+?)(?:\s*\| similarity:|$)", chunk)
            if match:
                reference_answers.append(match.group(1).strip())

        if not reference_answers:
            return JudgeResult(score=3.0, reasoning="Retrieved context does not contain a reference answer for comparison.")

        response_lower = response.lower()
        best_score = 0.0
        best_answer = reference_answers[0]

        for ref in reference_answers:
            ref_lower = ref.lower()
            if ref_lower == response_lower:
                best_score = 10.0
                best_answer = ref
                break
            if ref_lower in response_lower or response_lower in ref_lower:
                best_score = max(best_score, 8.0)
                best_answer = ref
                continue
            token_overlap = len(set(re.findall(r"\w+", ref_lower)) & set(re.findall(r"\w+", response_lower)))
            total_tokens = max(len(set(re.findall(r"\w+", ref_lower))), 1)
            similarity = SequenceMatcher(None, ref_lower, response_lower).ratio()
            score = (token_overlap / total_tokens) * 6 + similarity * 4
            if score > best_score:
                best_score = score
                best_answer = ref

        best_score = round(max(0.0, min(10.0, best_score)), 2)

        if best_score >= 8.0:
            reasoning = f"Response matches the retrieved reference answer: '{best_answer}'."
        elif best_score >= 5.0:
            reasoning = f"Response is partially consistent with the retrieved reference answer: '{best_answer}'."
        else:
            reasoning = f"Response does not match the retrieved reference answer: '{best_answer}'."

        return JudgeResult(score=best_score, reasoning=reasoning)
