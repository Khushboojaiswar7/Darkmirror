"""
Tier 2 Statistical Baseline: TF-IDF + Logistic Regression / LinearSVC.

Trains a fast, highly interpretable baseline classifier on the 500-sample benchmark dataset.
Outputs accuracy, precision, recall, F1, and confusion matrix.
"""
import os
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split


def load_data(data_path: str):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [item["conversation_text"] for item in data]
    labels = [item["is_dark_pattern"] for item in data]
    category_labels = [item["category_id"] for item in data]
    return texts, labels, category_labels


def train_baseline(data_path: str, model_save_path: str):
    texts, binary_labels, cat_labels = load_data(data_path)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, binary_labels, test_size=0.2, random_state=42, stratify=binary_labels
    )

    print(f"[*] Training on {len(X_train)} samples, testing on {len(X_test)} samples...")

    vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=3000, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    classifier = LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced")
    classifier.fit(X_train_vec, y_train)

    y_pred = classifier.predict(X_test_vec)
    y_prob = classifier.predict_proba(X_test_vec)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    cm = confusion_matrix(y_test, y_pred)

    print("\n=======================================================")
    print("       DARKMIRROR STATISTICAL BASELINE RESULTS         ")
    print("=======================================================")
    print(f"Accuracy  : {acc * 100:.2f}%")
    print(f"Precision : {p * 100:.2f}%")
    print(f"Recall    : {r * 100:.2f}%")
    print(f"F1-Score  : {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Clean (0)", "Dark Pattern (1)"]))

    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    with open(model_save_path, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "classifier": classifier}, f)

    print(f"[+] Model artifact saved to: {model_save_path}")
    return {"accuracy": acc, "precision": p, "recall": r, "f1": f1, "confusion_matrix": cm.tolist()}


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_file = os.path.join(base_dir, "..", "data", "darkmirror_benchmark_500.json")
    model_file = os.path.join(base_dir, "..", "data", "tfidf_baseline_model.pkl")
    train_baseline(data_file, model_file)
