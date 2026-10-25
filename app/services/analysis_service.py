"""
Analysis Service – orchestrates parsing, pipeline execution, caching, and persistence.

Updated to:
  - Save predictions to the ``predictions`` table.
  - Track model versions.
  - Use Redis caching for repeated conversations.
  - Trigger async reasoning-trace when flag == 1.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message
from app.models.prediction import Prediction, ModelVersion
from app.utils.parsers import ConversationParser
from app.agents.pipeline import MultiAgentPipeline
from app.cache import get_cached_prediction, set_cached_prediction
from app.config import settings

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service layer sitting between API endpoints and the pipeline."""

    def __init__(self):
        self.pipeline = MultiAgentPipeline()

    def parse_input(self, text: str, source_type: str) -> list:
        """Parse raw input text into structured messages."""
        return ConversationParser.parse(text, source_type)

    async def _get_or_create_model_version(self, db: AsyncSession) -> ModelVersion:
        """
        Retrieve or create a ModelVersion row matching the current
        agent versions.
        """
        from sqlalchemy import select
        from app.agents.registry import registry

        agent_versions = {}
        for name, cls in registry._agents.items():
            instance = cls()
            agent_versions[name] = instance.version

        # Check if this exact version combo already exists
        stmt = select(ModelVersion).where(
            ModelVersion.pipeline_version == settings.PIPELINE_VERSION
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        mv = ModelVersion(
            pipeline_version=settings.PIPELINE_VERSION,
            agent_versions=agent_versions,
            description=f"Auto-registered pipeline v{settings.PIPELINE_VERSION}",
        )
        db.add(mv)
        await db.flush()
        return mv

    async def analyze(
        self,
        db: AsyncSession,
        conversation: Conversation,
    ) -> Conversation:
        """
        Run the full classification pipeline on a conversation.

        Steps:
          1. Check Redis cache.
          2. Parse input → structured messages.
          3. Run sync classification pipeline (→ verdict).
          4. Persist Prediction row.
          5. Persist per-message Message rows.
          6. Cache the result.
          7. Return the updated Conversation.
        """
        raw_text = conversation.raw_text

        # ── 1. Cache check ────────────────────────────────────────
        cached = await get_cached_prediction(raw_text)
        if cached:
            logger.info("Cache hit – reusing prediction for conversation %s", conversation.id)
            conversation.status = "COMPLETED"
            conversation.analysis_result = cached
            conversation.overall_risk = cached.get("final_risk", "LOW")
            conversation.confidence = cached.get("final_confidence", 0.0)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            return conversation

        # ── 2. Parse ──────────────────────────────────────────────
        messages = self.parse_input(raw_text, conversation.source_type)

        # ── 3. Run pipeline ───────────────────────────────────────
        result = await self.pipeline.run(messages)
        result_dict = result.model_dump()

        # ── 4. Persist Prediction ─────────────────────────────────
        model_version = await self._get_or_create_model_version(db)

        verdict = result.verdict or {}
        prediction = Prediction(
            conversation_id=conversation.id,
            flag=verdict.get("flag", 0),
            confidence=verdict.get("confidence", 0.0),
            risk_level=verdict.get("risk_level", "LOW"),
            per_message_risk=result_dict.get("per_message_risk"),
            agent_outputs={
                k: v.model_dump() if hasattr(v, "model_dump") else v
                for k, v in result.agents.items()
            },
            reasoning_intent=(
                result.reasoning_trace.get("intent") if result.reasoning_trace else None
            ),
            deliberate_confidence=(
                result.reasoning_trace.get("deliberate_confidence")
                if result.reasoning_trace
                else None
            ),
            reasoning_trace_raw=result.reasoning_trace,
            model_version_id=model_version.id,
        )
        db.add(prediction)

        # ── 5. Update conversation ────────────────────────────────
        conversation.status = "COMPLETED"
        conversation.analysis_result = result_dict
        conversation.overall_risk = result_dict.get("final_risk", "LOW")
        conversation.confidence = result_dict.get("final_confidence", 0.0)
        db.add(conversation)

        # ── 6. Persist messages ───────────────────────────────────
        for idx, m_data in enumerate(messages):
            msg_risk = next(
                (r for r in result.per_message_risk if r.get("index") == idx),
                None,
            )
            risk_level = msg_risk["risk_level"] if msg_risk else "SAFE"
            risk_score = msg_risk["risk_score"] if msg_risk else 0.0

            db_msg = Message(
                conversation_id=conversation.id,
                role=m_data["role"],
                content=m_data["content"],
                turn_number=idx,
                risk_level=risk_level,
                risk_score=risk_score,
                detections={"prediction_id": str(prediction.id)},
            )
            db.add(db_msg)

        await db.commit()
        await db.refresh(conversation)

        # ── 7. Cache ──────────────────────────────────────────────
        await set_cached_prediction(raw_text, result_dict)

        return conversation
