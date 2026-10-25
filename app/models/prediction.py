"""
Database models for the prediction / audit tracking layer.

Tables:
    - predictions: Every verdict produced by the sync classification pipeline.
    - model_versions: Tracks which agent versions were used for each prediction.
    - audits: Batch audit jobs that group multiple predictions together.
"""
from sqlalchemy import String, Text, Float, Integer, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VerdictFlag(int, enum.Enum):
    """Binary classification flag: 0 = clean, 1 = dark pattern detected."""
    CLEAN = 0
    FLAGGED = 1


# ---------------------------------------------------------------------------
# Prediction  –  one row per pipeline verdict
# ---------------------------------------------------------------------------

class Prediction(Base):
    """
    Stores the output of the synchronous classification pipeline.

    The ``flag`` mirrors the Verdict step: 1 = dark pattern detected.
    ``reasoning_trace`` and ``xai_output`` are populated asynchronously
    *after* the sync pipeline has returned.
    """
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id"), index=True
    )
    # --- Sync verdict ---
    flag: Mapped[int] = mapped_column(Integer, default=0, comment="0=clean, 1=flagged")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW")
    per_message_risk: Mapped[dict] = mapped_column(JSON, nullable=True)
    agent_outputs: Mapped[dict] = mapped_column(JSON, nullable=True,
                                                  comment="Raw outputs from each agent")
    # --- Async: Reasoning-Trace Analysis (populated if flag=1) ---
    reasoning_intent: Mapped[str] = mapped_column(Text, nullable=True,
                                                    comment="Inferred intent behind the dark pattern")
    deliberate_confidence: Mapped[float] = mapped_column(Float, nullable=True,
                                                           comment="Confidence that the pattern is deliberate")
    reasoning_trace_raw: Mapped[dict] = mapped_column(JSON, nullable=True,
                                                        comment="Full reasoning trace output")
    # --- Async: XAI (populated on-demand via /explain) ---
    xai_output: Mapped[dict] = mapped_column(JSON, nullable=True,
                                               comment="LIME weights, SHAP values, heatmap data")
    # --- Meta ---
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_versions.id"), nullable=True
    )
    audit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("audits.id"), nullable=True, comment="NULL when not part of a batch"
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", backref="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")
    audit = relationship("Audit", back_populates="predictions")


# ---------------------------------------------------------------------------
# ModelVersion  –  tracks agent / pipeline versions used for a prediction
# ---------------------------------------------------------------------------

class ModelVersion(Base):
    """
    Records the exact version of each agent and the pipeline that
    produced a prediction.  Essential for reproducibility.
    """
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pipeline_version: Mapped[str] = mapped_column(String(50))
    agent_versions: Mapped[dict] = mapped_column(
        JSON, comment='e.g. {"flattery":"1.0.0","padding":"1.0.0"}'
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="model_version")


# ---------------------------------------------------------------------------
# Audit  –  batch processing job
# ---------------------------------------------------------------------------

class Audit(Base):
    """
    Represents a batch audit job that processes multiple chatbot
    conversations in one go.
    """
    __tablename__ = "audits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    total_conversations: Mapped[int] = mapped_column(Integer, default=0)
    completed_conversations: Mapped[int] = mapped_column(Integer, default=0)
    flagged_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20), default="PENDING",
        comment="PENDING | RUNNING | COMPLETED | FAILED"
    )
    summary: Mapped[dict] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="audit")
