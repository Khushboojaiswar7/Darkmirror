"""
Analytics API – dashboard statistics, trends, and pattern distribution.

Queries the predictions and conversations tables for real aggregated data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.conversation import Conversation
from app.models.prediction import Prediction

router = APIRouter()


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    """
    Aggregate dashboard statistics.

    Returns total conversations, predictions, average risk,
    flag rate, and recent activity.
    """
    # Total conversations
    total_result = await db.execute(select(func.count(Conversation.id)))
    total_conversations = total_result.scalar() or 0

    # Total predictions
    pred_count_result = await db.execute(select(func.count(Prediction.id)))
    total_predictions = pred_count_result.scalar() or 0

    # Average confidence
    avg_conf_result = await db.execute(select(func.avg(Prediction.confidence)))
    avg_confidence = round(avg_conf_result.scalar() or 0.0, 3)

    # Flagged count
    flagged_result = await db.execute(
        select(func.count(Prediction.id)).where(Prediction.flag == 1)
    )
    flagged_count = flagged_result.scalar() or 0

    flag_rate = round(flagged_count / max(1, total_predictions), 3)

    return {
        "total_conversations": total_conversations,
        "total_predictions": total_predictions,
        "average_confidence": avg_confidence,
        "flagged_count": flagged_count,
        "flag_rate": flag_rate,
        "avg_risk": avg_confidence,
    }


@router.get("/trends")
async def trends(db: AsyncSession = Depends(get_db)):
    """Time-series trend data for charts."""
    # Return recent conversations with risk scores
    result = await db.execute(
        select(Conversation)
        .where(Conversation.status == "COMPLETED")
        .order_by(Conversation.created_at.desc())
        .limit(50)
    )
    conversations = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "risk": c.overall_risk,
            "confidence": c.confidence,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in conversations
    ]


@router.get("/patterns")
async def patterns(db: AsyncSession = Depends(get_db)):
    """Pattern distribution across all predictions."""
    result = await db.execute(select(Prediction).where(Prediction.flag == 1))
    predictions = result.scalars().all()

    distribution: dict = {}
    for pred in predictions:
        if pred.agent_outputs:
            for agent_name, output in pred.agent_outputs.items():
                results = output.get("results", []) if isinstance(output, dict) else []
                for det in results:
                    ptype = det.get("pattern_type", "Unknown")
                    distribution[ptype] = distribution.get(ptype, 0) + 1

    return [
        {"name": name, "count": count}
        for name, count in sorted(distribution.items(), key=lambda x: -x[1])
    ]
