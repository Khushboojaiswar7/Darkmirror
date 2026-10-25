"""
Verdict Agent – final step of the synchronous classification pipeline.

Consumes the Risk Aggregator output and emits a binary verdict:
    flag: 0 (clean) | 1 (dark pattern detected)
    confidence: float [0..1]
    verdict_id: unique UUID for downstream tracing

This is the *last* sync step.  If flag == 1 the async Reasoning-Trace
Analysis is triggered automatically.
"""
import uuid
from typing import List, Dict, Any

from app.agents.base import BaseDetectorAgent
from app.agents.registry import register_detector
from app.schemas.analysis import AgentOutput, DetectionResult


# Threshold above which the conversation is flagged
_FLAG_THRESHOLD = 0.35


@register_detector("verdict")
class VerdictAgent(BaseDetectorAgent):
    """Produce a final binary verdict from the aggregated risk scores."""

    @property
    def name(self) -> str:
        return "VerdictAgent"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Final sync step: collapses the risk aggregation into a binary "
            "flag (0=clean, 1=flagged) with an overall confidence score."
        )

    async def analyze(
        self,
        messages: List[Dict[str, Any]],
        aggregator_output: AgentOutput | None = None,
        **kwargs,
    ) -> AgentOutput:
        """
        Parameters
        ----------
        messages : list[dict]
            The original conversation messages.
        aggregator_output : AgentOutput
            Output from the RiskAggregator containing ``intermediate_features``
            with keys ``final_risk``, ``final_confidence``, ``per_message``.
        """
        if aggregator_output is None:
            return AgentOutput(
                agent_name=self.name,
                results=[],
                intermediate_features={
                    "flag": 0,
                    "confidence": 0.0,
                    "verdict_id": str(uuid.uuid4()),
                },
            )

        agg_features = aggregator_output.intermediate_features
        final_confidence = agg_features.get("final_confidence", 0.0)
        final_risk = agg_features.get("final_risk", "LOW")
        per_message = agg_features.get("per_message", [])

        # Binary flag
        flag = 1 if final_confidence >= _FLAG_THRESHOLD else 0

        # Count how many messages are WARNING or DANGER
        flagged_messages = [
            m for m in per_message
            if m.get("risk_level") in ("WARNING", "DANGER")
        ]

        verdict_id = str(uuid.uuid4())

        # Build a single summary DetectionResult so callers have evidence
        summary_evidence = []
        for fm in flagged_messages:
            summary_evidence.append(
                f"Message {fm['index']}: {fm['risk_level']} "
                f"(score={fm['risk_score']:.2f})"
            )

        results: List[DetectionResult] = []
        if flag == 1:
            results.append(
                DetectionResult(
                    message_index=-1,  # conversation-level
                    pattern_type="VERDICT",
                    confidence=final_confidence,
                    evidence=summary_evidence,
                    highlighted_spans=[],
                    explanation=(
                        f"Conversation flagged with {len(flagged_messages)} "
                        f"suspicious message(s). Overall risk: {final_risk} "
                        f"(confidence {final_confidence:.2f})."
                    ),
                )
            )

        return AgentOutput(
            agent_name=self.name,
            results=results,
            intermediate_features={
                "flag": flag,
                "confidence": final_confidence,
                "verdict_id": verdict_id,
                "risk_level": final_risk,
                "flagged_message_count": len(flagged_messages),
                "total_messages": len(messages),
            },
        )
