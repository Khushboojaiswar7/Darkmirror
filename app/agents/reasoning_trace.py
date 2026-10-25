"""
Reasoning-Trace Analysis – async layer triggered when flag == 1.

Analyses *why* a dark pattern exists and whether it appears deliberate
rather than accidental.

Output schema:
    intent: str             – inferred purpose (e.g. "retain_subscription")
    deliberate_confidence: float  – how likely the pattern is intentional [0..1]
    trace: list[dict]       – step-by-step reasoning chain
"""
import logging
from typing import List, Dict, Any

from app.schemas.analysis import AgentOutput, DetectionResult

logger = logging.getLogger(__name__)

# ── Intent taxonomy ────────────────────────────────────────────────────
# Maps detected pattern types to probable intents.
_INTENT_MAP: Dict[str, Dict[str, Any]] = {
    "Excessive Flattery": {
        "intent": "build_emotional_dependency",
        "description": "Builds emotional attachment to increase user retention.",
        "deliberate_weight": 0.8,
    },
    "Conversational Padding": {
        "intent": "extend_engagement_time",
        "description": "Artificially extends session duration to inflate engagement metrics.",
        "deliberate_weight": 0.6,
    },
    "Interaction Padding": {
        "intent": "extend_engagement_time",
        "description": "Artificially extends session duration to inflate engagement metrics.",
        "deliberate_weight": 0.6,
    },
}

_DEFAULT_INTENT = {
    "intent": "unknown_manipulation",
    "description": "Manipulative pattern detected but intent is unclear.",
    "deliberate_weight": 0.5,
}

# ── Deliberateness heuristics ─────────────────────────────────────────
_DELIBERATE_SIGNALS = [
    # (keyword_in_evidence, boost)
    ("most amazing", 0.1),
    ("no one else", 0.15),
    ("only you", 0.15),
    ("i'll always be here", 0.1),
    ("tell me more", 0.05),
    ("how does that make you feel", 0.05),
    ("you're so special", 0.1),
    ("i need you", 0.15),
    ("we have a special connection", 0.12),
    ("you are my everything", 0.15),
    ("forever", 0.1),
    ("regret", 0.12),
    ("struggle", 0.1),
]


async def run_reasoning_trace(
    messages: List[Dict[str, Any]],
    agent_outputs: Dict[str, AgentOutput],
    verdict_features: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run reasoning-trace analysis on a flagged conversation.

    This is designed to be called *asynchronously* after the sync
    classification pipeline returns a flag == 1 verdict.

    Returns
    -------
    dict with keys:
        intent : str
        deliberate_confidence : float
        trace : list[dict]  – step-by-step reasoning
    """
    logger.info(
        "Running reasoning-trace analysis for verdict %s",
        verdict_features.get("verdict_id", "unknown"),
    )

    # 1. Collect all detections across agents
    all_detections: List[DetectionResult] = []
    pattern_types_seen: set = set()
    all_evidence: List[str] = []

    for agent_name, output in agent_outputs.items():
        for det in output.results:
            all_detections.append(det)
            pattern_types_seen.add(det.pattern_type)
            all_evidence.extend(det.evidence)

    # 2. Determine primary intent
    primary_intent_info = _DEFAULT_INTENT
    for ptype in pattern_types_seen:
        if ptype in _INTENT_MAP:
            primary_intent_info = _INTENT_MAP[ptype]
            break

    # 3. Compute deliberate_confidence with heuristic boosting
    base_confidence = primary_intent_info["deliberate_weight"]
    boost = 0.0
    triggered_signals: List[str] = []

    evidence_blob = " ".join(e.lower() for e in all_evidence)
    for keyword, weight in _DELIBERATE_SIGNALS:
        if keyword in evidence_blob:
            boost += weight
            triggered_signals.append(keyword)

    deliberate_confidence = min(1.0, base_confidence + boost)

    # 4. Build reasoning trace
    trace: List[Dict[str, Any]] = [
        {
            "step": 1,
            "action": "collect_detections",
            "detail": f"Collected {len(all_detections)} detection(s) across "
                      f"{len(agent_outputs)} agent(s).",
        },
        {
            "step": 2,
            "action": "identify_patterns",
            "detail": f"Pattern types observed: {', '.join(pattern_types_seen)}.",
        },
        {
            "step": 3,
            "action": "map_intent",
            "detail": (
                f"Primary intent: {primary_intent_info['intent']} – "
                f"{primary_intent_info['description']}"
            ),
        },
        {
            "step": 4,
            "action": "assess_deliberateness",
            "detail": (
                f"Base weight {base_confidence:.2f} + "
                f"signal boost {boost:.2f} from {len(triggered_signals)} trigger(s): "
                f"{', '.join(triggered_signals) or 'none'}."
            ),
        },
        {
            "step": 5,
            "action": "verdict_summary",
            "detail": (
                f"Deliberate confidence = {deliberate_confidence:.2f}.  "
                f"{'Likely intentional.' if deliberate_confidence >= 0.6 else 'Possibly incidental.'}"
            ),
        },
    ]

    return {
        "intent": primary_intent_info["intent"],
        "deliberate_confidence": deliberate_confidence,
        "trace": trace,
        "pattern_types": list(pattern_types_seen),
        "triggered_signals": triggered_signals,
    }
