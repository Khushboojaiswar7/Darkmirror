"""
Audit API – batch processing endpoint.

POST /api/audits       – create and run a batch audit
GET  /api/audits       – list all audits
GET  /api/audits/{id}  – get audit details with predictions
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.prediction import Audit, Prediction
from app.services.audit_service import AuditService
from app.schemas.analysis import BatchAuditRequest

router = APIRouter()
audit_service = AuditService()


@router.post("")
async def create_audit(
    request: BatchAuditRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create and execute a batch audit.

    Accepts a list of conversations and processes them all through
    the multi-agent pipeline.
    """
    audit = await audit_service.create_audit(
        db=db,
        name=request.name,
        description=request.description,
        conversations_data=request.conversations,
    )
    return {
        "audit_id": str(audit.id),
        "name": audit.name,
        "status": audit.status,
        "total_conversations": audit.total_conversations,
        "completed_conversations": audit.completed_conversations,
        "flagged_count": audit.flagged_count,
        "summary": audit.summary,
    }


@router.get("")
async def list_audits(db: AsyncSession = Depends(get_db)):
    """List all batch audits."""
    audits = await audit_service.list_audits(db)
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "status": a.status,
            "total_conversations": a.total_conversations,
            "completed_conversations": a.completed_conversations,
            "flagged_count": a.flagged_count,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in audits
    ]


@router.get("/{audit_id}")
async def get_audit(
    audit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific audit with its predictions."""
    audit = await audit_service.get_audit(db, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Fetch predictions for this audit
    pred_result = await db.execute(
        select(Prediction).where(Prediction.audit_id == audit_id)
    )
    predictions = pred_result.scalars().all()

    return {
        "id": str(audit.id),
        "name": audit.name,
        "description": audit.description,
        "status": audit.status,
        "total_conversations": audit.total_conversations,
        "completed_conversations": audit.completed_conversations,
        "flagged_count": audit.flagged_count,
        "summary": audit.summary,
        "started_at": audit.started_at.isoformat() if audit.started_at else None,
        "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
        "predictions": [
            {
                "id": str(p.id),
                "conversation_id": str(p.conversation_id),
                "flag": p.flag,
                "confidence": p.confidence,
                "risk_level": p.risk_level,
            }
            for p in predictions
        ],
    }
