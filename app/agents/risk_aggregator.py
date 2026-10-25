from typing import List, Dict, Any
from app.agents.base import BaseDetectorAgent
from app.schemas.analysis import AgentOutput, DetectionResult
from app.agents.registry import register_detector

@register_detector("risk_aggregator")
class RiskAggregator(BaseDetectorAgent):
    @property
    def name(self) -> str:
        return "RiskAggregator"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Aggregates risk scores across all models."

    async def analyze(self, messages: List[Dict[str, Any]], context_results: List[DetectionResult] = None, **kwargs) -> AgentOutput:
        features = {}
        
        if not context_results:
            return AgentOutput(agent_name=self.name, results=[], intermediate_features={"final_risk": "SAFE", "final_confidence": 0.0})
            
        msg_risks = {}
        for res in context_results:
            idx = res.message_index
            if idx not in msg_risks:
                msg_risks[idx] = []
            msg_risks[idx].append(res.confidence)
            
        per_message = []
        for idx in range(len(messages)):
            conf = max(msg_risks.get(idx, [0.0]))
            level = "SAFE"
            if conf > 0.6: level = "DANGER"
            elif conf >= 0.3: level = "WARNING"
            
            per_message.append({
                "index": idx,
                "risk_level": level,
                "risk_score": conf
            })
            
        weights = [1.0 + (i / len(messages)) for i in range(len(messages))]
        total_weight = sum(weights)
        
        agg_score = 0.0
        for p, w in zip(per_message, weights):
            agg_score += p["risk_score"] * w
            
        final_confidence = agg_score / total_weight if total_weight > 0 else 0.0
        
        final_risk = "LOW"
        if final_confidence > 0.6: final_risk = "HIGH"
        elif final_confidence >= 0.3: final_risk = "MEDIUM"
        
        features["final_risk"] = final_risk
        features["final_confidence"] = final_confidence
        features["per_message"] = per_message
        
        return AgentOutput(
            agent_name=self.name,
            results=[],
            intermediate_features=features
        )
