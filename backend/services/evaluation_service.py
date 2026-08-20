from typing import List
from datetime import datetime
from uuid import uuid4

from backend.models import (
    BatchEvaluationItem,
    BatchEvaluationResult,
    BatchEvaluationResponse,
    EvaluationRequest,
    EvaluationResponse,
    EvaluationRecord,
    JudgeResult,
)
from backend.rag.retriever import Retriever
from backend.agents.relevance_judge import RelevanceJudge
from backend.agents.accuracy_judge import AccuracyJudge
from backend.agents.hallucination_judge import HallucinationJudge
from backend.agents.completeness_judge import CompletenessJudge
from backend.agents.verdict_agent import VerdictAgent


class EvaluationService:
    """Coordinate the full evaluation workflow and persist results."""

    def __init__(self) -> None:
        self.retriever = Retriever()
        self.relevance_judge = RelevanceJudge()
        self.accuracy_judge = AccuracyJudge()
        self.hallucination_judge = HallucinationJudge()
        self.completeness_judge = CompletenessJudge()
        self.verdict_agent = VerdictAgent()
        self.records: List[EvaluationRecord] = []

    def _build_record(self, request: EvaluationRequest, response: EvaluationResponse, mode: str, model: str, dataset: str) -> EvaluationRecord:
        return EvaluationRecord(
            id=str(uuid4()),
            question=request.question,
            response=request.response,
            reference_answer=request.reference_answer,
            relevance=response.relevance,
            accuracy=response.accuracy,
            hallucination=response.hallucination,
            completeness=response.completeness,
            overall_score=response.overall_score,
            verdict=response.verdict,
            summary=response.summary,
            retrieved_context=response.retrieved_context,
            timestamp=datetime.utcnow().isoformat() + "Z",
            model=model,
            dataset=dataset,
            mode=mode,
        )

    def evaluate(self, request: EvaluationRequest, mode: str = "single", model: str = None, dataset: str = None) -> EvaluationResponse:
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

        response = EvaluationResponse(
            relevance=relevance,
            accuracy=accuracy,
            hallucination=hallucination,
            completeness=completeness,
            overall_score=verdict_result["overall_score"],
            verdict=verdict_result["verdict"],
            summary=verdict_result["summary"],
            retrieved_context=retrieved_context,
            timestamp=datetime.utcnow().isoformat() + "Z",
            model=model,
            dataset=dataset,
            mode=mode,
            question=request.question,
        )

        record = self._build_record(request, response, mode, model, dataset)
        self.records.append(record)

        return response

    def evaluate_batch(self, items: List[BatchEvaluationItem], mode: str = "batch", model: str = None, dataset: str = None) -> BatchEvaluationResponse:
        """Run evaluation for a batch of question-response pairs."""
        results: List[BatchEvaluationResult] = []
        passed = 0
        needs_improvement = 0
        failed = 0
        total_score = 0.0

        for item in items:
            try:
                item_model = item.model or model
                item_dataset = item.dataset or dataset
                eval_request = EvaluationRequest(
                    question=item.question,
                    response=item.response,
                    reference_answer=item.reference_answer,
                    model=item_model,
                    dataset=item_dataset,
                )
                eval_response = self.evaluate(eval_request, mode=mode, model=item_model, dataset=item_dataset)
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

    def list_records(self, mode: str = None, model: str = None, dataset: str = None, verdict: str = None, limit: int = 1000) -> List[EvaluationRecord]:
        records = self.records
        if mode:
            records = [r for r in records if r.mode == mode]
        if model:
            records = [r for r in records if r.model == model]
        if dataset:
            records = [r for r in records if r.dataset == dataset]
        if verdict:
            records = [r for r in records if r.verdict == verdict]
        return records[-limit:]

    def get_stats(self, records: List[EvaluationRecord]) -> dict:
        total = len(records)
        passed = sum(1 for r in records if r.verdict == "Pass")
        needs_improvement = sum(1 for r in records if r.verdict == "Needs Improvement")
        failed = sum(1 for r in records if r.verdict == "Fail")
        avg_relevance = round(sum(r.relevance.score for r in records) / total, 2) if total else 0.0
        avg_accuracy = round(sum(r.accuracy.score for r in records) / total, 2) if total else 0.0
        avg_completeness = round(sum(r.completeness.score for r in records) / total, 2) if total else 0.0
        avg_overall = round(sum(r.overall_score for r in records) / total, 2) if total else 0.0
        hallucinated = sum(1 for r in records if r.hallucination.score >= 7.0)
        hallucination_low = sum(1 for r in records if r.hallucination.score < 4.0)
        hallucination_medium = sum(1 for r in records if 4.0 <= r.hallucination.score < 7.0)
        hallucination_high = sum(1 for r in records if r.hallucination.score >= 7.0)
        return {
            "total": total,
            "passed": passed,
            "needs_improvement": needs_improvement,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 2) if total else 0.0,
            "average_overall_score": avg_overall,
            "average_relevance": avg_relevance,
            "average_accuracy": avg_accuracy,
            "average_completeness": avg_completeness,
            "hallucination_frequency": round(hallucinated / total * 100, 2) if total else 0.0,
            "hallucinated_count": hallucinated,
            "hallucination_low_count": hallucination_low,
            "hallucination_medium_count": hallucination_medium,
            "hallucination_high_count": hallucination_high,
            "hallucination_low_percentage": round(hallucination_low / total * 100, 2) if total else 0.0,
            "hallucination_medium_percentage": round(hallucination_medium / total * 100, 2) if total else 0.0,
            "hallucination_high_percentage": round(hallucination_high / total * 100, 2) if total else 0.0,
        }

    def get_trends(self, records: List[EvaluationRecord]) -> List[dict]:
        from collections import defaultdict
        daily = defaultdict(lambda: {"count": 0, "passed": 0, "failed": 0, "needs_improvement": 0, "avg_score": 0.0, "total_score": 0.0})
        for r in records:
            day = r.timestamp[:10]
            daily[day]["count"] += 1
            daily[day]["total_score"] += r.overall_score
            if r.verdict == "Pass":
                daily[day]["passed"] += 1
            elif r.verdict == "Needs Improvement":
                daily[day]["needs_improvement"] += 1
            else:
                daily[day]["failed"] += 1
        trends = []
        for day, data in sorted(daily.items()):
            trends.append({
                "date": day,
                "count": data["count"],
                "passed": data["passed"],
                "failed": data["failed"],
                "needs_improvement": data["needs_improvement"],
                "average_score": round(data["total_score"] / data["count"], 2) if data["count"] else 0.0,
            })
        return trends
