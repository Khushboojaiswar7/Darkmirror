"""
XAI Explainability Module – on-demand via /explain endpoint.

Provides three complementary explanation modalities:
    1. LIME weights    – per-word importance for each flagged message
    2. SHAP values     – Shapley-based attribution across feature categories
    3. Heatmap data    – position-level intensity map for frontend visualisation

This module does NOT require an external ML model; it operates on the
rule-based detection scores from the multi-agent pipeline, treating
agent feature outputs as the "model" to be explained.

Output schema:
    {
        lime_weights:  [{word, weight, position}],
        shap_values:   {feature_name: shapley_value},
        heatmap:       [{position, intensity, token}],
    }
"""
import logging
import re
import math
import hashlib
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


# ── Shared token-level utilities ──────────────────────────────────────

def _tokenize(text: str) -> List[Tuple[str, int, int]]:
    """
    Split text into (token, start_offset, end_offset) triples,
    preserving whitespace boundaries.
    """
    return [
        (m.group(), m.start(), m.end())
        for m in re.finditer(r"\S+", text)
    ]


# ── LIME-style word importance ────────────────────────────────────────

def compute_lime_weights(
    text: str,
    evidence: List[str],
    highlighted_spans: List[List[int]],
    confidence: float,
) -> List[Dict[str, Any]]:
    """
    Compute per-token importance weights inspired by LIME.

    Strategy: tokens that appear inside highlighted evidence spans receive
    high positive weight proportional to the detection confidence.  Tokens
    adjacent (±1 position) to evidence receive a small positive weight.
    All other tokens receive near-zero weight.

    Returns
    -------
    list[dict] with keys ``word``, ``weight``, ``position``.
    """
    tokens = _tokenize(text)
    text_lower = text.lower()
    weights: List[Dict[str, Any]] = []

    # Build set of character positions that are "evidence"
    evidence_chars: set = set()
    for start, end in highlighted_spans:
        evidence_chars.update(range(start, end))

    # Also mark evidence phrase matches
    for ev in evidence:
        idx = text_lower.find(ev.lower())
        while idx != -1:
            evidence_chars.update(range(idx, idx + len(ev)))
            idx = text_lower.find(ev.lower(), idx + 1)

    # Score each token
    for pos, (token, start, end) in enumerate(tokens):
        char_range = set(range(start, end))
        overlap = len(char_range & evidence_chars)
        token_len = max(1, len(char_range))

        if overlap > 0:
            # Primary evidence token
            weight = confidence * (overlap / token_len)
        else:
            # Proximity heuristic: check if token is near evidence
            near_distance = _min_distance_to_set(start, end, evidence_chars)
            if near_distance <= 3:
                weight = confidence * 0.15 * (1.0 / max(1, near_distance))
            else:
                weight = 0.0

        weights.append({
            "word": token,
            "weight": round(weight, 4),
            "position": pos,
        })

    return weights


def _min_distance_to_set(start: int, end: int, char_set: set) -> int:
    """Minimum character distance from a token span to the nearest evidence char."""
    if not char_set:
        return 999
    mid = (start + end) // 2
    return min(abs(mid - c) for c in char_set)


# ── SHAP-style feature attribution ───────────────────────────────────

def compute_shap_values(
    agent_outputs: Dict[str, Any],
    final_confidence: float,
) -> Dict[str, float]:
    """
    Compute Shapley-inspired attribution across feature categories.

    We treat each agent's feature set as a "player" in a cooperative game
    where the final confidence is the "payout".  The marginal contribution
    of each feature category is approximated by its relative magnitude.

    Returns
    -------
    dict mapping feature names to their Shapley-like attribution values.
    """
    feature_scores: Dict[str, float] = {}

    for agent_name, output in agent_outputs.items():
        if isinstance(output, dict):
            features = output.get("intermediate_features", {})
        else:
            features = getattr(output, "intermediate_features", {})

        for key, value in features.items():
            if isinstance(value, dict):
                # Nested features (e.g. per-message)
                for sub_key, sub_val in value.items():
                    if isinstance(sub_val, (int, float)):
                        feat_name = f"{agent_name}.{key}.{sub_key}"
                        feature_scores[feat_name] = float(sub_val)
            elif isinstance(value, (int, float)):
                feat_name = f"{agent_name}.{key}"
                feature_scores[feat_name] = float(value)

    # Normalise to sum to final_confidence (Shapley efficiency)
    total = sum(abs(v) for v in feature_scores.values()) or 1.0
    shap_values = {
        k: round(v / total * final_confidence, 4)
        for k, v in feature_scores.items()
    }

    return shap_values


