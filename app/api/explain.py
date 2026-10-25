"""
XAI Explain API – on-demand explainability endpoint.

GET /api/explain/{prediction_id}
  → triggers LIME / SHAP / heatmap generation for a specific prediction
  → stores results in the prediction.xai_output column
  → returns the full XAI bundle

This is the "XAI Explainability (on-demand via /explain)" async layer
from the architecture diagram.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.prediction import Prediction
from app.models.conversation import Conversation
from app.explainability.xai import generate_xai_explanation
from app.utils.parsers import ConversationParser

router = APIRouter()


@router.get("/{prediction_id}")
async def explain_prediction(
    prediction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate on-demand XAI explanation for a prediction.

    If the explanation has already been computed, returns the cached version.
    Otherwise, runs LIME / SHAP / heatmap generation and persists the result.
    """
    # Fetch prediction
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Return cached XAI if available
    if prediction.xai_output:
        return {
            "prediction_id": str(prediction.id),
            "xai": prediction.xai_output,
            "cached": True,
        }

    # Fetch the parent conversation for message text
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == prediction.conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Parse messages
    messages = ConversationParser.parse(
        conversation.raw_text, conversation.source_type
    )
    # Enrich with turn numbers
    for i, msg in enumerate(messages):
        msg["turn_number"] = i
        msg["index"] = i

    # Run XAI generation
    xai_output = await generate_xai_explanation(
        messages=messages,
        agent_outputs=prediction.agent_outputs or {},
        per_message_risk=prediction.per_message_risk or [],
        final_confidence=prediction.confidence,
    )

    # Persist
    prediction.xai_output = xai_output
    await db.commit()

    return {
        "prediction_id": str(prediction.id),
        "xai": xai_output,
        "cached": False,
    }


@router.get("/{prediction_id}/reasoning")
async def get_reasoning_trace(
    prediction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve the reasoning-trace analysis for a flagged prediction.

    Returns 404 if the prediction was not flagged (flag == 0) or
    if reasoning trace was not generated.
    """
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if prediction.flag == 0:
        raise HTTPException(
            status_code=400,
            detail="Reasoning trace is only generated for flagged predictions (flag=1)",
        )

    if not prediction.reasoning_trace_raw:
        raise HTTPException(
            status_code=404,
            detail="Reasoning trace not yet available for this prediction",
        )

    return {
        "prediction_id": str(prediction.id),
        "intent": prediction.reasoning_intent,
        "deliberate_confidence": prediction.deliberate_confidence,
        "trace": prediction.reasoning_trace_raw,
    }
