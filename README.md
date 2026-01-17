# 🎯 Nare

**The Narrative Reframer — AI coaching that helps PMs spot the stories holding them back.**

> *Nare* (pronounced "Narry" 🔊 — rhymes with Larry) = **Na**rrative **Re**framer

<p align="center">
  <img src="docs/screenshot-home.png" alt="Nare Home Screen" width="600">
</p>

Nare helps Product Managers recognize self-sabotaging mental patterns and reframe the narratives that keep them stuck. Built with a privacy-first architecture and grounded in psychological research.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Why Nare?

Every PM knows the feeling: you're stuck in a loop of self-doubt, perfectionism, or people-pleasing, and you can't see your way out. Nare acts as a **confidential thinking partner** that helps you:

- **Recognize patterns** — Name the saboteur that's running the show
- **Reframe narratives** — Hear a grounded perspective on your situation  
- **Build self-awareness** — Track which patterns show up most for you

**This is not therapy.** It's a tool for self-reflection, built by a PM who's been in those spirals too.

---

## 🐾 The Five Saboteurs

| Animal | Pattern | Core Fear |
|--------|---------|-----------|
| 🦜 **Parrot** | Inner Critic | "I'm not enough" |
| 🦚 **Peacock** | Insecure Performer | "I'm only worth what I produce" |
| 🐙 **Octopus** | Anxious Controller | "If I let go, disaster follows" |
| 🐕 **Golden Retriever** | Compulsive Pleaser | "I'll be rejected if I disappoint" |
| 🐇 **Rabbit** | Restless Escapist | "This moment is unbearable" |

The framework combines insights from **Internal Family Systems (IFS)**, **Cognitive Behavioral Therapy (CBT)**, and **Acceptance & Commitment Therapy (ACT)** — mapped to memorable animal metaphors so you can catch yourself in the moment.

---

## 🚀 Quick Start

```bash
# 1. Download and unzip from GitHub (green "Code" button → Download ZIP)
# 2. Open terminal, navigate to the folder, and run:

bash setup.sh
```

That's it! The setup script installs everything and launches the app in your browser.

### Choose Your Backend

| Option | What You Need | Privacy | Quality |
|--------|---------------|---------|---------|
| **Claude API** | Your API key ([get one here](https://console.anthropic.com/)) | Your Anthropic account | ⭐⭐⭐⭐⭐ |
| **Ollama (Local)** | Ollama installed ([ollama.ai](https://ollama.ai)) | 100% on-device | ⭐⭐⭐ |

---

## 🔒 Privacy Architecture

Your reflections are personal. Nare is designed so **we never see your data**:

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR MACHINE                                               │
│                                                             │
│  ┌─────────────┐         ┌─────────────────────────────┐   │
│  │   Nare UI   │────────▶│  Claude API (your account)  │   │
│  │             │         └─────────────────────────────┘   │
│  │             │                    OR                     │
│  │             │         ┌─────────────────────────────┐   │
│  │             │────────▶│  Ollama (never leaves device)│   │
│  └─────────────┘         └─────────────────────────────┘   │
│                                                             │
│  📁 Local storage only: feedback, logs, preferences         │
└─────────────────────────────────────────────────────────────┘
```

- **Claude API**: Your API key, your Anthropic account, your data
- **Ollama**: 100% local — nothing ever leaves your machine
- **No telemetry**: We don't collect or transmit anything

---

## 🧪 Built-In Evaluation

Nare includes a **37-entry golden dataset** and eval dashboard to measure response quality:

<p align="center">
  <img src="docs/screenshot-evals.png" alt="Eval Dashboard" width="600">
</p>

| Metric | Claude Sonnet | Llama 3.1 8B |
|--------|---------------|--------------|
| **F1 Score** | 89% | 62% |
| **Precision** | 91% | 62% |
| **Recall** | 88% | 62% |

Compare backends, run subset tests, and drill into individual results.

---

## 🏢 Enterprise GenAI Features

This project demonstrates production-ready GenAI patterns:

| Category | Features |
|----------|----------|
| **Quality** | RAG grounding, prompt versioning, golden dataset evals |
| **Safety** | PII detection, input validation, rate limiting ($0.50/session cap) |
| **Observability** | Request logging, audit trail, token/cost tracking |
| **UX** | Streaming responses, regenerate, multi-turn conversation |
| **Privacy** | BYOK model, local-first storage, data export |

---

## 📁 Project Structure

```
nare/
├── app.py              # Main Streamlit app (2,900+ lines)
├── golden_dataset.py   # 37 labeled test cases
├── eval.py             # Evaluation utilities  
├── rag.py              # RAG with sentence-transformers + ChromaDB
├── knowledge/          # Saboteur framework documentation
│   ├── parrot.md
│   ├── peacock.md
│   ├── octopus.md
│   ├── golden_retriever.md
│   ├── rabbit.md
│   └── grounded_pm.md
├── requirements.txt
└── README.md
```

---

## 🧠 Psychological Foundation

Nare's framework synthesizes evidence-based approaches:

- **[Internal Family Systems (IFS)](https://ifs-institute.com/)** — Parts work, the Self
- **[Cognitive Behavioral Therapy (CBT)](https://beckinstitute.org/)** — Cognitive distortions, reframing
- **[Acceptance & Commitment Therapy (ACT)](https://contextualscience.org/act)** — Defusion, observing self
- **[Compassion-Focused Therapy](https://www.compassionatemind.co.uk/)** — Self-compassion, inner critic

**⚠️ Disclaimer:** Nare is a self-reflection tool, not therapy. It cannot diagnose conditions or replace professional mental health support. If you're in crisis, please contact a professional or call 988 (US).

---

## 🛠️ Development

```bash
# Run tests
python -m pytest

# Check syntax
python -c "import app"

# Run evals
python eval.py
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built during a series of pair-programming sessions with Claude. The saboteur framework draws inspiration from Shirzad Chamine's *Positive Intelligence* and the IFS model developed by Dr. Richard Schwartz.

---

<p align="center">
  <i>Built by a PM, for PMs, in January 2025</i>
</p>
