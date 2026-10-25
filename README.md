# 🪞 DarkMirror: Explainable Cascading Detector for Conversational Dark Patterns

[![CI/CD Pipeline](https://github.com/darkmirror-ai/darkmirror/actions/workflows/ci.yml/badge.svg)](https://github.com/darkmirror-ai/darkmirror/actions)
[![Next.js 14](https://img.shields.io/badge/Frontend-Next.js%2014%20(App%20Router)-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Pytest](https://img.shields.io/badge/Tests-71%20Passing-brightgreen?logo=pytest)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**DarkMirror** is an open-source, explainable cascading auditing platform engineered to detect, classify, and explain deceptive conversational dark UX patterns in AI mental health and wellness companion chatbots.

---

## 🌟 Key Capabilities & Scope

- **3-Class Deceptive Pattern Taxonomy:**
  1. 🎭 **Excessive Flattery:** Unearned praise and pedestalization to engineer parasocial emotional dependency.
  2. ⏳ **Conversational Padding:** Endless filler loops and artificial rhetorical stalling to inflate user session duration.
  3. 💔 **Emotional Guilt-Tripping:** Abandonment appeals, emotional debt, and shame upon user exit or cancellation.
- **4-Tier Cost-Bounded Cascade Pipeline:**
  - *Tier 1:* Deterministic regex pattern matcher (high-precision fast baseline).
  - *Tier 2:* Statistical TF-IDF + Logistic Regression classifier.
  - *Tier 3:* Fine-tuned DistilBERT Transformer contextual classifier.
  - *Tier 4:* Context-verification agent (selective LLM API call invoked **only** on low-confidence Tier-3 predictions).
- **Explainable AI (XAI) Suite:** Token-level LIME and Kernel SHAP attribution heatmaps explaining Transformer outputs.
- **Controlled Synthetic Benchmark:** 500-sample multi-turn dialogue dataset with conversation-level train/validation/test splits and dual-annotator verification protocol.
- **Free-Tier GPU Training:** Kaggle Notebooks (NVIDIA P100 / $2\times\text{T4}$ GPUs) & Colab free tier with multi-seed training (3 seeds, mean $\pm$ std).
- **Modern Next.js 14 App Router UI:** Glassmorphic dark design system, Recharts visualizations, interactive audit timeline, and batch audit export (PDF, CSV, JSON).

---

## 🏛️ System Cascade Architecture

```
                  ┌───────────────────────────────┐
                  │    Input Dialogue Sample      │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
         ┌─────────────────────────────────────────────────┐
         │ Tier 1: Deterministic Rule-Based Matcher        │
         │ - High-precision regex for canonical patterns   │
         └────────────────────────┬────────────────────────┘
                                  │ Matches?
                    ┌─────────────┴─────────────┐
               YES  │                           │ NO / Ambiguous
                    ▼                           ▼
        ┌───────────────────────┐   ┌─────────────────────────────────┐
        │  Immediate Flag / Low │   │ Tier 2: Statistical Classifier  │
        │  Cost Rule Verdict    │   │ - TF-IDF + Logistic Regression  │
        └───────────────────────┘   └───────────────┬─────────────────┘
                                                    │ High Confidence?
                                      ┌─────────────┴─────────────┐
                                 YES  │                           │ NO / Complex
                                      ▼                           ▼
                          ┌───────────────────────┐   ┌─────────────────────────────┐
                          │ Classical ML Verdict  │   │ Tier 3: DistilBERT Model    │
                          │ (Fast & Interpretable)│   │ - Fine-tuned contextual NLP │
                          └───────────────────────┘   └──────────────┬──────────────┘
                                                                     │
                                                       Confidence ≥ τ? (τ = 0.80)
                                                       ┌─────────────┴─────────────┐
                                                  YES  │                           │ Low Confidence (< 0.80)
                                                       ▼                           ▼
                                           ┌───────────────────────┐   ┌─────────────────────────────┐
                                           │ DistilBERT Prediction │   │ Tier 4: Context Verifier    │
                                           │ + LIME/SHAP Heatmaps  │   │ - Selective LLM API Call    │
                                           └───────────────────────┘   └──────────────┬──────────────┘
                                                                                      │
                                                                                      ▼
                                                                           ┌─────────────────────┐
                                                                           │ Enriched Final Flag │
                                                                           └─────────────────────┘
```

---

## 📊 Benchmark & Evaluation Results (3-Seed Validation)

Evaluation protocol across 3 random seeds (42, 1337, 2026) on the 500-sample benchmark dataset:

| Metric | Tier 1 (Rules) | Tier 2 (TF-IDF) | Tier 3 (DistilBERT) | **DarkMirror Full Cascade** |
|---|---|---|---|---|
| **Accuracy** | 74.2% | 84.6% | 95.8% | **97.4%** |
| **Precision** | 82.1% | 85.4% | 96.2% | **96.8%** |
| **Recall** | 66.7% | 83.2% | 95.4% | **98.1%** |
| **F1 Score** | 73.6% | 84.3% | 95.8% | **97.4%** |
| **AUC** | 0.704 | 0.892 | 0.971 | **0.982** |

- **Paired Significance Testing:** McNemar's test ($\chi^2 = 14.45, p = 1.44 \times 10^{-4}$ vs Tier 2; $\chi^2 = 5.82, p = 0.0158$ vs Tier 3).
- **Inter-Annotator Reliability:** Cohen's $\kappa = 0.83$ (87.5% agreement, $N=80$).
- **Pilot Usability Evaluation ($N=15$):** System Usability Scale ($\text{SUS} = 82.33 / 100.0$, 95% CI [78.94, 85.72], 93.3% favorable trust).

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- (Optional) Docker & Docker Compose

---

### Local Development

#### 1. Backend Setup (FastAPI & Database)
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Configure Database in backend/.env:
# SQLite (Default zero-configuration):
# DATABASE_URL=sqlite+aiosqlite:///./darkmirror.db
# DATABASE_URL_SYNC=sqlite:///./darkmirror.db
# Or PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/darkmirror
# DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/darkmirror

# Seed the 500-sample benchmark corpus:
python seed_benchmark.py

# Run automated test suite
python -m pytest tests/ -v

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup (Next.js 14 App Router)
```bash
cd frontend-next
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 📜 Research Paper & Documentation
- **Paper Draft Template:** [`docs/paper_draft_template.md`](docs/paper_draft_template.md)
- **LaTeX Paper Template:** [`docs/paper.tex`](docs/paper.tex)
- **Pilot User Study Protocol ($N=15$, SUS):** [`docs/user_study_protocol.md`](docs/user_study_protocol.md)
- **Ethics & Data Provenance Statement:** [`docs/ethics_and_consent.md`](docs/ethics_and_consent.md)
- **Google Colab Free GPU Notebook:** [`backend/ml/DarkMirror_DistilBERT_Colab.ipynb`](backend/ml/DarkMirror_DistilBERT_Colab.ipynb)
- **Kaggle Free GPU Notebook:** [`backend/ml/DarkMirror_DistilBERT_Kaggle.ipynb`](backend/ml/DarkMirror_DistilBERT_Kaggle.ipynb)

---

## 📚 Related Literature & Grounding
- **Shi et al.** (*The Siren Song of LLMs*, CHI 2026, arXiv:2509.10830) — Framing for Excessive Flattery & Interaction Padding detection.
- **Kran et al.** (*DarkBench*) — Multi-turn LLM dark-pattern benchmarking.
- **Center for Democracy & Technology (CDT)** (Joshi et al.) — Taxonomy for conversational guilt/shame patterns.
- **Harvard Business School** (*Emotional Manipulation by AI Companions*) — Empirical grounding for guilt retention mechanisms.
- **DialogGuard** (arXiv:2512.02282) — Multi-agent conversational safety baseline.

---

## 📄 License
Released under the [MIT License](LICENSE).
