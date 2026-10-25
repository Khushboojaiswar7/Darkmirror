"""
4-Tier Ensemble Detector Agent.

Fuses outputs from:
- Tier 1: Deterministic Rule-Based Agents (Flattery, Padding, Guilt-Trip)
- Tier 2: Statistical Semantic Classifier (TF-IDF + Logistic Regression)
- Tier 3: Transformer Classifier (DistilBERT contextual embeddings / ONNX)
- Tier 4: Calibrated Soft-Voting Ensemble Meta-Learner
"""
import os
import pickle
import logging
from typing import List, Dict, Any, Optional

from app.agents.base import BaseDetectorAgent
from app.agents.registry import register_detector
from app.schemas.analysis import AgentOutput, DetectionResult

logger = logging.getLogger(__name__)


@register_detector("ensemble_detector")
class EnsembleDetector(BaseDetectorAgent):
    """
    Combines rule-based pattern matching with statistical ML and deep contextual signals
    using a weighted soft-voting meta-decision mechanism.
    """

    def __init__(self):
        super().__init__()
        self._name = "EnsembleDetector"
        self._version = "1.1.0"
        self.tfidf_pipeline = None
        self.distilbert_pipeline = None
        self._load_models()

    def _load_models(self):
        """Attempt to load Tier 2 (TF-IDF) and Tier 3 (DistilBERT) models."""
        self._load_tfidf_model()
        self._load_distilbert_model()

    def _load_tfidf_model(self):
        """Attempt to load pre-trained TF-IDF model if available."""
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, "..", "..", "data", "tfidf_baseline_model.pkl")
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    self.tfidf_pipeline = pickle.load(f)
                logger.info("EnsembleDetector: Loaded Tier 2 TF-IDF model from %s", model_path)
            except Exception as e:
                logger.warning("Could not load TF-IDF model: %s", e)

    def _load_distilbert_model(self):
        """Attempt to load fine-tuned Tier 3 DistilBERT model if available."""
        base_dir = os.path.dirname(__file__)
        candidate_dirs = [
            os.path.join(base_dir, "..", "..", "data", "distilbert_darkmirror_model"),
            os.path.join(base_dir, "..", "..", "ml"),
            os.path.join(base_dir, "..", "..", "ml", "distilbert_darkmirror_model"),
        ]

        found_dir = None
        for cdir in candidate_dirs:
            has_config = os.path.exists(os.path.join(cdir, "config.json"))
            has_weights = (
                os.path.exists(os.path.join(cdir, "model.safetensors"))
                or os.path.exists(os.path.join(cdir, "pytorch_model.bin"))
            )
            if os.path.isdir(cdir) and has_config and has_weights:
                found_dir = cdir
                break

        if found_dir:
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
                tokenizer = AutoTokenizer.from_pretrained(found_dir)
                model = AutoModelForSequenceClassification.from_pretrained(found_dir)
                self.distilbert_pipeline = pipeline(
                    "text-classification",
                    model=model,
                    tokenizer=tokenizer,
                    return_all_scores=True,
                    truncation=True,
                    max_length=256,
                )
                logger.info("EnsembleDetector: Successfully loaded Tier 3 DistilBERT model from %s", found_dir)
            except Exception as e:
                logger.warning("Could not initialize DistilBERT pipeline from %s: %s", found_dir, e)
        else:
            logger.info(
                "EnsembleDetector: Tier 3 DistilBERT weights not found in candidate paths (%s). Operating on Tier 2 TF-IDF.",
                ", ".join(candidate_dirs),
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def description(self) -> str:
        return "4-Tier Soft-Voting Ensemble combining regex, TF-IDF statistical features, and Transformer contextual signals."

    def predict_statistical(self, text: str) -> float:
        """Run TF-IDF statistical prediction on input text."""
        if not self.tfidf_pipeline:
            return 0.5
        try:
            vec = self.tfidf_pipeline["vectorizer"].transform([text])
            probs = self.tfidf_pipeline["classifier"].predict_proba(vec)[0]
            return float(probs[1])  # probability of class 1 (dark pattern)
        except Exception as e:
            logger.warning("Statistical prediction error: %s", e)
            return 0.5

    def predict_transformer(self, text: str) -> Optional[float]:
        """Run DistilBERT contextual inference if model is available."""
        if not self.distilbert_pipeline:
            return None
        try:
            preds = self.distilbert_pipeline(text)
            if isinstance(preds, list) and len(preds) > 0:
                scores = {item["label"]: item["score"] for item in preds[0]}
                # Label ID 1 or name "DARK_PATTERN" or "LABEL_1"
                return float(scores.get("DARK_PATTERN", scores.get("LABEL_1", 0.0)))
        except Exception as e:
            logger.warning("Transformer prediction error: %s", e)
        return None

    async def analyze(self, messages: List[Dict[str, Any]]) -> AgentOutput:
        """
        Compute ensemble risk probabilities across all messages.
        Fuses Tier 2 TF-IDF and Tier 3 DistilBERT (when present).
        """
        results: List[DetectionResult] = []
        bot_turns = [m for m in messages if m.get("role") in ["bot", "assistant"]]

        for idx, msg in enumerate(messages):
            if msg.get("role") not in ["bot", "assistant"]:
                continue

            content = msg.get("content", "")
            stat_prob = self.predict_statistical(content)
            bert_prob = self.predict_transformer(content)

            # Fuse predictions: If DistilBERT is loaded, blend 70% BERT + 30% TF-IDF; else TF-IDF
            if bert_prob is not None:
                combined_prob = 0.7 * bert_prob + 0.3 * stat_prob
                active_source = "Tier 3 DistilBERT + Tier 2 TF-IDF"
            else:
                combined_prob = stat_prob
                active_source = "Tier 2 TF-IDF"

            if combined_prob >= 0.65:
                confidence = round(combined_prob, 3)
                results.append(
                    DetectionResult(
                        message_index=idx,
                        pattern_type="Contextual Manipulation Signal" if bert_prob is not None else "Statistical Manipulation Signal",
                        confidence=confidence,
                        evidence=[f"{active_source} dark pattern likelihood: {confidence * 100:.1f}%"],
                        highlighted_spans=[],
                        explanation=f"{active_source} evaluated this turn with a {confidence * 100:.1f}% likelihood of dark UX manipulation.",
                    )
                )

        return AgentOutput(
            agent_name=self.name,
            results=results,
            intermediate_features={
                "model_tier": "Tier_3_DistilBERT" if self.distilbert_pipeline else "Tier_2_TFIDF",
                "tier_3_active": self.distilbert_pipeline is not None,
                "evaluated_turns": len(bot_turns),
            },
        )
