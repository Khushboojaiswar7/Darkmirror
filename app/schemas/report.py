from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class ReportCreate(BaseModel):
    conversation_id: uuid.UUID

class ReportResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    overall_risk: str
    confidence: float
    summary: Dict[str, Any]
    patterns_detected: Dict[str, Any]
    pdf_path: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ReportDownload(BaseModel):
    format: str
