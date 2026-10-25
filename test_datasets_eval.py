import pytest
from app.services.evaluation_service import EvaluationService


def test_metrics_computation():
    service = EvaluationService()
    predictions = [1, 1, 0, 0, 1, 0]
    labels = [1, 0, 0, 0, 1, 1]

    metrics = service.compute_metrics(predictions, labels)
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0


def test_confusion_matrix_computation():
    service = EvaluationService()
    predictions = [1, 0, 1, 0]
    labels = [1, 0, 0, 1]

    cm = service.compute_confusion_matrix(predictions, labels)
    assert len(cm) == 2
    assert len(cm[0]) == 2
    # TN=1, FP=1, FN=1, TP=1
    assert cm == [[1, 1], [1, 1]]


def test_roc_and_comparison():
    service = EvaluationService()
    roc = service.compute_roc([0.9, 0.2], [1, 0])
    assert "fpr" in roc
    assert "tpr" in roc
    assert "auc" in roc

    metrics = {"accuracy": 0.92, "precision": 0.89, "recall": 0.94, "f1": 0.91}
    comp = service.compare_approaches(metrics)
    assert "single_classifier" in comp
    assert "multi_agent" in comp
    assert comp["multi_agent"]["accuracy"] == 0.92
