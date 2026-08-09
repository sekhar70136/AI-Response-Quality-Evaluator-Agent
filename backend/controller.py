from fastapi import APIRouter, HTTPException
from backend.models import BatchEvaluationRequest, BatchEvaluationResponse, EvaluationRequest, EvaluationResponse
from backend.services.evaluation_service import EvaluationService

router = APIRouter()
service = EvaluationService()


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_response(request: EvaluationRequest):
    """Evaluate an AI response using the RAG-enhanced judge agents."""
    try:
        result = service.evaluate(request)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/evaluate/batch", response_model=BatchEvaluationResponse)
def evaluate_batch(request: BatchEvaluationRequest):
    """Evaluate a batch of AI responses using the RAG-enhanced judge agents."""
    try:
        result = service.evaluate_batch(request.items)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
