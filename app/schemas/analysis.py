"""
Pydantic schemas for the analysis pipeline output.

Updated to reflect the new architecture:
  - Verdict: {flag, confidence, verdict_id, ...}
  - Reasoning-Trace: {intent, deliberate_confidence, trace}
  - XAI: {lime_weights, shap_values, heatmap}
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class DetectionResult(BaseModel):
    """Single detection from a detector agent."""
    message_index: int
    pattern_type: str
    confidence: float
    evidence: List[str]
    highlighted_spans: List[List[int]]
    explanation: str


class AgentOutput(BaseModel):
    """Output from one detector agent."""
    agent_name: str
    results: List[DetectionResult]
    intermediate_features: Dict[str, Any]


class VerdictOutput(BaseModel):
    """Binary verdict produced by the Verdict Agent."""
    flag: int  # 0 = clean, 1 = flagged
    confidence: float
    verdict_id: str
    risk_level: str = "LOW"
    flagged_message_count: int = 0
    total_messages: int = 0


class ReasoningTraceOutput(BaseModel):
    """Output from the async Reasoning-Trace Analysis."""
    intent: str
    deliberate_confidence: float
    trace: List[Dict[str, Any]]
    pattern_types: List[str] = []
    triggered_signals: List[str] = []


class XAIOutput(BaseModel):
    """Output from the on-demand XAI explainability layer."""
    lime_weights: List[Dict[str, Any]]
    shap_values: Dict[str, float]
    heatmap: List[Dict[str, Any]]
    per_message_explanations: List[Dict[str, Any]] = []


class PipelineResult(BaseModel):
    """Full result from the multi-agent classification pipeline."""
    # ── Agent outputs ──
    agents: Dict[str, AgentOutput]
    context_adjustments: List[Dict[str, Any]]
    # ── Aggregated risk ──
    final_risk: str
    final_confidence: float
    per_message_risk: List[Dict[str, Any]]
    summary: str
    # ── Verdict (sync) ──
    verdict: Optional[Dict[str, Any]] = None
    # ── Reasoning trace (async, populated if flag=1) ──
    reasoning_trace: Optional[Dict[str, Any]] = None
    # ── XAI (populated on-demand via /explain) ──
    xai: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    """API response for a prediction."""
    id: str
    conversation_id: str
    flag: int
    confidence: float
    risk_level: str
    verdict: Optional[VerdictOutput] = None
    reasoning_trace: Optional[ReasoningTraceOutput] = None
    xai: Optional[XAIOutput] = None
    created_at: str


class BatchAuditRequest(BaseModel):
    """Request schema for batch audit processing."""
    name: str
    description: Optional[str] = None
    conversations: List[Dict[str, Any]]  # [{text, source_type, title}, ...]


class BatchAuditResponse(BaseModel):
    """Response schema for batch audit results."""
    audit_id: str
    name: str
    status: str
    total_conversations: int
    completed_conversations: int
    flagged_count: int
    predictions: List[PredictionResponse] = []


class ExplainRequest(BaseModel):
    """Request body for on-demand XAI explanation."""
    prediction_id: str
