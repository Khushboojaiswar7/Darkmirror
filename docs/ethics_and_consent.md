# DarkMirror – Research Ethics, Data Provenance & Informed Consent Statement

## 1. Ethical Framework & Data Provenance
The DarkMirror project investigates conversational manipulation and deceptive UX patterns in AI wellness companions. Our research adheres to the ACM Code of Ethics, IEEE Ethically Aligned Design, and the Belmont Report guidelines.

### Core Ethical Commitments:
1. **Defensive AI Safety Focus:** DarkMirror is designed strictly for auditing, defensiveness, and harm reduction—identifying patterns that engineer artificial retention and parasocial dependency in mental health and wellness applications.
2. **Synthetic Data Provenance (No Real-User Scraped Data):** 
   - All benchmark datasets (~500 multi-turn dialogues) are **entirely synthetically generated** via structured LLM API calls and manually validated.
   - **No live user interactions, scraped private chat logs, or commercial platform user data (e.g., Wysa, Replika, Woebot)** were captured or processed.
   - Zero Personally Identifiable Information (PII) or protected health information (PHI) is present in the corpus.
3. **Annotator Safety & Well-Being:**
   - Reviewing manipulative or guilt-tripping language can induce cognitive fatigue.
   - Annotation sessions were strictly capped at 45-minute intervals with mandatory rest periods to protect annotator psychological well-being.
4. **Institutional Review & Scope:**
   - Because data generation is purely synthetic and human participation was limited to a voluntary, anonymous software usability evaluation ($N=15$), the study meets standard institutional exemption criteria for human subjects research.
   - Investigators confirmed compliance with institutional ethics protocols prior to administering the usability pilot.

---

## 2. Participant Informed Consent Form (Pilot Usability Study)

**Study Title:** Pilot Evaluation of Explainability and Usability in Conversational Dark Pattern Auditing ($N=15$)  
**Principal Investigator:** DarkMirror Research Team  

### Purpose of the Study:
You are invited to participate in a pilot research study evaluating an interactive software system designed to audit conversational AI for deceptive dark UX patterns (*Excessive Flattery*, *Conversational Padding*, and *Emotional Guilt-Tripping*).

### Procedures:
- You will interact with the DarkMirror web platform to inspect synthetic audit scenarios.
- You will inspect token-level LIME/SHAP attributions and multi-tier detection outputs.
- You will complete a 10-question System Usability Scale (SUS) questionnaire and provide qualitative feedback.
- Total time commitment: approximately 20–30 minutes.

### Risks and Benefits:
- **Risks:** Minimal. Transcripts contain simulated deceptive conversational tactics. You may pause, skip any task, or end the session at any time.
- **Benefits:** You will gain hands-on experience with state-of-the-art Explainable AI (XAI) auditing tools for conversational safety.

### Confidentiality & Anonymity:
All survey responses and metric logs are strictly anonymized and referenced via non-identifying participant codes (`P01`–`P15`). No telemetry, video recordings, or personal data will be collected or shared.

### Voluntary Participation:
Participation is entirely voluntary. You may withdraw at any moment without penalty.

---

## 3. Contact & Inquiries
For questions regarding participant rights, ethics, or data provenance, contact the research maintainers via the DarkMirror repository.
