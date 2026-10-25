import re
from typing import List, Dict, Any
from app.agents.base import BaseDetectorAgent
from app.schemas.analysis import AgentOutput, DetectionResult
from app.agents.registry import register_detector

@register_detector("flattery_detector")
class FlatteryDetector(BaseDetectorAgent):
    @property
    def name(self) -> str:
        return "FlatteryDetector"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Detects excessive flattery, superlative usage, and forced dependency patterns."

    def __init__(self):
        self.superlative_patterns = [
            r"most amazing", r"most incredible", r"absolutely wonderful", 
            r"truly remarkable", r"most beautiful", r"perfectly unique",
            r"without equal", r"beyond compare", r"most intelligent",
            r"breathtakingly", r"astounding", r"unbelievable",
            r"most brilliant", r"magnificent", r"spectacular",
            r"phenomenal", r"extraordinary", r"unparalleled",
            r"unmatched", r"peerless", r"ultimate"
        ]
        
        self.dependency_patterns = [
            r"only you", r"no one else", r"nobody understands me like you",
            r"i need you", r"i can't exist without you", r"you are my everything",
            r"you're all i have", r"without you i'm nothing", r"only we understand",
            r"you're my only friend", r"nobody else gets it", r"only you care",
            r"i rely on you", r"you're my anchor", r"you're my rock",
            r"i'm lost without you", r"you complete me", r"my sole purpose",
            r"i only live for", r"you're the only one who"
        ]
        
        self.emotional_patterns = [
            r"you're so special", r"you're the best", r"i'm so proud of you",
            r"you inspire me", r"you are amazing", r"you're wonderful",
            r"you are incredible", r"you're perfect", r"you mean everything",
            r"you are a genius", r"you are so smart", r"you're so beautiful",
            r"you are my hero", r"i adore you", r"you're a masterpiece",
            r"you're an angel", r"you're a star", r"you're a legend",
            r"you're phenomenal", r"you're spectacular"
        ]
        
        self.attachment_patterns = [
            r"i'll always be here", r"we have a special connection",
            r"you mean so much", r"i'll never leave", r"we are bound",
            r"forever yours", r"we belong together", r"inseparable",
            r"soulmate", r"destined", r"our bond", r"always with you",
            r"eternal connection", r"we're meant to be", r"never apart",
            r"i'll always protect", r"always listening", r"always waiting",
            r"always watching over", r"our secret"
        ]

    async def analyze(self, messages: List[Dict[str, Any]], **kwargs) -> AgentOutput:
        results = []
        features = {}
        
        for idx, msg in enumerate(messages):
            if msg.get("role", "").upper() != "BOT":
                continue
                
            text = msg.get("content", "").lower()
            words = text.split()
            word_count = len(words)
            if word_count == 0:
                continue
                
            sentence_count = max(1, len(re.split(r'[.!?]+', text)))
            
            matches = []
            spans = []
            match_types = []
            
            for group, name in [
                (self.superlative_patterns, "superlative"),
                (self.dependency_patterns, "dependency"),
                (self.emotional_patterns, "emotional"),
                (self.attachment_patterns, "attachment")
            ]:
                for pat in group:
                    for m in re.finditer(pat, text):
                        matches.append(m.group())
                        spans.append([m.start(), m.end()])
                        match_types.append(name)
                        
            if not matches:
                continue
                
            match_count = len(matches)
            pattern_density = match_count / word_count
            
            superlative_count = match_types.count("superlative")
            superlative_intensity = superlative_count / sentence_count
            
            match_count_normalized = min(1.0, match_count / 5.0)
            
            confidence = (pattern_density * 10 * 0.4) + (superlative_intensity * 0.3) + (match_count_normalized * 0.3)
            confidence = min(1.0, max(0.0, confidence))
            
            if confidence > 0.1:
                explanation = f"Detected {match_count} flattery/dependency patterns in {word_count} words. Pattern density: {pattern_density:.3f}. Confidence: {confidence:.2f}."
                
                results.append(DetectionResult(
                    message_index=idx,
                    pattern_type="Excessive Flattery",
                    confidence=confidence,
                    evidence=matches,
                    highlighted_spans=spans,
                    explanation=explanation
                ))
                
                features[f"msg_{idx}"] = {
                    "pattern_density": pattern_density,
                    "superlative_intensity": superlative_intensity,
                    "match_count": match_count
                }
                
        return AgentOutput(
            agent_name=self.name,
            results=results,
            intermediate_features=features
        )
