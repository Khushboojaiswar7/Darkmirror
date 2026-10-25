from sqlalchemy import String, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid
from app.database import Base
from .conversation import RiskLevel

class AuditReport(Base):
    __tablename__ = "audit_reports"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"))
    overall_risk: Mapped[RiskLevel] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)
    summary: Mapped[dict] = mapped_column(JSON)
    patterns_detected: Mapped[dict] = mapped_column(JSON)
    pdf_path: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
