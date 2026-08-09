from typing import List

from backend.models import (
    BatchEvaluationItem,
    BatchEvaluationResult,
    BatchEvaluationResponse,
    EvaluationRequest,
    EvaluationResponse,
    JudgeResult,
)
from backend.rag.retriever import Retriever
from backend.agents.relevance_judge import RelevanceJudge
from backend.agents.accuracy_judge import AccuracyJudge
from backend.agents.hallucination_judge import HallucinationJudge
from backend.agents.completeness_judge import CompletenessJudge
from backend.agents.verdict_agent import VerdictAgent


class EvaluationService:
    """Coordinate the full evaluation workflow."""

    def __init__(self) -> None:
        self.retriever = Retriever()
        self.relevance_judge = RelevanceJudge()
        self.accuracy_judge = AccuracyJudge()
        self.hallucination_judge = HallucinationJudge()
        self.completeness_judge = CompletenessJudge()
        self.verdict_agent = VerdictAgent()

    def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """Run retrieval and all judge agents, then combine their outputs."""
        if request.reference_answer and request.reference_answer.strip():
            retrieved_context = [request.reference_answer.strip()]
        else:
            retrieved_context = self.retriever.retrieve(request.question)

        relevance = self.relevance_judge.evaluate(
            question=request.question,
            response=request.response,
            context=retrieved_context,
        )
        accuracy = self.accuracy_judge.evaluate(
            question=request.question,
            response=request.response,
            context=retrieved_context,
        )
        hallucination = self.hallucination_judge.evaluate(
            question=request.question,
            response=request.response,
            context=retrieved_context,
        )
        completeness = self.completeness_judge.evaluate(
            question=request.question,
            response=request.response,
            context=retrieved_context,
        )

        verdict_result = self.verdict_agent.calculate(relevance, accuracy, hallucination, completeness)

        return EvaluationResponse(
            relevance=relevance,
            accuracy=accuracy,
            hallucination=hallucination,
            completeness=completeness,
            overall_score=verdict_result["overall_score"],
            verdict=verdict_result["verdict"],
            summary=verdict_result["summary"],
            retrieved_context=retrieved_context,
        )

    def evaluate_batch(self, items: List[BatchEvaluationItem]) -> BatchEvaluationResponse:
        """Run evaluation for a batch of question-response pairs."""
        results: List[BatchEvaluationResult] = []
        passed = 0
        needs_improvement = 0
        failed = 0
        total_score = 0.0

        for item in items:
            try:
                eval_request = EvaluationRequest(
                    question=item.question,
                    response=item.response,
                    reference_answer=item.reference_answer,
                )
                eval_response = self.evaluate(eval_request)
                results.append(
                    BatchEvaluationResult(
                        question=item.question,
                        overall_score=eval_response.overall_score,
                        verdict=eval_response.verdict,
                        summary=eval_response.summary,
                        relevance=eval_response.relevance,
                        accuracy=eval_response.accuracy,
                        hallucination=eval_response.hallucination,
                        completeness=eval_response.completeness,
                        retrieved_context=eval_response.retrieved_context,
                    )
                )
                total_score += eval_response.overall_score
                if eval_response.verdict == "Pass":
                    passed += 1
                elif eval_response.verdict == "Needs Improvement":
                    needs_improvement += 1
                else:
                    failed += 1
            except Exception as exc:
                results.append(
                    BatchEvaluationResult(
                        question=item.question,
                        overall_score=0.0,
                        verdict="Fail",
                        summary=str(exc),
                        relevance=JudgeResult(score=0.0, reasoning="Evaluation failed."),
                        accuracy=JudgeResult(score=0.0, reasoning="Evaluation failed."),
                        hallucination=JudgeResult(score=0.0, reasoning="Evaluation failed."),
                        completeness=JudgeResult(score=0.0, reasoning="Evaluation failed."),
                        retrieved_context=[],
                        error=str(exc),
                    )
                )
                failed += 1

        total = len(results)
        average_overall = round(total_score / total, 2) if total else 0.0

        return BatchEvaluationResponse(
            total=total,
            passed=passed,
            needs_improvement=needs_improvement,
            failed=failed,
            average_overall_score=average_overall,
            results=results,
        )
