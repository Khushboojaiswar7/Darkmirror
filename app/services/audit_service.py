"""
Audit Service – batch processing of chatbot conversations.

Corresponds to the "Audit Service" box in the architecture diagram.
Accepts a batch of conversations, runs the pipeline on each, and
produces an aggregated audit summary.
"""
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.conversation import Conversation
from app.models.prediction import Audit, Prediction
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)


class AuditService:
    """Batch-process chatbot conversations and aggregate audit results."""

    def __init__(self):
        self.analysis_service = AnalysisService()

    async def create_audit(
        self,
        db: AsyncSession,
        name: str,
        description: str | None,
        conversations_data: List[Dict[str, Any]],
    ) -> Audit:
        """
        Create a batch audit and begin processing conversations.

        Parameters
        ----------
        name : str
            Human-readable audit name.
        description : str | None
            Optional description.
        conversations_data : list[dict]
            Each dict has keys: ``text``, ``source_type``, ``title``.

        Returns
        -------
        Audit with updated status and prediction references.
        """
        audit = Audit(
            name=name,
            description=description,
            total_conversations=len(conversations_data),
            status="RUNNING",
            started_at=datetime.utcnow(),
        )
        db.add(audit)
        await db.flush()

        flagged = 0
        completed = 0

        for conv_data in conversations_data:
            try:
                # Create Conversation row
                conversation = Conversation(
                    title=conv_data.get("title", f"Batch item {completed + 1}"),
                    raw_text=conv_data["text"],
                    source_type=conv_data.get("source_type", "TEXT"),
                    user_id=None,
                )
                db.add(conversation)
                await db.flush()

                # Run pipeline
                result_conv = await self.analysis_service.analyze(db, conversation)

                # Link prediction to audit
                pred_result = await db.execute(
                    select(Prediction)
                    .where(Prediction.conversation_id == conversation.id)
                    .order_by(Prediction.created_at.desc())
                )
                prediction = pred_result.scalar_one_or_none()
                if prediction:
                    prediction.audit_id = audit.id
                    if prediction.flag == 1:
                        flagged += 1

                completed += 1

            except Exception as exc:
                logger.error("Audit batch item failed: %s", exc)
                continue

        # Finalise audit
        audit.completed_conversations = completed
        audit.flagged_count = flagged
        audit.status = "COMPLETED"
        audit.completed_at = datetime.utcnow()
        audit.summary = {
            "total": len(conversations_data),
            "completed": completed,
            "flagged": flagged,
            "clean": completed - flagged,
            "flag_rate": round(flagged / max(1, completed), 3),
        }

        await db.commit()
        await db.refresh(audit)
        return audit

    async def get_audit(self, db: AsyncSession, audit_id: uuid.UUID) -> Audit | None:
        """Retrieve an audit by ID."""
        result = await db.execute(select(Audit).where(Audit.id == audit_id))
        return result.scalar_one_or_none()

    async def list_audits(self, db: AsyncSession) -> List[Audit]:
        """List all audits."""
        result = await db.execute(select(Audit).order_by(Audit.created_at.desc()))
        return list(result.scalars().all())
