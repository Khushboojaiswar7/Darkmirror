import asyncio
import logging
from typing import List, Dict, Any, Optional

import app.agents  # Ensures all agent submodules are imported and registered
from app.agents.registry import registry
from app.agents.reasoning_trace import run_reasoning_trace
from app.schemas.analysis import PipelineResult, AgentOutput

logger = logging.getLogger(__name__)


class MultiAgentPipeline:
    """
    Orchestrates the full multi-agent detection pipeline.

    The ``run`` method executes the **synchronous** classification steps
    and, when the Verdict flag is 1, automatically fires the async
    Reasoning-Trace Analysis.  XAI is *not* triggered here – it is
    invoked on-demand via the ``/api/explain`` endpoint.
    """

    def __init__(self):
        self.flattery = registry.get("flattery_detector")
        self.padding = registry.get("padding_detector")
        self.guilt_trip = registry.get("guilt_trip_detector")
        self.context = registry.get("context_verifier")
        self.aggregator = registry.get("risk_aggregator")
        self.verdict_agent = registry.get("verdict")

    async def run(self, messages: List[Dict[str, Any]]) -> PipelineResult:
        """
        Execute the full pipeline.

        Returns a ``PipelineResult`` enriched with verdict and, when
        applicable, reasoning-trace data.
        """
        # ── Step 1: Parallel detection ─────────────────────────────
        logger.info("Pipeline: running flattery, padding & guilt_trip detectors in parallel")
        flat_res, pad_res, guilt_res = await asyncio.gather(
            self.flattery.analyze(messages),
            self.padding.analyze(messages),
            self.guilt_trip.analyze(messages),
        )

        # ── Step 2: Context verification (FP reduction) ───────────
        combined_results = flat_res.results + pad_res.results + guilt_res.results
        logger.info("Pipeline: context verification on %d detections", len(combined_results))
        context_out = await self.context.analyze(
            messages, previous_results=combined_results
        )

        # ── Step 3: Risk aggregation ──────────────────────────────
        logger.info("Pipeline: risk aggregation")
        agg_out = await self.aggregator.analyze(
            messages, context_results=context_out.results
        )

        # ── Step 4: Verdict ───────────────────────────────────────
        logger.info("Pipeline: computing verdict")
        verdict_out = await self.verdict_agent.analyze(
            messages, aggregator_output=agg_out
        )
        verdict_features = verdict_out.intermediate_features
        flag = verdict_features.get("flag", 0)
        logger.info(
            "Pipeline verdict: flag=%d  confidence=%.3f  id=%s",
            flag,
            verdict_features.get("confidence", 0.0),
            verdict_features.get("verdict_id", "?"),
        )

        # ── Step 5 (async): Reasoning-Trace Analysis if flag==1 ──
        reasoning_trace: Optional[Dict[str, Any]] = None
        if flag == 1:
            logger.info("Pipeline: flag=1 → running async reasoning-trace analysis")
            agent_outputs_map = {
                "flattery_detector": flat_res,
                "padding_detector": pad_res,
                "guilt_trip_detector": guilt_res,
            }
            reasoning_trace = await run_reasoning_trace(
                messages, agent_outputs_map, verdict_features
            )

        # ── Assemble result ───────────────────────────────────────
        return PipelineResult(
            agents={
                "flattery_detector": flat_res,
                "padding_detector": pad_res,
                "guilt_trip_detector": guilt_res,
            },
            context_adjustments=[r.model_dump() for r in context_out.results],
            final_risk=agg_out.intermediate_features.get("final_risk", "LOW"),
            final_confidence=agg_out.intermediate_features.get("final_confidence", 0.0),
            per_message_risk=agg_out.intermediate_features.get("per_message", []),
            summary=(
                f"Verdict: {'FLAGGED' if flag else 'CLEAN'} "
                f"(confidence={verdict_features.get('confidence', 0):.2f}). "
                + (
                    f"Intent: {reasoning_trace['intent']}. "
                    f"Deliberate confidence: {reasoning_trace['deliberate_confidence']:.2f}."
                    if reasoning_trace
                    else "No dark patterns detected."
                )
            ),
            verdict=verdict_features,
            reasoning_trace=reasoning_trace,
        )
