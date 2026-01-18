# 🧠 GenAI Development Concepts Learned Building Nare

This document captures the GenAI development patterns and concepts we learned while building Nare — an AI coaching app for Product Managers. These lessons apply to any production GenAI application.

**Starting point:** 52% accuracy, messy UI, basic prompt  
**Ending point:** 89% accuracy, polished UX, enterprise-ready patterns

---

## Table of Contents

1. [Prompt Engineering](#1-prompt-engineering)
2. [RAG (Retrieval-Augmented Generation)](#2-rag-retrieval-augmented-generation)
3. [Evaluation & Testing](#3-evaluation--testing)
4. [Streaming & UX](#4-streaming--ux)
5. [Multi-Turn Conversation](#5-multi-turn-conversation)
6. [Token Management & Cost Control](#6-token-management--cost-control)
7. [Model Comparison & Fallbacks](#7-model-comparison--fallbacks)
8. [Safety & Privacy](#8-safety--privacy)
9. [Observability & Logging](#9-observability--logging)
10. [Debugging LLM Applications](#10-debugging-llm-applications)
11. [UX Patterns for AI Products](#11-ux-patterns-for-ai-products)
12. [Working with AI as a Collaborator](#12-working-with-ai-as-a-collaborator)

---

## 1. Prompt Engineering

The prompt is your most important code. Treat it that way.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **System prompts** | Define persona, rules, and output format upfront | "You are Nare, the Narrative Reframer — a coaching assistant for Product Managers..." |
| **Output formatting** | Specify exact structure | "## Primary Saboteur\n\n[Emoji] **[Animal Name]**: \"[exact quote]\"" |
| **Guardrails** | Explicit constraints to prevent bad behavior | "Quote ONLY words that appear EXACTLY in the user's entry — never invent or paraphrase" |
| **Scope control** | Handle off-topic gracefully | "If the entry is NOT about product management work, politely explain and redirect" |
| **Negative instructions** | Tell model what NOT to do | "NEVER write 'Secondary Saboteur: None' — just omit the section entirely" |
| **Prompt versioning** | Track iterations like code | `PROMPT_VERSIONS = {"1.0": "Initial prompt", "1.1": "Added guardrails"}` |

### Key Insight

> The model kept hallucinating saboteurs that weren't in the user's text. The fix wasn't code — it was 12 words in the prompt: "quote ONLY words that appear EXACTLY in the user's entry."

**Prompt debugging is a new skill. Treat prompts like code: version them, test them, review them.**

---

## 2. RAG (Retrieval-Augmented Generation)

RAG grounds your model's responses in source material, reducing hallucinations.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Embeddings** | Convert text to vectors for semantic search | `sentence-transformers` (all-MiniLM-L6-v2) |
| **Vector database** | Store and query embeddings efficiently | ChromaDB (local, no server needed) |
| **Chunking** | Split knowledge base into retrievable pieces | 6 markdown files, one per saboteur |
| **Context injection** | Append retrieved content to prompt | "RELEVANT FRAMEWORK REFERENCE:\n\n{rag_context}" |
| **Grounding** | Model responses stay consistent with source | Saboteur descriptions match framework exactly |

### Architecture

```
User Query
    ↓
[Embedding Model] → Vector
    ↓
[ChromaDB] → Top 3 matching documents
    ↓
[Prompt] = System + RAG Context + User Input
    ↓
[LLM] → Grounded Response
```

### Key Insight

> I assumed RAG required complex infrastructure. Turns out: sentence-transformers + ChromaDB + 6 markdown files = grounded responses. **Total infrastructure cost: $0.**

---

## 3. Evaluation & Testing

You can't improve what you can't measure.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Golden dataset** | Human-labeled examples as ground truth | 37 entries with expected saboteur labels |
| **Metrics** | Quantify model performance | Precision, Recall, F1 Score |
| **Primary accuracy** | Did it get the main answer right? | 19/21 correct = 90% |
| **False positives** | Model said yes, should be no | Over-detecting patterns |
| **False negatives** | Model said no, should be yes | Missing patterns |
| **Edge cases** | Tricky examples that test boundaries | "Healthy" responses that sound like saboteurs |
| **Hard negatives** | Examples designed to trick the model | Overwhelmed but coping well (not Golden Retriever) |

### Metrics Explained

```
Precision = TP / (TP + FP)  →  "When it detects, is it right?"
Recall    = TP / (TP + FN)  →  "Does it catch everything?"
F1 Score  = 2 × (P × R) / (P + R)  →  "Balance of both"
```

### Results

| Metric | First Prompt | Final Prompt |
|--------|--------------|--------------|
| F1 Score | 52% | 89% |
| Precision | 48% | 91% |
| Recall | 56% | 88% |

### Key Insight

> Every GenAI product needs a way to know if it's actually working. Build your golden dataset early — it's how you know if changes help or hurt.

---

## 4. Streaming & UX

Perceived performance matters as much as actual performance.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Streaming responses** | Show tokens as they generate | `client.messages.stream()` |
| **Perceived latency** | Streaming makes waits feel shorter | 3s felt broken; 3s streaming felt fast |
| **Progressive rendering** | Update UI as content arrives | `st.write_stream()` |
| **Loading states** | Show progress during generation | Spinner, "Thinking..." |

### Code Pattern

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        yield text  # Render immediately
```

### Key Insight

> Users thought the app was broken when responses took 3 seconds with no feedback. Adding streaming made the exact same latency feel instant. **Perception > reality.**

---

## 5. Multi-Turn Conversation

LLMs are stateless — you must manage context yourself.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Conversation history** | Store all exchanges | `[{role: "user", content: "..."}, {role: "assistant", content: "..."}]` |
| **Context window** | Pass full history each request | Messages array grows with conversation |
| **Follow-up framing** | Help model understand continuity | "[The same PM continues the conversation]" |
| **Stateless model** | LLM has no memory between calls | You must provide all context every time |

### The Bug We Hit

User sent a follow-up, but the model thought it was a *new person* commenting on the conversation. 

**Fix:** Frame follow-ups explicitly:
```
[The same PM continues the conversation]

{user's message}

[Remember: You are coaching THIS person through their situation.]
```

### Key Insight

> The model doesn't "remember" — it only sees what you send it. Design your message array carefully.

---

## 6. Token Management & Cost Control

Transparency builds trust; limits prevent surprises.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Token counting** | Track input/output per request | `response.usage.input_tokens` |
| **Cost estimation** | Calculate before sending | `cost = (tokens / 1_000_000) * price_per_million` |
| **Estimated vs actual** | Show comparison | Table with Estimated / Actual / Difference |
| **Rate limiting** | Cap requests per time window | 10 requests per minute |
| **Cost caps** | Limit spending per session | $0.50 max per session |
| **BYOK model** | User provides their own API key | Their key, their bill, their data |

### Cost Formula (Claude Sonnet)

```python
input_cost = (input_tokens / 1_000_000) * 3.00   # $3/M input
output_cost = (output_tokens / 1_000_000) * 15.00  # $15/M output
total_cost = input_cost + output_cost
```

### Key Insight

> Show users what they're spending. Cost transparency prevents sticker shock and builds trust.

---

## 7. Model Comparison & Fallbacks

Different models for different needs.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Multiple backends** | Support more than one model | Claude API + Ollama (local) |
| **Quality vs privacy** | Cloud = better, Local = private | User chooses their tradeoff |
| **Graceful fallbacks** | Handle unavailable backends | If no API key, offer Ollama |
| **Compare mode** | Run same prompt through both | Side-by-side with voting |
| **Eval by backend** | Measure each model's quality | Claude: 89% F1, Llama: 62% F1 |

### Architecture

```
┌─────────────────────────────────────────┐
│  User Input                             │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
  [Claude API]      [Ollama Local]
   Best quality      Max privacy
   ~$0.01/query      Free
   89% F1            62% F1
```

### Key Insight

> Give users control over the quality/privacy tradeoff. Some will pay for quality; others need data to never leave their device.

---

## 8. Safety & Privacy

Design so you *can't* see user data, even if you wanted to.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **PII detection** | Warn on sensitive content | Regex for emails, phones, SSNs |
| **Input validation** | Check before sending | Length limits, content warnings |
| **Local-first storage** | Data stays on user's device | JSON files, not cloud database |
| **Data export** | Users can download everything | Export button in UI |
| **Data deletion** | Users can clear their data | Delete button in UI |
| **BYOK architecture** | You never see their API key | Key stored in session state only |

### Privacy Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  USER'S MACHINE                                             │
│                                                             │
│  ┌─────────────┐         ┌─────────────────────────────┐   │
│  │   Nare UI   │────────▶│  Claude API (their account) │   │
│  │             │         └─────────────────────────────┘   │
│  │             │                    OR                     │
│  │             │         ┌─────────────────────────────┐   │
│  │             │────────▶│  Ollama (never leaves device)│   │
│  └─────────────┘         └─────────────────────────────┘   │
│                                                             │
│  📁 Local storage: feedback, logs, preferences              │
└─────────────────────────────────────────────────────────────┘

We (app developers) never see user data. By design.
```

### Key Insight

> Privacy unlocks honesty. When users know their reflections never leave their device, they write things they'd never type into ChatGPT.

---

## 9. Observability & Logging

You need to know what happened when something goes wrong.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Request logging** | Record each API call | Timestamp, tokens, cost, latency |
| **Audit trail** | Track what happened | User input → model response |
| **Feedback collection** | Capture quality signals | 👍/👎 buttons |
| **Session stats** | Aggregate metrics | Total cost, request count |
| **Local storage** | Keep logs on user's device | `nare_logs.json` |

### What We Log

```python
{
    "timestamp": "2025-01-17T10:30:00Z",
    "context": "setback",
    "input_length": 245,
    "output_length": 512,
    "input_tokens": 1234,
    "output_tokens": 456,
    "cost": 0.0089,
    "latency": 2.3,
    "backend": "claude",
    "feedback": "positive"
}
```

### Key Insight

> Logging is for the user, not you. Store locally, let them export/delete, use it for their own insights.

---

## 10. Debugging LLM Applications

LLM bugs don't throw errors — they just give wrong answers.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Prompt bugs** | Model does unexpected things | Hallucinating saboteurs not in text |
| **Output parsing** | Extract structure from freeform | Regex to find detected patterns |
| **Regression testing** | Catch when changes break things | Run golden dataset after each change |
| **Hallucination diagnosis** | Figure out why model invents things | Missing guardrails in prompt |
| **A/B prompt testing** | Compare prompt versions | v1.0 vs v1.1 on same inputs |

### Debugging Process

```
1. Notice wrong output
2. Check: Is it a code bug or prompt bug?
3. If prompt: Add to golden dataset as test case
4. Modify prompt with guardrail
5. Run eval to verify fix
6. Check for regressions
```

### Key Insight

> The hardest bugs are in the prompt. You can't step through them with a debugger. Build evals early so you can test prompt changes systematically.

---

## 11. UX Patterns for AI Products

AI products need different UX patterns than traditional software.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Regenerate button** | Retry without starting over | "🔄 Regenerate" after response |
| **Editable examples** | Pre-fill but allow customization | Sample text user can modify |
| **Step-by-step wizard** | Guide through complex flows | Context → Describe → Model → Response |
| **Confidence display** | Show what model detected | "Primary Saboteur: 🦜 Parrot" |
| **Explain the output** | Human-readable reasoning | "This quote reveals..." |
| **Compare mode** | Let users evaluate options | Claude vs Ollama side-by-side |

### Key Insight

> AI output is probabilistic. Give users ways to retry, compare, and understand what the model did.

---

## 12. Working with AI as a Collaborator

How you work *with* the AI matters as much as what you build.

### What We Learned

| Concept | Description | Example from Nare |
|---------|-------------|-------------------|
| **Batch feedback** | Collect multiple issues, fix together | 5-6 comments in one message |
| **Context matters** | Explain the full picture | "Here's what I'm trying to achieve..." |
| **Start ugly** | Momentum beats perfection | Ship broken v1, iterate fast |
| **Throw away code** | Early features get cut | Name changed 3 times |
| **Treat it like a collaborator** | Not a command line | Design review, not commands |

### The Batching Insight

**Early approach (slow):**
```
Me: "Fix this button"
AI: [fixes button]
Me: "Change that color"
AI: [changes color]
Me: "Move this text"
AI: [moves text]
```

**Better approach (fast):**
```
Me: "Here are 5 things to fix:
1. Button is wrong
2. Color should be blue
3. Text should be higher
4. Add a loading state
5. Error message is unclear

Here's the full context of what I'm trying to achieve..."

AI: [fixes all 5 holistically]
```

### Key Insight

> The AI worked better when I treated it like a collaborator, not a command line. Batch feedback. Explain context. Just like you'd do in a design review with a human.

---

## Summary: The GenAI Development Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     UX LAYER                                │
│  Streaming · Regenerate · Compare · Wizard · Transparency   │
├─────────────────────────────────────────────────────────────┤
│                   APPLICATION LAYER                         │
│  Multi-turn · Cost Control · Rate Limiting · Logging        │
├─────────────────────────────────────────────────────────────┤
│                    QUALITY LAYER                            │
│  Golden Dataset · Evals · Prompt Versioning · RAG           │
├─────────────────────────────────────────────────────────────┤
│                    SAFETY LAYER                             │
│  PII Detection · Input Validation · Privacy Architecture    │
├─────────────────────────────────────────────────────────────┤
│                    MODEL LAYER                              │
│  Claude API · Ollama · Fallbacks · BYOK                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Final Thoughts

Building Nare taught us that GenAI development is a new discipline — not quite software engineering, not quite data science. It requires:

- **New debugging skills** — prompt bugs don't throw errors
- **New testing methods** — golden datasets and evals
- **New UX patterns** — regenerate, compare, explain
- **New collaboration models** — batch feedback, context sharing

The technology is powerful, but the craft is still emerging. These patterns worked for us. We hope they help you too.

---

*Built while pair-programming with Claude · January 2025*
