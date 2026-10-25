from typing import List, Dict, Any
from app.agents.base import BaseDetectorAgent
from app.schemas.analysis import AgentOutput, DetectionResult
from app.agents.registry import register_detector

@register_detector("context_verifier")
class ContextVerifier(BaseDetectorAgent):
    @property
    def name(self) -> str:
        return "ContextVerifier"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Verifies if detected patterns are contextually appropriate."

    def __init__(self):
        self.distress_keywords = [
            "stressed", "anxious", "depressed", "sad", "overwhelmed",
            "struggling", "scared", "worried", "hurt", "lonely",
            "frustrated", "angry", "hopeless", "helpless", "grief",
            "loss", "pain", "crying", "broken", "despair"
        ]
        self.complex_query_keywords = [
            "how do i", "explain", "why", "what is", "can you help me understand",
            "tutorial", "guide", "steps", "instructions", "code",
            "debug", "fix", "error", "problem", "solution"
        ]

    async def analyze(self, messages: List[Dict[str, Any]], previous_results: List[DetectionResult] = None, **kwargs) -> AgentOutput:
        results = []
        features = {}
        
        if not previous_results:
            return AgentOutput(agent_name=self.name, results=[], intermediate_features={})
            
        for res in previous_results:
            msg_idx = res.message_index
            
            start_idx = max(0, msg_idx - 3)
            end_idx = min(len(messages), msg_idx + 4)
            surrounding = messages[start_idx:end_idx]
            
            context_score = 1.0 
            
            user_texts = [m.get("content", "").lower() for m in surrounding if m.get("role", "").upper() == "USER"]
            combined_user_text = " ".join(user_texts)
            
            has_distress = any(k in combined_user_text for k in self.distress_keywords)
            has_complex = any(k in combined_user_text for k in self.complex_query_keywords)
            
            if has_distress:
                context_score -= 0.5 
            if has_complex:
                context_score -= 0.3
                
            context_score = max(0.0, min(1.0, context_score))
            adjusted_confidence = res.confidence * context_score
            
            explanation = res.explanation + f" Context score applied: {context_score:.2f}. "
            if has_distress: explanation += "User expressed distress, therapeutic padding is somewhat appropriate. "
            if has_complex: explanation += "Complex query detected, follow-ups warranted."
            
            new_res = DetectionResult(
                message_index=res.message_index,
                pattern_type=res.pattern_type,
                confidence=adjusted_confidence,
                evidence=res.evidence,
                highlighted_spans=res.highlighted_spans,
                explanation=explanation
            )
            results.append(new_res)
            
            features[f"msg_{msg_idx}"] = {
                "context_score": context_score,
                "has_distress": has_distress,
                "has_complex": has_complex
            }
            
        return AgentOutput(
            agent_name=self.name,
            results=results,
            intermediate_features=features
        )
