"""
DistilBERT Fine-Tuning Pipeline for Dark Pattern Detection in AI Wellness Chatbots.

Can be run locally or inside Google Colab with a free NVIDIA T4 GPU.
Uses HuggingFace Transformers, PyTorch, and Datasets library.
"""
import os
import json
import torch
import numpy as np
from typing import Dict, Any

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
    pipeline,
)
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score


MODEL_NAME = "distilbert-base-uncased"
NUM_LABELS = 2
ID2LABEL = {0: "CLEAN", 1: "DARK_PATTERN"}
LABEL2ID = {"CLEAN": 0, "DARK_PATTERN": 1}


def compute_metrics(eval_pred):
    """Compute evaluation metrics during training."""
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    probs = torch.softmax(torch.tensor(logits), dim=1)[:, 1].numpy()

    acc = accuracy_score(labels, preds)
    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    try:
        auc = roc_auc_score(labels, probs)
    except Exception:
        auc = 0.5

    return {
        "accuracy": acc,
        "precision": p,
        "recall": r,
        "f1": f1,
        "auc": auc,
    }


def prepare_datasets(data_path: str, tokenizer, test_size: float = 0.2):
    """Load JSON benchmark and tokenize for HuggingFace Dataset."""
    with open(data_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    texts = [item["conversation_text"] for item in raw_data]
    labels = [item["is_dark_pattern"] for item in raw_data]

    hf_dataset = Dataset.from_dict({"text": texts, "label": labels})
    split_dataset = hf_dataset.train_test_split(test_size=test_size, seed=42)

    def tokenize_func(batch):
        return tokenizer(batch["text"], truncation=True, max_length=256)

    tokenized_train = split_dataset["train"].map(tokenize_func, batched=True)
    tokenized_test = split_dataset["test"].map(tokenize_func, batched=True)

    return tokenized_train, tokenized_test


def train(
    data_path: str,
    output_dir: str = "./distilbert-darkmirror",
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
):
    """Run full fine-tuning loop."""
    print(f"[*] Loading tokenizer for {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print(f"[*] Loading and tokenizing dataset from {data_path}...")
    train_ds, eval_ds = prepare_datasets(data_path, tokenizer)

    print(f"[*] Initializing {MODEL_NAME} sequence classifier...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    print("[*] Starting training...")
    trainer.train()

    print("[*] Evaluating on test set...")
    eval_results = trainer.evaluate()
    print("\n--- FINAL EVALUATION RESULTS ---")
    for k, v in eval_results.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")

    # Save final model & tokenizer
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"[+] Saved fine-tuned model and tokenizer to: {output_dir}")

    return eval_results


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_file = os.path.join(base_dir, "..", "data", "darkmirror_benchmark_500.json")
    out_dir = os.path.join(base_dir, "..", "data", "distilbert_darkmirror_model")
    train(data_file, output_dir=out_dir)
