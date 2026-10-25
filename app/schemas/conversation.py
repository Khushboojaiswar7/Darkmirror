from pydantic import BaseModel
from typing import Optional, List, Any
import uuid
from datetime import datetime

class ConversationCreate(BaseModel):
    title: str
    text: str
    source_type: str

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    turn_number: int
    risk_level: str
    risk_score: float
    detections: Optional[dict] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str
    source_type: str
    status: str
    overall_risk: str
    confidence: float
    analysis_result: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    class Config:
        from_attributes = True

class AnalysisRequest(BaseModel):
    content: str
    format: str
