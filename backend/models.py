from typing import List, Optional
from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    """Input payload received from the frontend for evaluation."""

    question: str = Field(..., min_length=1, description="The user's question")
    response: str = Field(..., min_length=1, description="The AI-generated response to evaluate")
    reference_answer: Optional[str] = Field(
        default=None,
        description="Optional reference answer that can help with evaluation",
    )


class BatchEvaluationItem(BaseModel):
    """Single item in a batch evaluation request."""

    question: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    reference_answer: Optional[str] = Field(default=None)


class BatchEvaluationRequest(BaseModel):
    """Batch evaluation request payload."""

    items: List[BatchEvaluationItem] = Field(..., min_length=1, max_length=100)


class BatchEvaluationResult(BaseModel):
    """Result for a single item in a batch evaluation."""

    question: str
    overall_score: float = Field(..., ge=0, le=10)
    verdict: str
    summary: str
    relevance: JudgeResult
    accuracy: JudgeResult
    hallucination: JudgeResult
    completeness: JudgeResult
    retrieved_context: List[str]
    error: Optional[str] = Field(default=None)


class BatchEvaluationResponse(BaseModel):
    """Response for a batch evaluation request."""

    total: int
    passed: int
    needs_improvement: int
    failed: int
    average_overall_score: float = Field(..., ge=0, le=10)
    results: List[BatchEvaluationResult]


class JudgeResult(BaseModel):
    """Output returned by one judge agent."""

    score: float = Field(..., ge=0, le=10, description="Score between 0 and 10")
    reasoning: str = Field(..., description="Short explanation for the score")
    missing_points: Optional[List[str]] = Field(default=None, description="List of missing points for completeness judge")
    unsupported_claims: Optional[List[str]] = Field(default=None, description="List of unsupported claims for hallucination judge")


class EvaluationResponse(BaseModel):
    """Final response returned by the backend API."""

    relevance: JudgeResult
    accuracy: JudgeResult
    hallucination: JudgeResult
    completeness: JudgeResult
    overall_score: float = Field(..., ge=0, le=10, description="Overall weighted score")
    verdict: str = Field(..., description="Pass, Needs Improvement, or Fail")
    summary: str = Field(..., description="Final evaluation summary")
    retrieved_context: List[str] = Field(..., description="Top relevant context chunks retrieved from the RAG source")
