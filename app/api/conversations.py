from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.services.analysis_service import AnalysisService
import uuid

router = APIRouter()
analysis_service = AnalysisService()

@router.post("/analyze", response_model=ConversationResponse)
async def analyze(conv: ConversationCreate, db: AsyncSession = Depends(get_db)):
    db_conv = Conversation(
        title=conv.title,
        raw_text=conv.text,
        source_type=conv.source_type,
        user_id=None
    )
    db.add(db_conv)
    await db.commit()
    await db.refresh(db_conv)
    
    result = await analysis_service.analyze(db, db_conv)
    stmt = select(Conversation).where(Conversation.id == result.id).options(selectinload(Conversation.messages))
    res = await db.execute(stmt)
    return res.scalar_one()

@router.get("", response_model=list[ConversationResponse])
async def list_conv(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Conversation).options(selectinload(Conversation.messages)))
    return res.scalars().all()

@router.get("/{id}", response_model=ConversationResponse)
async def get_conv(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Conversation).where(Conversation.id == id).options(selectinload(Conversation.messages)))
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Not found")
    return conv

@router.delete("/{id}")
async def delete_conv(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Conversation).where(Conversation.id == id))
    conv = res.scalar_one_or_none()
    if conv:
        await db.delete(conv)
        await db.commit()
    return {"status": "deleted"}
