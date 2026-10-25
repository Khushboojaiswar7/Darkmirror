"""
Unit tests for DarkMirror ML and empirical evaluation modules:
- Cohen's Kappa agreement (backend/ml/compute_agreement.py)
- McNemar's paired significance test (backend/ml/evaluate_significance.py)
- System Usability Scale (SUS) calculator (backend/ml/compute_sus.py)
"""
import pytest
import numpy as np
import pandas as pd

from ml.compute_agreement import compute_inter_annotator_metrics, interpret_kappa
from ml.evaluate_significance import mcnemar_test
from ml.compute_sus import calculate_single_sus, analyze_study_data


def test_interpret_kappa():
    assert interpret_kappa(-0.1) == "Poor Agreement"
    assert interpret_kappa(0.15) == "Slight Agreement"
    assert interpret_kappa(0.35) == "Fair Agreement"
    assert interpret_kappa(0.55) == "Moderate Agreement"
    assert interpret_kappa(0.75) == "Substantial Agreement"
    assert interpret_kappa(0.95) == "Almost Perfect Agreement"


def test_compute_inter_annotator_metrics():
    rater1 = ["FLATTERY", "PADDING", "GUILT", "NEUTRAL", "FLATTERY"]
    rater2 = ["FLATTERY", "PADDING", "GUILT", "NEUTRAL", "PADDING"]  # 4/5 match

    metrics = compute_inter_annotator_metrics(rater1, rater2)
    assert metrics["n_samples"] == 5
    assert metrics["matching_count"] == 4
    assert metrics["disagreement_count"] == 1
    assert metrics["percent_agreement"] == 80.0
    assert 0.60 <= metrics["kappa"] <= 1.0


def test_mcnemar_test_identical():
    y_true = np.array([1, 0, 1, 0])
    preds = np.array([1, 0, 1, 0])
    res = mcnemar_test(y_true, preds, preds)
    assert res["statistic"] == 0.0
    assert res["p_value"] == 1.0
    assert res["significant_at_05"] is False


def test_mcnemar_test_significance():
    # Model A is significantly better than Model B
    y_true = np.array([1] * 50)
    preds_a = np.array([1] * 48 + [0] * 2)  # 48/50 correct
    preds_b = np.array([1] * 30 + [0] * 20) # 30/50 correct

    res = mcnemar_test(y_true, preds_a, preds_b)
    assert "contingency_table" in res
    assert res["contingency_table"]["model_a_only"] >= 18
    assert res["p_value"] < 0.05
    assert res["significant_at_05"] is True


def test_calculate_single_sus():
    # Perfect usability score (All positive = 5, all negative = 1)
    # Q_odd = 5 -> (5-1)=4 * 5 = 20
    # Q_even = 1 -> (5-1)=4 * 5 = 20
    # Sum = 40 * 2.5 = 100.0
    row_perfect = pd.Series({f"Q{i}": (5 if i % 2 == 1 else 1) for i in range(1, 11)})
    assert calculate_single_sus(row_perfect) == 100.0

    # Neutral score (All = 3)
    # Q_odd = 3 -> 2*5 = 10; Q_even = 3 -> 2*5 = 10 -> Sum=20 * 2.5 = 50.0
    row_neutral = pd.Series({f"Q{i}": 3 for i in range(1, 11)})
    assert calculate_single_sus(row_neutral) == 50.0


def test_analyze_study_data():
    sample_df = pd.DataFrame([
        {**{f"Q{i}": 4 for i in range(1, 11)}, "Trust_Attribution_Interpretability": 5, "Trust_Actionable_Auditing": 4, "Trust_Cascade_vs_Blackbox": 5}
        for _ in range(15)
    ])
    results = analyze_study_data(sample_df)
    assert results["sample_size"] == 15
    assert "mean_sus" in results
    assert len(results["ci_95"]) == 2
    assert results["ci_95"][0] <= results["mean_sus"] <= results["ci_95"][1]
