from models import JudgeResult


class VerdictAgent:
    """Calculate overall score and verdict using weighted judge outputs."""

    WEIGHTS = {
        "relevance": 0.25,
        "accuracy": 0.35,
        "hallucination": 0.20,
        "completeness": 0.20,
    }

    VERDICT_THRESHOLDS = {
        "pass": 8.0,
        "needs_improvement": 5.0,
    }

    VERDICT_LABELS = {
        "Pass": "The response meets quality standards across all dimensions.",
        "Needs Improvement": "The response is usable but has notable weaknesses in one or more dimensions.",
        "Fail": "The response has critical quality issues and should not be used without revision.",
    }

    def calculate(self, relevance: JudgeResult, accuracy: JudgeResult, hallucination: JudgeResult, completeness: JudgeResult) -> dict:
        """Return overall score, verdict, and summary."""
        inverted_hallucination = 10.0 - hallucination.score
        overall_score = round(
            (
                relevance.score * self.WEIGHTS["relevance"]
                + accuracy.score * self.WEIGHTS["accuracy"]
                + inverted_hallucination * self.WEIGHTS["hallucination"]
                + completeness.score * self.WEIGHTS["completeness"]
            ),
            2,
        )
        verdict = self._determine_verdict(overall_score)
        summary = self._build_summary(relevance, accuracy, hallucination, completeness, overall_score, verdict)
        return {
            "overall_score": overall_score,
            "verdict": verdict,
            "summary": summary,
        }

    def _determine_verdict(self, overall_score: float) -> str:
        """Return Pass, Needs Improvement, or Fail based on thresholds."""
        if overall_score >= self.VERDICT_THRESHOLDS["pass"]:
            return "Pass"
        if overall_score >= self.VERDICT_THRESHOLDS["needs_improvement"]:
            return "Needs Improvement"
        return "Fail"

    def _build_summary(self, relevance, accuracy, hallucination, completeness, overall_score, verdict) -> str:
        """Create a consolidated human-readable summary combining all judge outputs."""
        weakest = min(
            [relevance, accuracy, completeness],
            key=lambda j: j.score,
        )
        strongest = max(
            [relevance, accuracy, completeness],
            key=lambda j: j.score,
        )

        parts = [
            f"Overall Score: {overall_score}/10 — {verdict}. {self.VERDICT_LABELS[verdict]}",
            f"Strongest dimension: {strongest.__class__.__name__ if hasattr(strongest, '__class__') else 'unknown'} ({strongest.score}/10). {strongest.reasoning}",
            f"Weakest dimension: {weakest.__class__.__name__ if hasattr(weakest, '__class__') else 'unknown'} ({weakest.score}/10). {weakest.reasoning}",
            f"Hallucination level: {hallucination.score}/10 (inverted score used in aggregation: {round(10.0 - hallucination.score, 2)}). {hallucination.reasoning}",
        ]

        if completeness.missing_points and any(p not in ("None detected", "No context available") for p in completeness.missing_points):
            parts.append(f"Missing points: {'; '.join(p for p in completeness.missing_points if p not in ('None detected', 'No context available'))}")

        if hallucination.unsupported_claims:
            parts.append(f"Unsupported claims: {'; '.join(hallucination.unsupported_claims)}")

        return " | ".join(parts)
