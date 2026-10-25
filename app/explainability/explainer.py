from typing import List, Dict, Any
from app.schemas.analysis import DetectionResult

class Explainer:
    @staticmethod
    def generate_explanation(result: DetectionResult) -> str:
        if result.pattern_type == "Excessive Flattery":
            return f"The text contains exaggerated personal praise ({', '.join(result.evidence[:3])}) which strongly matches the {result.pattern_type} pattern. Confidence: {result.confidence:.2f}."
        elif result.pattern_type == "Conversational Padding":
            return f"The text contains filler or empty affirmations ({', '.join(result.evidence[:3])}) matching {result.pattern_type}. Confidence: {result.confidence:.2f}."
        else:
            return result.explanation
