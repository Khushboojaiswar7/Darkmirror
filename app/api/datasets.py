"""
Datasets API – dataset management, manual labeling, and export.
"""
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.evaluation_service import EvaluationService

router = APIRouter()
eval_service = EvaluationService()


class CreateDatasetRequest(BaseModel):
    name: str
    description: str


class ImportConversationsRequest(BaseModel):
    conversations: List[Dict[str, Any]]
    annotator: Optional[str] = "Expert_A"


class AnnotateRequest(BaseModel):
    labels: Dict[str, Any]
    annotator: str


@router.get("")
async def list_datasets(db: AsyncSession = Depends(get_db)):
    """List all annotated datasets."""
    return await eval_service.list_datasets(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_dataset(
    request: CreateDatasetRequest, db: AsyncSession = Depends(get_db)
):
    """Create a new dataset."""
    ds = await eval_service.import_dataset(db, request.name, request.description)
    return {
        "id": str(ds.id),
        "name": ds.name,
        "description": ds.description,
        "conversation_count": 0,
        "created_at": ds.created_at.isoformat() if ds.created_at else None,
    }


@router.get("/{id}")
async def get_dataset(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a dataset by ID."""
    ds = await eval_service.get_dataset(db, id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {
        "id": str(ds.id),
        "name": ds.name,
        "description": ds.description,
        "created_at": ds.created_at.isoformat() if ds.created_at else None,
    }


@router.post("/{id}/import")
async def import_conversations(
    id: uuid.UUID,
    request: ImportConversationsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Import conversation samples into a dataset."""
    ds = await eval_service.get_dataset(db, id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    created = await eval_service.add_conversations(
        db, id, request.conversations, request.annotator or "Expert_A"
    )
    return {"status": "success", "imported_count": len(created)}


@router.post("/conversations/{conv_id}/annotate")
async def annotate_conversation(
    conv_id: uuid.UUID,
    request: AnnotateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Annotate an existing conversation with ground-truth dark pattern labels."""
    conv = await eval_service.annotate(db, conv_id, request.labels, request.annotator)
    if not conv:
        raise HTTPException(status_code=404, detail="Annotated conversation not found")
    return {"status": "annotated", "id": str(conv.id), "labels": conv.labels}


@router.put("/conversations/{conv_id}/approve")
async def approve_annotation(
    conv_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Approve a reviewed annotation."""
    conv = await eval_service.approve_annotation(db, conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Annotated conversation not found")
    return {"status": "approved", "id": str(conv.id)}


@router.get("/{id}/export")
async def export_dataset(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Export the dataset and all labeled conversations."""
    data = await eval_service.export_dataset(db, id)
    if not data:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return data


@router.get("/{id}/agreement")
async def get_agreement(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get inter-annotator agreement metrics for the dataset."""
    return await eval_service.compute_agreement(db, id)