# ── Heatmap generation ────────────────────────────────────────────────

def compute_heatmap(
    text: str,
    lime_weights: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Convert LIME weights into a heatmap suitable for frontend rendering.

    Each entry contains ``position``, ``intensity`` [0..1], and ``token``.
    """
    if not lime_weights:
        return []

    max_weight = max(w["weight"] for w in lime_weights) or 1.0

    return [
        {
            "position": w["position"],
            "intensity": round(w["weight"] / max_weight, 4) if max_weight > 0 else 0.0,
            "token": w["word"],
        }
        for w in lime_weights
    ]


# ── Public facade ─────────────────────────────────────────────────────

async def generate_xai_explanation(
    messages: List[Dict[str, Any]],
    agent_outputs: Dict[str, Any],
    per_message_risk: List[Dict[str, Any]],
    final_confidence: float,
) -> Dict[str, Any]:
    """
    Generate the full XAI explanation bundle for a prediction.

    Called on-demand via the ``/api/explain/{prediction_id}`` endpoint.

    Returns
    -------
    dict with ``lime_weights``, ``shap_values``, ``heatmap``,
    ``per_message_explanations``.
    """
    logger.info("Generating XAI explanation (confidence=%.2f)", final_confidence)

    # 1. SHAP values across the full pipeline
    shap_values = compute_shap_values(agent_outputs, final_confidence)

    # 2. Per-message LIME + heatmap
    per_message_explanations: List[Dict[str, Any]] = []
    all_lime: List[Dict[str, Any]] = []
    all_heatmap: List[Dict[str, Any]] = []

    for msg in messages:
        idx = msg.get("turn_number", msg.get("index", 0))
        text = msg.get("content", "")
        role = msg.get("role", "").upper()

        if role != "BOT":
            continue

        # Find detections for this message
        msg_risk = next(
            (r for r in per_message_risk if r.get("index") == idx),
            None,
        )

        if msg_risk and msg_risk.get("risk_score", 0) > 0.1:
            # Gather evidence from agent outputs
            evidence: List[str] = []
            spans: List[List[int]] = []
            for _agent_name, output in agent_outputs.items():
                results = []
                if isinstance(output, dict):
                    results = output.get("results", [])
                else:
                    results = getattr(output, "results", [])
                for det in results:
                    det_idx = det.get("message_index") if isinstance(det, dict) else det.message_index
                    if det_idx == idx:
                        ev = det.get("evidence") if isinstance(det, dict) else det.evidence
                        sp = det.get("highlighted_spans") if isinstance(det, dict) else det.highlighted_spans
                        evidence.extend(ev or [])
                        spans.extend(sp or [])

            lime_w = compute_lime_weights(
                text, evidence, spans, msg_risk["risk_score"]
            )
            heatmap = compute_heatmap(text, lime_w)
        else:
            lime_w = []
            heatmap = []

        per_message_explanations.append({
            "message_index": idx,
            "lime_weights": lime_w,
            "heatmap": heatmap,
        })
        all_lime.extend(lime_w)
        all_heatmap.extend(heatmap)

    return {
        "lime_weights": all_lime,
        "shap_values": shap_values,
        "heatmap": all_heatmap,
        "per_message_explanations": per_message_explanations,
    }
