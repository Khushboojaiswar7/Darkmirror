"""
Evaluation API – benchmarks detection pipeline against labeled data.
"""
from typing import Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.evaluation_service import EvaluationService

router = APIRouter()
eval_service = EvaluationService()


class RunEvaluationRequest(BaseModel):
    dataset_id: Optional[str] = None


@router.post("/run")
async def run_evaluation(
    request: Optional[RunEvaluationRequest] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Run evaluation on the multi-agent detection pipeline.
    Calculates Accuracy, Precision, Recall, F1, Confusion Matrix, and ROC Curve.
    """
    dataset_id = request.dataset_id if request else None
    return await eval_service.run_evaluation(db, dataset_id)


@router.get("/latest")
async def get_latest_results(db: AsyncSession = Depends(get_db)):
    """Retrieve latest evaluation metrics."""
    return await eval_service.run_evaluation(db, None)
