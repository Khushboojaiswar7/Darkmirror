from typing import List, Dict, Any

class Highlighter:
    @staticmethod
    def highlight(text: str, spans: List[List[int]], confidences: List[float]) -> List[Dict[str, Any]]:
        highlights = []
        for span, conf in zip(spans, confidences):
            color = "green"
            if conf > 0.7: color = "red"
            elif conf >= 0.3: color = "yellow"
            
            highlights.append({
                "start": span[0],
                "end": span[1],
                "weight": conf,
                "color": color,
                "text_snippet": text[span[0]:span[1]]
            })
        return highlights
