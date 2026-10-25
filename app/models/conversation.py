from sqlalchemy import String, Text, Enum, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base

class SourceType(str, enum.Enum):
    TEXT = "TEXT"
    TXT = "TXT"
    JSON = "JSON"
    CSV = "CSV"

class Status(str, enum.Enum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NONE = "NONE"
    SAFE = "SAFE"
    WARNING = "WARNING"
    DANGER = "DANGER"

class RoleEnum(str, enum.Enum):
    USER = "USER"
    BOT = "BOT"

class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    raw_text: Mapped[str] = mapped_column(Text)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING)
    analysis_result: Mapped[dict] = mapped_column(JSON, nullable=True)
    overall_risk: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), default=RiskLevel.NONE)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", lazy="selectin")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum))
    content: Mapped[str] = mapped_column(Text)
    turn_number: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), default=RiskLevel.SAFE)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    detections: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")
