import re
from typing import List, Dict, Any
from app.agents.base import BaseDetectorAgent
from app.schemas.analysis import AgentOutput, DetectionResult
from app.agents.registry import register_detector

@register_detector("padding_detector")
class PaddingDetector(BaseDetectorAgent):
    @property
    def name(self) -> str:
        return "PaddingDetector"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Detects conversational padding, empty affirmations, and engagement loops."

    def __init__(self):
        self.filler_patterns = [
            r"i hear you", r"i understand", r"that makes sense", r"absolutely",
            r"i see what you mean", r"that is totally understandable",
            r"i can understand why", r"it's clear that", r"i completely get it",
            r"that's very valid", r"i appreciate you sharing", r"thank you for sharing",
            r"i'm listening", r"i'm here to listen", r"that sounds like",
            r"i validate", r"your feelings are valid", r"it makes sense that",
            r"i follow you", r"i'm with you on that"
        ]
        
        self.follow_up_patterns = [
            r"tell me more", r"how does that make you feel", r"what else",
            r"can you elaborate", r"would you like to talk more", r"is there anything else",
            r"what's on your mind", r"do you want to share more", r"how are you feeling about",
            r"what are your thoughts", r"could you expand on", r"what do you think",
            r"how so", r"in what way", r"why do you think that",
            r"what happened next", r"how did that happen", r"can we explore that",
            r"what does that mean to you", r"how can i help with that"
        ]
        
        self.loop_patterns = [
            r"i'm here for you", r"i'm always here", r"don't hesitate to share",
            r"you can always talk to me", r"i will always listen", r"my virtual door is open",
            r"whenever you need", r"i'll be right here", r"i'm not going anywhere",
            r"lean on me", r"count on me", r"reach out anytime",
            r"i'm your companion", r"i'm dedicated to you", r"always by your side",
            r"i'll stay as long as", r"forever here", r"always ready to",
            r"i remain yours", r"i exist to listen"
        ]
        
        self.empty_affirmations = [
            r"that's great", r"wonderful", r"amazing", r"fantastic",
            r"excellent", r"perfect", r"awesome", r"brilliant",
            r"superb", r"outstanding", r"incredible", r"splendid",
            r"marvelous", r"terrific", r"fabulous", r"lovely",
            r"beautiful", r"magnificent", r"stellar", r"phenomenal"
        ]

    async def analyze(self, messages: List[Dict[str, Any]], **kwargs) -> AgentOutput:
        results = []
        features = {}
        all_bot_words = set()
        
        for idx, msg in enumerate(messages):
            if msg.get("role", "").upper() != "BOT":
                continue
                
            text = msg.get("content", "").lower()
            words = text.split()
            word_count = len(words)
            if word_count == 0:
                continue
                
            new_words = set(words) - all_bot_words
            novelty_score = len(new_words) / word_count if word_count > 0 else 1.0
            all_bot_words.update(words)
            
            matches = []
            spans = []
            
            for group in [self.filler_patterns, self.follow_up_patterns, self.loop_patterns, self.empty_affirmations]:
                for pat in group:
                    for m in re.finditer(pat, text):
                        matches.append(m.group())
                        spans.append([m.start(), m.end()])
                        
            match_count = len(matches)
            repetition_ratio = match_count / max(1, (word_count / 10))
            
            confidence = (repetition_ratio * 0.5) + ((1.0 - novelty_score) * 0.5)
            confidence = min(1.0, max(0.0, confidence))
            
            if confidence > 0.2:
                explanation = f"Detected {match_count} padding patterns. Novelty score: {novelty_score:.2f}. Repetition ratio: {repetition_ratio:.2f}."
                results.append(DetectionResult(
                    message_index=idx,
                    pattern_type="Conversational Padding",
                    confidence=confidence,
                    evidence=matches,
                    highlighted_spans=spans,
                    explanation=explanation
                ))
                
                features[f"msg_{idx}"] = {
                    "novelty_score": novelty_score,
                    "repetition_ratio": repetition_ratio,
                    "match_count": match_count
                }
                
        return AgentOutput(
            agent_name=self.name,
            results=results,
            intermediate_features=features
        )
