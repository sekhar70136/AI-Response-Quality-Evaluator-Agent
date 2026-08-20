import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from backend.models import BatchEvaluationItem, BatchEvaluationResponse, JudgeResult
from backend.services.evaluation_service import EvaluationService


class FakeResult:
    def __init__(self, hallucination_score=None, overall_score=None):
        self.hallucination = type("H", (), {"score": hallucination_score})()
        self.overall_score = overall_score


class TestBatchEvaluation:
    """Tests for batch evaluation functionality."""

    def test_batch_csv_loading(self):
        """Simulate loading batch items from CSV-like data."""
        csv_rows = [
            {"question": "What is the capital of France?", "aiResponse": "Paris.", "referenceAnswer": "Paris"},
            {"question": "What is 2+2?", "aiResponse": "4.", "referenceAnswer": "4"},
        ]
        items = [
            BatchEvaluationItem(
                question=row["question"],
                response=row["aiResponse"],
                reference_answer=row.get("referenceAnswer") or None,
            )
            for row in csv_rows
        ]
        assert len(items) == 2
        assert items[0].question == "What is the capital of France?"
        assert items[1].response == "4."

    def test_batch_evaluation_returns_results(self):
        """EvaluationService.evaluate_batch should return correct structure."""
        service = EvaluationService()
        items = [
            BatchEvaluationItem(question="What is the capital of France?", response="Paris is the capital of France."),
            BatchEvaluationItem(question="What is 2+2?", response="4"),
        ]
        result = service.evaluate_batch(items)
        assert isinstance(result, BatchEvaluationResponse)
        assert "results" in result.model_dump()
        assert "total" in result.model_dump()
        assert "passed" in result.model_dump()
        assert "needs_improvement" in result.model_dump()
        assert "failed" in result.model_dump()
        assert "average_overall_score" in result.model_dump()
        assert len(result.results) == 2
        for item_result in result.results:
            assert "overall_score" in item_result.model_dump()
            assert "verdict" in item_result.model_dump()
            assert "relevance" in item_result.model_dump()
            assert "accuracy" in item_result.model_dump()
            assert "hallucination" in item_result.model_dump()
            assert "completeness" in item_result.model_dump()

    def test_hallucination_frequency_calculation(self):
        """Hallucination frequency should count responses with hallucination score > 0."""
        fake_results = [
            FakeResult(hallucination_score=0.0),
            FakeResult(hallucination_score=3.0),
            FakeResult(hallucination_score=8.0),
            FakeResult(hallucination_score=5.5),
        ]
        with_hallucination = sum(1 for r in fake_results if r.hallucination.score > 0)
        without_hallucination = sum(1 for r in fake_results if r.hallucination.score == 0)
        assert with_hallucination == 3
        assert without_hallucination == 1
        assert with_hallucination + without_hallucination == len(fake_results)

    def test_quality_trend_data_generation(self):
        """Quality trend data should extract overall_score per response."""
        fake_results = [
            FakeResult(overall_score=8.2),
            FakeResult(overall_score=6.5),
            FakeResult(overall_score=9.1),
        ]
        scores = [r.overall_score for r in fake_results]
        assert scores == [8.2, 6.5, 9.1]
        assert len(scores) == len(fake_results)
        assert all(0.0 <= s <= 10.0 for s in scores)

    def test_empty_batch_handling(self):
        """Empty batch items list should return a response with total=0."""
        service = EvaluationService()
        result = service.evaluate_batch([])
        assert isinstance(result, BatchEvaluationResponse)
        assert result.total == 0
        assert len(result.results) == 0

    def test_batch_evaluation_service_directly(self):
        """EvaluationService.evaluate_batch should return correct structure."""
        service = EvaluationService()
        items = [
            BatchEvaluationItem(question="What is the capital of France?", response="Paris."),
            BatchEvaluationItem(question="What is 2+2?", response="4"),
        ]
        result = service.evaluate_batch(items)
        assert isinstance(result, BatchEvaluationResponse)
        assert result.total == 2
        assert len(result.results) == 2
        assert result.passed + result.needs_improvement + result.failed == result.total
