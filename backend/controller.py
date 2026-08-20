from fastapi import APIRouter, HTTPException, Query
from models import (
    BatchEvaluationRequest,
    BatchEvaluationResponse,
    EvaluationRequest,
    EvaluationResponse,
)
from services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api")
service = EvaluationService()


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_response(request: EvaluationRequest):
    """Evaluate an AI response using the RAG-enhanced judge agents."""
    try:
        result = service.evaluate(
            request,
            model=request.model,
            dataset=request.dataset,
        )
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/evaluate/batch", response_model=BatchEvaluationResponse)
def evaluate_batch(request: BatchEvaluationRequest):
    """Evaluate a batch of AI responses using the RAG-enhanced judge agents."""
    try:
        result = service.evaluate_batch(
            request.items,
            model=request.model,
            dataset=request.dataset,
        )
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/evaluations")
def list_evaluations(
    mode: str = Query(None),
    model: str = Query(None),
    dataset: str = Query(None),
    verdict: str = Query(None),
    limit: int = Query(1000),
):
    """List stored evaluation records with optional filters."""
    records = service.list_records(mode=mode, model=model, dataset=dataset, verdict=verdict, limit=limit)
    return {
        "total": len(records),
        "records": [
            {
                "id": r.id,
                "question": r.question,
                "overall_score": r.overall_score,
                "verdict": r.verdict,
                "timestamp": r.timestamp,
                "model": r.model,
                "dataset": r.dataset,
                "mode": r.mode,
                "relevance_score": r.relevance.score,
                "accuracy_score": r.accuracy.score,
                "hallucination_score": r.hallucination.score,
                "completeness_score": r.completeness.score,
                "summary": r.summary,
                "retrieved_context": r.retrieved_context,
            }
            for r in records
        ],
    }


@router.get("/evaluations/stats")
def evaluation_stats(
    mode: str = Query(None),
    model: str = Query(None),
    dataset: str = Query(None),
    verdict: str = Query(None),
):
    """Return aggregated statistics for stored evaluations."""
    records = service.list_records(mode=mode, model=model, dataset=dataset, verdict=verdict)
    return service.get_stats(records)


@router.get("/evaluations/trends")
def evaluation_trends(
    mode: str = Query(None),
    model: str = Query(None),
    dataset: str = Query(None),
):
    """Return daily trends for stored evaluations."""
    records = service.list_records(mode=mode, model=model, dataset=dataset)
    return {"trends": service.get_trends(records)}
