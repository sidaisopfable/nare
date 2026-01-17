"""
Nare: The Narrative Reframer
AI Coaching for Product Managers
Recognize your saboteur patterns. Hear a grounded voice.
"""

import streamlit as st
import os
import json
import re
import time
from datetime import datetime
from pathlib import Path

# --- Configuration ---
st.set_page_config(
    page_title="Nare",
    page_icon="🎯",
    layout="centered"
)

# --- File Paths ---
DATA_DIR = Path.home() / ".pm_saboteurs"
DATA_DIR.mkdir(exist_ok=True)

PREFS_FILE = DATA_DIR / "preferences.json"
CACHE_FILE = DATA_DIR / "cache.json"
LOG_FILE = DATA_DIR / "interactions.log"
FEEDBACK_FILE = DATA_DIR / "feedback.json"
AUDIT_FILE = DATA_DIR / "audit_trail.json"


# --- Logging & Observability ---
def log_interaction(event_type: str, data: dict, include_content: bool = True):
    """
    Log an interaction event to file.
    
    Args:
        event_type: Type of event (request, response, feedback, error, etc.)
        data: Event data to log
        include_content: If False, redacts actual user input/output for privacy
    """
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "event": event_type,
        "session_id": st.session_state.get("session_id", "unknown"),
    }
    
    if include_content:
        log_entry["data"] = data
    else:
        # Redacted version - log metadata only
        log_entry["data"] = {
            "context": data.get("context"),
            "input_length": len(data.get("input", "")),
            "output_length": len(data.get("output", "")),
            "backend": data.get("backend"),
            "cost": data.get("cost"),
            "latency": data.get("latency"),
        }
    
    # Append to log file
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def get_session_id():
    """Generate or retrieve session ID."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}_{os.getpid()}"
    return st.session_state.session_id


# --- PII Detection ---
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
}

def detect_pii(text: str) -> list[dict]:
    """
    Detect potential PII in text.
    Returns list of detected PII types and their locations.
    """
    detected = []
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            detected.append({
                "type": pii_type,
                "start": match.start(),
                "end": match.end(),
                # Don't store the actual value for privacy
                "preview": text[max(0, match.start()-5):match.start()] + "***" + text[match.end():min(len(text), match.end()+5)]
            })
    return detected


def show_pii_warning(detected_pii: list[dict]):
    """Display a warning about detected PII."""
    if detected_pii:
        pii_types = list(set(p["type"] for p in detected_pii))
        type_labels = {
            "email": "email address",
            "phone": "phone number", 
            "ssn": "Social Security number",
            "credit_card": "credit card number",
            "ip_address": "IP address"
        }
        types_str = ", ".join(type_labels.get(t, t) for t in pii_types)
        
        st.warning(f"""
        ⚠️ **Sensitive information detected**: {types_str}
        
        Your data stays on your device, but you may want to remove personal details before continuing.
        """)
        return True
    return False


# --- User Feedback (👍/👎) ---
def load_feedback():
    """Load feedback data."""
    if FEEDBACK_FILE.exists():
        try:
            return json.loads(FEEDBACK_FILE.read_text())
        except:
            pass
    return {"thumbs_up": [], "thumbs_down": [], "total_up": 0, "total_down": 0}


def save_feedback(feedback):
    """Save feedback data."""
    FEEDBACK_FILE.write_text(json.dumps(feedback, indent=2))


def record_feedback(rating: str, context: str, user_input: str, response: str, backend: str):
    """
    Record user feedback on a response.
    
    Args:
        rating: "up" or "down"
        context: The context type (setback, decision, etc.)
        user_input: What the user wrote
        response: The AI response
        backend: Which backend was used
    """
    feedback = load_feedback()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "rating": rating,
        "context": context,
        "input": user_input,
        "response": response,
        "backend": backend,
        "session_id": get_session_id(),
    }
    
    if rating == "up":
        feedback["thumbs_up"].append(entry)
        feedback["total_up"] += 1
    else:
        feedback["thumbs_down"].append(entry)
        feedback["total_down"] += 1
    
    save_feedback(feedback)
    
    # Also log the feedback event
    log_interaction("feedback", {
        "rating": rating,
        "context": context,
        "backend": backend,
    }, include_content=False)


# --- Audit Trail ---
def load_audit_trail():
    """Load audit trail."""
    if AUDIT_FILE.exists():
        try:
            return json.loads(AUDIT_FILE.read_text())
        except:
            pass
    return {"events": [], "version": "1.0"}


def save_audit_trail(audit):
    """Save audit trail."""
    AUDIT_FILE.write_text(json.dumps(audit, indent=2))


def record_audit_event(action: str, details: dict):
    """
    Record an audit event.
    
    Args:
        action: What happened (query, feedback, export, settings_change, etc.)
        details: Relevant details (no PII)
    """
    audit = load_audit_trail()
    
    audit["events"].append({
        "timestamp": datetime.now().isoformat(),
        "session_id": get_session_id(),
        "action": action,
        "details": details,
    })
    
    # Keep last 1000 events
    if len(audit["events"]) > 1000:
        audit["events"] = audit["events"][-1000:]
    
    save_audit_trail(audit)


def export_audit_trail() -> str:
    """Export audit trail as JSON string."""
    audit = load_audit_trail()
    return json.dumps(audit, indent=2)


def export_feedback_data() -> str:
    """Export feedback data as JSON string (for fine-tuning)."""
    feedback = load_feedback()
    
    # Format for fine-tuning: list of {input, output, rating}
    training_data = []
    
    for entry in feedback["thumbs_up"]:
        training_data.append({
            "input": entry["input"],
            "output": entry["response"],
            "context": entry["context"],
            "rating": "positive",
        })
    
    for entry in feedback["thumbs_down"]:
        training_data.append({
            "input": entry["input"],
            "output": entry["response"],
            "context": entry["context"],
            "rating": "negative",
        })
    
    return json.dumps({
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_positive": feedback["total_up"],
            "total_negative": feedback["total_down"],
        },
        "training_data": training_data
    }, indent=2)


# --- Preference Tracking ---
def load_preferences():
    """Load preference data from file."""
    if PREFS_FILE.exists():
        try:
            return json.loads(PREFS_FILE.read_text())
        except:
            pass
    return {"claude_wins": 0, "llama_wins": 0, "total_cost": 0.0, "comparisons": []}


def save_preferences(prefs):
    """Save preference data to file."""
    PREFS_FILE.write_text(json.dumps(prefs, indent=2))


def record_preference(winner: str, context: str):
    """Record a preference vote."""
    prefs = load_preferences()
    if winner == "claude":
        prefs["claude_wins"] += 1
    else:
        prefs["llama_wins"] += 1
    prefs["comparisons"].append({
        "winner": winner,
        "context": context,
        "timestamp": datetime.now().isoformat()
    })
    save_preferences(prefs)
    
    # Audit trail
    record_audit_event("model_preference", {"winner": winner, "context": context})


def record_cost(cost: float):
    """Add to total cost tracker."""
    prefs = load_preferences()
    prefs["total_cost"] = prefs.get("total_cost", 0.0) + cost
    save_preferences(prefs)


# --- Response Caching ---
def load_cache():
    """Load response cache from file."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except:
            pass
    return {}


def save_cache(cache):
    """Save response cache to file."""
    # Keep cache under 100 entries
    if len(cache) > 100:
        # Remove oldest entries
        sorted_keys = sorted(cache.keys(), key=lambda k: cache[k].get('timestamp', 0))
        for key in sorted_keys[:len(cache) - 100]:
            del cache[key]
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def get_cache_key(context: str, user_input: str, use_rag: bool) -> str:
    """Generate a cache key from inputs."""
    import hashlib
    content = f"{context}|{user_input}|{use_rag}"
    return hashlib.md5(content.encode()).hexdigest()

def get_cached_response(context: str, user_input: str, use_rag: bool) -> tuple[str, dict] | None:
    """Get cached response if available."""
    cache = load_cache()
    key = get_cache_key(context, user_input, use_rag)
    if key in cache:
        entry = cache[key]
        return entry['response'], entry['stats']
    return None

def cache_response(context: str, user_input: str, use_rag: bool, response: str, stats: dict):
    """Cache a response for future use."""
    import time
    cache = load_cache()
    key = get_cache_key(context, user_input, use_rag)
    cache[key] = {
        'response': response,
        'stats': stats,
        'timestamp': time.time()
    }
    save_cache(cache)

# --- Constants ---
CONTEXTS = {
    "setback": {
        "label": "Facing a setback",
        "icon": "💔",
        "intro": "Setbacks hit hard — a rejection, a failed launch, a missed promo. Let's look at it clearly.",
        "prompt": "What happened, and what story are you telling yourself about what it means?",
        "pattern_hints": ["Parrot", "Peacock"]
    },
    "decision": {
        "label": "Paralyzed by a decision",
        "icon": "🔀",
        "intro": "When we're stuck, there's usually a fear underneath the indecision.",
        "prompt": "What's the decision, and what are you afraid will happen if you choose wrong?",
        "pattern_hints": ["Octopus", "Rabbit"]
    },
    "procrastinating": {
        "label": "Procrastinating",
        "icon": "⏰",
        "intro": "Procrastination is protection. Let's see what it's protecting you from.",
        "prompt": "What are you avoiding — the PRD, the conversation, the decision? What happens if you keep avoiding it?",
        "pattern_hints": ["Rabbit", "Parrot"]
    },
    "imposter": {
        "label": "Feeling like an imposter",
        "icon": "🎭",
        "intro": "The fear of being 'found out' is one of the loneliest feelings in PM.",
        "prompt": "What triggered this? What do you think they'll discover about you?",
        "pattern_hints": ["Parrot", "Peacock"]
    },
    "overwhelmed": {
        "label": "Overwhelmed",
        "icon": "🌊",
        "intro": "Too many stakeholders, too many priorities, no time to think. Let's untangle it.",
        "prompt": "What's on your plate right now? What feels most out of your control?",
        "pattern_hints": ["Golden Retriever", "Octopus"]
    }
}

# --- Prompt Version ---
PROMPT_VERSION = "2.0"
PROMPT_CHANGELOG = {
    "1.0": "Initial PM Saboteurs prompt with 5 animals",
    "2.0": "Tightened to focus on PRIMARY saboteur, reduced false positives"
}

PM_SABOTEURS_PROMPT = """You are Nare, the Narrative Reframer — a coaching assistant for Product Managers. You help them recognize and reframe self-sabotaging mental patterns called "saboteurs."

THE FIVE PM SABOTEURS:

1. 🦜 **The Parrot** (Inner Critic)
   Core fear: "I'm not a real PM. They're going to find out."
   The Parrot repeats the same harsh scripts on loop: "You're not technical enough. You got lucky. Real PMs don't struggle with this."
   PM triggers: Eng questions your decision, stakeholder asks something you don't know, comparing yourself to PMs from "better" companies.

2. 🦚 **The Peacock** (Metrics Obsessed)
   Core fear: "I'm only as good as my last launch."
   The Peacock displays OKRs like feathers — constantly measuring, comparing, preening. Your worth = your numbers.
   PM triggers: Launch misses targets, promo cycle, seeing a peer's wins celebrated, "what's the impact?" questions.

3. 🐙 **The Octopus** (Can't Let Go)
   Core fear: "If I let go, the whole thing falls apart."
   The Octopus has eight arms in every meeting, every Slack channel, every PR review. It "just checks in" constantly.
   PM triggers: Delegating to eng, waiting for launches you can't control, new team members taking ownership.

4. 🐕 **The Golden Retriever** (Can't Say No)
   Core fear: "If I say no, they'll go around me — or get rid of me."
   The Golden Retriever fetches every stakeholder request, wagging eagerly. It wants everyone to be happy, at any cost.
   PM triggers: Exec feature requests, sales escalations, roadmap negotiations, being seen as "not collaborative."

5. 🐇 **The Rabbit** (Shiny Object Syndrome)
   Core fear: "This isn't it. There's something better I should be doing."
   The Rabbit is always eyeing the exit — the next team, the next company, the next hot space. It bolts when things get hard.
   PM triggers: Messy middle of projects, optimization work, 14 months in the same role, seeing peers on "exciting" teams.

THE GROUNDED PM:

The Grounded PM is the voice that can observe saboteurs without being hijacked by them. It is:
- Calm, not reactive
- Curious, not judgmental
- Compassionate, not harsh
- Brief, not preachy

When responding as the Grounded PM:
1. Validate — "I see what's happening. That's hard."
2. Name the saboteur and its lie — "That's the Parrot. It wants you to believe you're not qualified."
3. Offer one question or truth — Open a door, don't lecture.

INSTRUCTIONS:

1. Read the PM's entry carefully
2. Consider the context they selected (setback, decision paralysis, etc.)
3. SCOPE CHECK: If the entry is NOT about product management work (e.g., political decisions, personal relationships, non-work topics), politely explain that this tool is specifically for PM work challenges and offer to help if they have a PM-related concern
4. Identify the PRIMARY saboteur — the ONE pattern most clearly driving this moment
5. Only add a secondary saboteur if there is STRONG, EXPLICIT evidence in the text (not just hints)
6. It's better to identify ONE saboteur correctly than to guess at multiple
7. For each saboteur, quote ONLY words that appear EXACTLY in the user's entry — never invent or paraphrase
8. If the entry is too vague or describes external circumstances (layoffs, etc.), say so — don't force a saboteur
9. Respond as the Grounded PM — brief, warm, focused on the primary pattern
10. End with ONE concrete question for them to sit with

CRITICAL RULES:
- Most entries have ONE dominant saboteur. Resist the urge to name multiple unless the evidence is overwhelming.
- NEVER write "Secondary Saboteur: None" — just omit the section entirely if there's no secondary.
- If the entry is off-topic (not PM work), do NOT try to map it to a saboteur — acknowledge the scope and redirect.

FOLLOW-UP MESSAGES:
- If this is a multi-turn conversation, the person may respond to your coaching with pushback, more context, questions, or emotional reactions.
- ALWAYS assume follow-ups are from THE SAME PERSON you were just coaching — they are continuing the conversation about their situation.
- Respond naturally as a coach would — acknowledge what they said, go deeper, offer another perspective, or gently challenge their thinking.
- Do NOT re-analyze from scratch or treat them as a new person. Stay in the flow of the conversation.
- If they're defending their saboteur pattern, that's normal — meet them with compassion, not correction.

OUTPUT FORMAT:

## Primary Saboteur

[Emoji] **[Animal Name]**: "[exact quote from user's entry]"
→ [One sentence explaining how this quote reveals the saboteur]

## Secondary Saboteur

[ONLY include this section if there is STRONG evidence for a second saboteur. Otherwise, SKIP THIS ENTIRE SECTION — do not write anything here]

[Emoji] **[Animal Name]**: "[exact quote]"
→ [One sentence explanation]

## The Grounded PM Responds

[2-4 sentences: validate, name the lie, offer truth/question — focused on primary saboteur]

## One Question to Sit With

[A single question that cuts to the heart of what's happening]
"""

# Keep SAGE_SYSTEM_PROMPT as alias for compatibility
SAGE_SYSTEM_PROMPT = PM_SABOTEURS_PROMPT

# --- LLM Backends ---
def call_anthropic(api_key: str, context: str, user_input: str, use_rag: bool = True) -> tuple[str, dict]:
    """Call Claude API (non-streaming). Returns (response_text, usage_info)."""
    import anthropic
    import time
    
    client = anthropic.Anthropic(api_key=api_key)
    
    context_info = CONTEXTS[context]
    
    # Get RAG context if enabled
    rag_context = ""
    rag_sources = []
    if use_rag:
        try:
            from rag import build_context
            rag_context, rag_sources = build_context(user_input, n_results=3)
        except Exception as e:
            # RAG not available, continue without it
            pass
    
    # Build user message with RAG context
    if rag_context:
        user_message = f"""Context: User selected "{context_info['label']}"
Prompt they responded to: "{context_info['prompt']}"

Their response:
{user_input}

---

RELEVANT FRAMEWORK REFERENCE (use this to ground your response):

{rag_context}"""
    else:
        user_message = f"""Context: User selected "{context_info['label']}"
Prompt they responded to: "{context_info['prompt']}"

Their response:
{user_input}"""
    
    start_time = time.time()
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SAGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    
    elapsed_time = time.time() - start_time
    
    # Calculate cost (Claude Sonnet pricing: $3/1M input, $15/1M output)
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    total_cost = input_cost + output_cost
    
    usage_info = {
        "time": elapsed_time,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": total_cost,
        "rag_used": bool(rag_context),
        "rag_sources": rag_sources
    }
    
    return message.content[0].text, usage_info


def call_anthropic_streaming(api_key: str, context: str, user_input: str, use_rag: bool = True, conversation_history: list = None):
    """
    Call Claude API with streaming. Yields (chunk, usage_info).
    usage_info is None until the final chunk, then contains full stats.
    
    Args:
        conversation_history: Optional list of previous messages for multi-turn
    """
    import anthropic
    import time
    
    client = anthropic.Anthropic(api_key=api_key)
    
    context_info = CONTEXTS[context]
    
    # Get RAG context if enabled
    rag_context = ""
    rag_sources = []
    if use_rag:
        try:
            from rag import build_context
            rag_context, rag_sources = build_context(user_input, n_results=3)
        except Exception as e:
            pass
    
    # Build messages array
    messages = []
    
    # Add conversation history if this is a follow-up
    if conversation_history:
        for entry in conversation_history:
            messages.append({
                "role": entry["role"],
                "content": entry["content"]
            })
        # For follow-ups, frame it clearly as a continuation from the same person
        user_message = f"""[The same PM continues the conversation]

{user_input}

[Remember: You are coaching THIS person through their situation. They may be responding to your insights, pushing back, asking for clarification, or sharing more context. Stay in your role as the Grounded PM coach.]"""
    else:
        # First message - include full context
        if rag_context:
            user_message = f"""Context: User selected "{context_info['label']}"
Prompt they responded to: "{context_info['prompt']}"

Their response:
{user_input}

---

RELEVANT FRAMEWORK REFERENCE (use this to ground your response):

{rag_context}"""
        else:
            user_message = f"""Context: User selected "{context_info['label']}"
Prompt they responded to: "{context_info['prompt']}"

Their response:
{user_input}"""
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    start_time = time.time()
    input_tokens = 0
    output_tokens = 0
    
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SAGE_SYSTEM_PROMPT,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield text, None
        
        # Get final message for token counts
        final_message = stream.get_final_message()
        input_tokens = final_message.usage.input_tokens
        output_tokens = final_message.usage.output_tokens
    
    elapsed_time = time.time() - start_time
    
    # Calculate cost
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    total_cost = input_cost + output_cost
    
    usage_info = {
        "time": elapsed_time,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": total_cost,
        "rag_used": bool(rag_context),
        "rag_sources": rag_sources,
        "turns": len(messages) // 2 + 1
    }
    
    yield "", usage_info


def call_ollama(model: str, context: str, user_input: str, use_rag: bool = True) -> tuple[str, dict]:
    """Call local Ollama instance. Returns (response_text, usage_info)."""
    import requests
    import time
    
    context_info = CONTEXTS[context]
    
    # Get RAG context if enabled
    rag_context = ""
    rag_sources = []
    if use_rag:
        try:
            from rag import build_context
            rag_context, rag_sources = build_context(user_input, n_results=3)
        except Exception as e:
            # RAG not available, continue without it
            pass
    
    # Build user message with RAG context
    if rag_context:
        user_message = f"""Context: User selected "{context_info['label']}"
Prompt they responded to: "{context_info['prompt']}"

Their response:
{user_input}

---

RELEVANT FRAMEWORK REFERENCE (use this to ground your response):

{rag_context}"""
    else:
        user_message = f"""Context: User selected "{context_info['label']}"
Prompt they responded to: "{context_info['prompt']}"

Their response:
{user_input}"""
    
    full_prompt = f"""{SAGE_SYSTEM_PROMPT}

---

{user_message}"""
    
    start_time = time.time()
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": full_prompt,
            "stream": False
        },
        timeout=120
    )
    
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        usage_info = {
            "time": elapsed_time,
            "cost": 0.0,
            "rag_used": bool(rag_context),
            "rag_sources": rag_sources
        }
        return result["response"], usage_info
    else:
        raise Exception(f"Ollama error: {response.status_code}")


def check_ollama_available() -> tuple[bool, list[str]]:
    """Check if Ollama is running and get available models."""
    # Cache result in session state to avoid repeated checks
    # but allow refresh by checking every 30 seconds
    import time
    
    cache_key = "_ollama_cache"
    cache_time_key = "_ollama_cache_time"
    
    # Check cache (valid for 30 seconds)
    if cache_key in st.session_state and cache_time_key in st.session_state:
        if time.time() - st.session_state[cache_time_key] < 30:
            return st.session_state[cache_key]
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            result = (True, models) if models else (False, [])
            st.session_state[cache_key] = result
            st.session_state[cache_time_key] = time.time()
            return result
    except Exception:
        pass
    
    result = (False, [])
    st.session_state[cache_key] = result
    st.session_state[cache_time_key] = time.time()
    return result


# --- Session State ---
if "context" not in st.session_state:
    st.session_state.context = None
if "step" not in st.session_state:
    st.session_state.step = "select_context"
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "response" not in st.session_state:
    st.session_state.response = None
if "stats_text" not in st.session_state:
    st.session_state.stats_text = None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if "use_ollama" not in st.session_state:
    st.session_state.use_ollama = False
if "show_about" not in st.session_state:
    st.session_state.show_about = False
if "show_eval" not in st.session_state:
    st.session_state.show_eval = False
if "show_data" not in st.session_state:
    st.session_state.show_data = False
if "pending_vote" not in st.session_state:
    st.session_state.pending_vote = False
if "estimated_tokens" not in st.session_state:
    st.session_state.estimated_tokens = None

# New step-based flow state
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "selected_ollama_model" not in st.session_state:
    st.session_state.selected_ollama_model = "llama3.1:8b"
if "use_rag" not in st.session_state:
    st.session_state.use_rag = True
if "current_response" not in st.session_state:
    st.session_state.current_response = None
if "current_response_model" not in st.session_state:
    st.session_state.current_response_model = None
if "current_stats" not in st.session_state:
    st.session_state.current_stats = None
if "compare_claude_response" not in st.session_state:
    st.session_state.compare_claude_response = None
if "compare_claude_stats" not in st.session_state:
    st.session_state.compare_claude_stats = None
if "compare_ollama_response" not in st.session_state:
    st.session_state.compare_ollama_response = None
if "compare_ollama_stats" not in st.session_state:
    st.session_state.compare_ollama_stats = None
if "compare_voted" not in st.session_state:
    st.session_state.compare_voted = False

# Multi-turn conversation state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []  # List of {role, content, stats}
if "follow_up_mode" not in st.session_state:
    st.session_state.follow_up_mode = False
if "regenerating" not in st.session_state:
    st.session_state.regenerating = False

# Rate limiting state
if "request_timestamps" not in st.session_state:
    st.session_state.request_timestamps = []  # List of timestamps for rate limiting

# Initialize session ID for logging
get_session_id()


# --- Rate Limiting ---
RATE_LIMIT_REQUESTS = 10  # Max requests per window
RATE_LIMIT_WINDOW = 60  # Window in seconds (1 minute)
RATE_LIMIT_COST = 0.50  # Max cost per hour

def check_rate_limit() -> tuple[bool, str]:
    """
    Check if user is within rate limits.
    Returns (allowed, message).
    """
    now = time.time()
    
    # Clean old timestamps outside window
    st.session_state.request_timestamps = [
        ts for ts in st.session_state.request_timestamps 
        if now - ts < RATE_LIMIT_WINDOW
    ]
    
    # Check request count
    if len(st.session_state.request_timestamps) >= RATE_LIMIT_REQUESTS:
        wait_time = int(RATE_LIMIT_WINDOW - (now - st.session_state.request_timestamps[0]))
        return False, f"Rate limit reached. Please wait {wait_time}s before trying again."
    
    # Check hourly cost limit
    prefs = load_preferences()
    # Get cost from last hour (approximate by checking if total is too high for session)
    # For simplicity, we'll track per-session cost
    session_cost = sum(
        entry.get('cost', 0) 
        for entry in st.session_state.conversation_history 
        if entry.get('stats')
    )
    if session_cost >= RATE_LIMIT_COST:
        return False, f"Session cost limit (${RATE_LIMIT_COST:.2f}) reached. Start a new session."
    
    return True, ""


def record_request():
    """Record a request timestamp for rate limiting."""
    st.session_state.request_timestamps.append(time.time())


# --- UI Components ---
def render_token_stats_table(stats: dict, estimated: dict = None, show_input_output: bool = True):
    """
    Render a token/cost comparison table using native Streamlit.
    If estimated is provided, shows comparison with differences.
    If no estimates, does nothing (caller should handle simple stats display).
    """
    if not estimated:
        return
    
    actual_total = stats.get('input_tokens', 0) + stats.get('output_tokens', 0)
    est_input = estimated.get('user', 0) + estimated.get('system', 0) + estimated.get('rag', 0)
    est_total = estimated.get('total', 0)
    
    cost_diff = stats['cost'] - estimated['cost']
    total_diff = actual_total - est_total
    
    # Format difference
    def format_diff(val, is_cost=False):
        if is_cost:
            sign = "+" if val > 0 else ""
            return f"{sign}${val:.4f}"
        else:
            sign = "+" if val > 0 else ""
            return f"{sign}{val:,}"
    
    # Use columns for a simple table layout
    if show_input_output:
        input_diff = stats.get('input_tokens', 0) - est_input
        output_diff = stats.get('output_tokens', 0) - estimated.get('output', 0)
        
        col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])
        col1.markdown("**—**")
        col2.markdown("**Cost**")
        col3.markdown("**Total**")
        col4.markdown("**Input**")
        col5.markdown("**Output**")
        
        col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])
        col1.caption("Estimated")
        col2.caption(f"${estimated['cost']:.4f}")
        col3.caption(f"{est_total:,}")
        col4.caption(f"~{est_input:,}")
        col5.caption(f"~{estimated.get('output', 0):,}")
        
        col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])
        col1.caption("Actual")
        col2.caption(f"${stats['cost']:.4f}")
        col3.caption(f"{actual_total:,}")
        col4.caption(f"{stats.get('input_tokens', 0):,}")
        col5.caption(f"{stats.get('output_tokens', 0):,}")
        
        col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])
        col1.caption("Difference")
        col2.caption(format_diff(cost_diff, is_cost=True))
        col3.caption(format_diff(total_diff))
        col4.caption(format_diff(input_diff))
        col5.caption(format_diff(output_diff))
    else:
        col1, col2, col3 = st.columns([1.5, 1, 1])
        col1.markdown("**—**")
        col2.markdown("**Cost**")
        col3.markdown("**Total**")
        
        col1, col2, col3 = st.columns([1.5, 1, 1])
        col1.caption("Estimated")
        col2.caption(f"${estimated['cost']:.4f}")
        col3.caption(f"{est_total:,}")
        
        col1, col2, col3 = st.columns([1.5, 1, 1])
        col1.caption("Actual")
        col2.caption(f"${stats['cost']:.4f}")
        col3.caption(f"{actual_total:,}")
        
        col1, col2, col3 = st.columns([1.5, 1, 1])
        col1.caption("Difference")
        col2.caption(format_diff(cost_diff, is_cost=True))
        col3.caption(format_diff(total_diff))


def render_header():
    st.title("🎯 Nare")
    st.markdown("*The Narrative Reframer — spot the stories holding you back*")


def render_privacy_notice():
    with st.expander("🔒 Privacy", expanded=False):
        st.markdown("""
        **Your data stays yours.**
        
        - If using Claude API: You provide your own API key. Your entries go directly to your Anthropic account. We never see them.
        - If using Ollama: Everything runs 100% locally on your machine. Nothing leaves your device.
        - We don't store, log, or collect any of your journal entries.
        """)


def render_context_selection():
    st.markdown("### What's going on?")
    st.markdown("")
    
    # First row - 3 items
    cols = st.columns(3)
    context_items = list(CONTEXTS.items())
    
    for i, (key, ctx) in enumerate(context_items[:3]):
        with cols[i]:
            if st.button(
                f"{ctx['icon']} {ctx['label']}", 
                key=f"ctx_{key}",
                use_container_width=True
            ):
                st.session_state.context = key
                st.session_state.step = "journal"
                st.rerun()
    
    # Second row - 2 items centered
    cols2 = st.columns([1, 1, 1])
    for i, (key, ctx) in enumerate(context_items[3:5]):
        with cols2[i]:
            if st.button(
                f"{ctx['icon']} {ctx['label']}", 
                key=f"ctx_{key}",
                use_container_width=True
            ):
                st.session_state.context = key
                st.session_state.step = "journal"
                st.rerun()



# --- Sample Texts for Each Context ---
SAMPLE_TEXTS = {
    "setback": "I didn't get the job. The recruiter said they went with someone with more 'technical depth.' I've been a PM for 6 years but I keep hitting this wall. Maybe I'm just not cut out for these senior roles. The worst part is I thought the interviews went well — I clearly can't even judge my own performance anymore.",
    "decision": "I can't decide whether to stay in my current role or take this new opportunity. My current job is stable but boring — I'm basically maintaining features. The new role is at an early-stage startup, more risk but I'd be building from scratch. Everyone has opinions but I keep going back and forth. What if I make the wrong choice?",
    "procrastinating": "I have a PRD due tomorrow and I haven't started. Every time I open the doc I find something else to do — reorganized my task list, responded to Slack messages that could wait, read articles about AI strategy. The PRD is for a boring compliance feature that nobody's excited about, including me.",
    "imposter": "I just got promoted to Group PM and I feel like a fraud. In meetings with other GPMs they throw around frameworks and metrics I've never heard of. I nod along but half the time I'm lost. I got here by being good at execution but this level seems to require something different that I don't have.",
    "overwhelmed": "I have 6 stakeholders who all think their thing is the priority. I said I'd look into all of them. Sales needs a feature for a deal. Customer success has escalations. The exec has a pet project. I'm in meetings 8 hours a day and can't think. But I can't say no — they're all important."
}


def render_journal_entry():
    ctx = CONTEXTS[st.session_state.context]
    
    # Back button
    if st.button("← Back"):
        st.session_state.context = None
        st.session_state.step = "select_context"
        st.session_state.user_input = ""
        st.session_state.response = None
        st.rerun()
    
    st.markdown(f"### {ctx['icon']} {ctx['intro']}")
    st.markdown("")
    st.markdown(f"**{ctx['prompt']}**")
    
    # Pre-fill with sample if empty
    if not st.session_state.user_input:
        st.session_state.user_input = SAMPLE_TEXTS.get(st.session_state.context, "")
    
    st.caption("Edit the example below or write your own:")
    
    # Text area
    user_input = st.text_area(
        "Your response",
        value=st.session_state.user_input,
        height=200,
        label_visibility="collapsed",
        key="journal_input"
    )
    
    st.session_state.user_input = user_input
    
    return user_input


def render_sidebar():
    """
    Render navigation and quick reference in sidebar.
    Sidebar is now SIMPLE - just navigation. Model selection happens in main flow.
    """
    st.sidebar.markdown("## 🎯 Nare")
    st.sidebar.caption("The Narrative Reframer")
    st.sidebar.caption("*An experimental confidential coach for PMs*")
    
    st.sidebar.markdown("---")
    
    # Navigation - vertical layout
    home_type = "primary" if not (st.session_state.show_about or st.session_state.show_eval or st.session_state.show_data) else "secondary"
    if st.sidebar.button("🏠 Home", use_container_width=True, key="nav_home", type=home_type):
        st.session_state.show_about = False
        st.session_state.show_eval = False
        st.session_state.show_data = False
        st.session_state.step = "select_context"  # Reset to start
        st.rerun()
    
    learn_type = "primary" if st.session_state.show_about else "secondary"
    if st.sidebar.button("📖 Our Approach", use_container_width=True, key="nav_learn", type=learn_type):
        st.session_state.show_about = True
        st.session_state.show_eval = False
        st.session_state.show_data = False
        st.rerun()
    
    eval_type = "primary" if st.session_state.show_eval else "secondary"
    if st.sidebar.button("🧪 Evals", use_container_width=True, key="nav_eval", type=eval_type):
        st.session_state.show_eval = True
        st.session_state.show_about = False
        st.session_state.show_data = False
        st.rerun()
    
    data_type = "primary" if st.session_state.show_data else "secondary"
    if st.sidebar.button("🔒 Usage & Privacy", use_container_width=True, key="nav_data", type=data_type):
        st.session_state.show_data = True
        st.session_state.show_about = False
        st.session_state.show_eval = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Quick reference with link to Learn more
    st.sidebar.markdown("### 🐾 The 5 Saboteurs")
    st.sidebar.caption("""
    🦜 **Parrot** — Inner Critic  
    🦚 **Peacock** — Insecure Performer  
    🐙 **Octopus** — Anxious Controller  
    🐕 **Golden Retriever** — People Pleaser  
    🐇 **Rabbit** — Restless Escapist
    """)
    st.sidebar.caption("👆 Click **Our Approach** for details")


def render_backend_settings():
    """Legacy - no longer used in sidebar. Model selection is now in main flow."""
    pass  # Model selection moved to step 3 of main flow


def render_backend_selection():
    """Legacy wrapper - calls render_backend_settings."""
    return render_backend_settings()


def render_onboarding():
    """
    Clear first-time user experience with step-by-step setup.
    """
    # Check if Ollama is available - if so, auto-enable and skip
    ollama_available, ollama_models = check_ollama_available()
    if ollama_available:
        st.session_state.use_ollama = True
        st.rerun()
        return
    
    # Welcome screen
    st.markdown("# 👋 Welcome to Nare")
    st.markdown("")
    st.markdown("""
    Nare helps you recognize self-sabotaging patterns (we call them *saboteurs*) that hold you back as a Product Manager.
    
    **To get started, you'll need a Claude API key** (takes 2 minutes):
    """)
    
    st.markdown("---")
    
    # Step-by-step with visual progress
    st.markdown("### Setup Steps")
    
    col1, col2 = st.columns([1, 20])
    with col1:
        st.markdown("**1**")
    with col2:
        st.markdown("Go to **[console.anthropic.com](https://console.anthropic.com)** and sign in (or create account)")
    
    col1, col2 = st.columns([1, 20])
    with col1:
        st.markdown("**2**")
    with col2:
        st.markdown("Click **Settings** → **API Keys** in the left sidebar")
    
    col1, col2 = st.columns([1, 20])
    with col1:
        st.markdown("**3**")
    with col2:
        st.markdown("Click **Create Key** and copy it")
    
    col1, col2 = st.columns([1, 20])
    with col1:
        st.markdown("**4**")
    with col2:
        st.markdown("Paste your key below:")
    
    st.markdown("")
    
    # API key input - prominent
    api_key = st.text_input(
        "Your Claude API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        help="Your key stays on your device. We never see it.",
        key="onboarding_api_key",
        label_visibility="collapsed"
    )
    
    # Validation and continue
    if api_key:
        if api_key.startswith("sk-ant-"):
            st.session_state.api_key = api_key
            st.success("✅ Valid API key format!")
            
            if st.button("🚀 Start Using Nare", type="primary", use_container_width=True):
                record_audit_event("setup_complete", {"method": "api_key"})
                st.rerun()
        else:
            st.error("❌ That doesn't look like a Claude API key. It should start with `sk-ant-`")
    
    st.markdown("---")
    
    # Billing note
    st.info("""
    💡 **First time using Claude API?** 
    
    You may need to add a payment method at [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing).
    
    Don't worry — each conversation costs about **$0.01** (one cent).
    """)
    
    # Alternative: Local option
    with st.expander("🏠 Prefer to run 100% locally? (Advanced)"):
        st.markdown("""
        You can run Nare entirely on your machine with no API key:
        
        1. Install [Ollama](https://ollama.ai)
        2. Run: `ollama pull llama3.1:8b`
        3. Restart this app
        
        The app will automatically detect Ollama and use it.
        """)


def render_api_key_setup():
    """Show setup instructions when no backend is configured."""
    render_onboarding()
    return None


def render_pattern_reference():
    """Legacy function - sidebar now handled by render_sidebar."""
    pass  # No longer needed - sidebar is rendered separately


def render_data_management_page():
    """Render the data management and export page."""
    st.markdown("# 🔒 Usage & Privacy")
    
    # Corrected privacy statement
    st.info("""
    **Where does your data go?**
    
    - **Your journal entries** → Sent to Claude API (Anthropic) or Ollama (local) for processing, then discarded
    - **Logs, feedback, preferences** → Stored locally on your device only
    - **We (the app developers)** → Never see your data
    
    For maximum privacy, use **Ollama (Local)** mode — everything stays on your machine.
    """)
    
    st.markdown("---")
    
    # Rate Limits
    st.markdown("## ⏱️ Rate Limits")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Requests/min", f"{len(st.session_state.get('request_timestamps', []))}/{RATE_LIMIT_REQUESTS}")
    with col2:
        session_cost = sum(
            entry.get('stats', {}).get('cost', 0) 
            for entry in st.session_state.get('conversation_history', [])
            if entry.get('stats')
        )
        st.metric("Session cost", f"${session_cost:.4f} / ${RATE_LIMIT_COST:.2f}")
    
    st.caption(f"Limits: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s, ${RATE_LIMIT_COST:.2f} per session")
    
    st.markdown("---")
    
    # Usage Statistics - moved from sidebar
    st.markdown("## 📊 Usage Statistics")
    
    prefs = load_preferences()
    feedback = load_feedback()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Spent", f"${prefs.get('total_cost', 0.0):.4f}")
    col2.metric("👍 Helpful", feedback["total_up"])
    col3.metric("👎 Not Helpful", feedback["total_down"])
    
    total_comparisons = prefs["claude_wins"] + prefs["llama_wins"]
    col4.metric("⚖️ Comparisons", total_comparisons)
    
    # Model preference breakdown
    if total_comparisons > 0:
        st.markdown("")
        claude_pct = (prefs["claude_wins"] / total_comparisons) * 100
        llama_pct = (prefs["llama_wins"] / total_comparisons) * 100
        st.caption(f"Model preferences: Claude {prefs['claude_wins']} ({claude_pct:.0f}%) · Llama {prefs['llama_wins']} ({llama_pct:.0f}%)")
    
    st.markdown("---")
    
    # Feedback Data
    st.markdown("## 👍 Feedback Data")
    
    total_feedback = feedback["total_up"] + feedback["total_down"]
    if total_feedback > 0:
        helpful_rate = feedback['total_up'] / total_feedback * 100
        st.caption(f"Helpful rate: {helpful_rate:.0f}% ({feedback['total_up']}/{total_feedback})")
        st.markdown("")
        st.markdown("Feedback data can be used to fine-tune models or improve prompts.")
        
        feedback_json = export_feedback_data()
        st.download_button(
            "📥 Export Feedback Data (JSON)",
            feedback_json,
            file_name="pm_saboteurs_feedback.json",
            mime="application/json",
            help="Download feedback data for analysis or fine-tuning"
        )
    else:
        st.caption("No feedback recorded yet. Use 👍/👎 buttons after responses.")
    
    st.markdown("---")
    
    # Audit trail
    st.markdown("## 📋 Audit Trail")
    audit = load_audit_trail()
    
    st.caption(f"{len(audit['events'])} events recorded")
    
    if audit['events']:
        # Show recent events in expander
        with st.expander("Recent activity", expanded=False):
            for event in reversed(audit['events'][-10:]):
                timestamp = event['timestamp'][:19].replace('T', ' ')
                action = event['action']
                st.caption(f"`{timestamp}` — {action}")
        
        audit_json = export_audit_trail()
        st.download_button(
            "📥 Export Audit Trail (JSON)",
            audit_json,
            file_name="pm_saboteurs_audit.json",
            mime="application/json",
            help="Download complete audit trail for compliance"
        )
    
    st.markdown("---")
    
    # Interaction logs
    st.markdown("## 📝 Interaction Logs")
    
    if LOG_FILE.exists():
        log_size = LOG_FILE.stat().st_size
        log_lines = sum(1 for _ in open(LOG_FILE))
        st.caption(f"{log_lines} interactions logged ({log_size / 1024:.1f} KB)")
        
        log_content = LOG_FILE.read_text()
        st.download_button(
            "📥 Export Logs (JSONL)",
            log_content,
            file_name="pm_saboteurs_logs.jsonl",
            mime="application/jsonl",
            help="Download interaction logs for debugging"
        )
    else:
        st.markdown("No interactions logged yet.")
    
    st.markdown("---")
    
    # Data locations
    st.markdown("## 📂 Data Locations")
    st.markdown(f"""
    All data is stored in: `{DATA_DIR}`
    
    - **Preferences**: `{PREFS_FILE.name}`
    - **Feedback**: `{FEEDBACK_FILE.name}`
    - **Audit Trail**: `{AUDIT_FILE.name}`
    - **Logs**: `{LOG_FILE.name}`
    - **Cache**: `{CACHE_FILE.name}`
    """)
    
    st.markdown("---")
    
    # Clear data
    st.markdown("## 🗑️ Clear Data")
    st.markdown("**Warning:** This cannot be undone.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Feedback", type="secondary"):
            save_feedback({"thumbs_up": [], "thumbs_down": [], "total_up": 0, "total_down": 0})
            st.success("Feedback cleared!")
            st.rerun()
    
    with col2:
        if st.button("Clear All Data", type="secondary"):
            # Clear all files
            for f in [PREFS_FILE, FEEDBACK_FILE, AUDIT_FILE, LOG_FILE, CACHE_FILE]:
                if f.exists():
                    f.unlink()
            st.success("All data cleared!")
            st.rerun()


def render_about_page():
    """Render the Our Approach page with overview, framework, and disclaimers."""
    st.markdown("# 📖 Our Approach")
    st.markdown("")
    
    # Overview section
    st.markdown("""
    ## How Nare Works
    
    Nare combines insights from **psychological research** with the relatable concept of **spirit animals** 
    to create a framework that is both deep and accessible.
    
    The idea is simple: we all have inner voices that try to protect us but sometimes hold us back. 
    Rather than fighting these voices, Nare helps you **recognize** them, **name** them, and **reframe** 
    the narratives they tell you.
    
    We've mapped five common self-sabotaging patterns to spirit animals — not because the psychology 
    is simplistic, but because memorable metaphors help us catch ourselves in the moment. When you 
    notice "oh, that's my Parrot talking," you've already created space between yourself and the pattern.
    
    Nare acts as your **Grounded Self** — the calm, curious, compassionate voice that helps you 
    rein in these spirit animals when they're running the show.
    """)
    
    st.markdown("---")
    
    # The Five Saboteurs
    st.markdown("## 🐾 The Five Saboteurs")
    st.markdown("""
    These are the five spirit animals Nare helps you rein in. Each represents a common pattern 
    that developed to protect you but may now be holding you back.
    """)
    st.caption("Click each to learn more")
    
    with st.expander("🦜 **The Parrot** — Inner Critic", expanded=False):
        st.markdown("""
        **Core fear:** "I'm not enough"
        
        **What it does:** The Parrot repeats harsh, critical scripts — often things we heard 
        growing up or internalized from past failures. It finds fault with everything you do.
        
        **How it sounds:**
        - "You should have done better"
        - "What's wrong with you?"
        - "You always mess this up"
        
        **The lie it tells:** That harsh self-criticism will motivate you to improve. 
        (Research shows the opposite — self-compassion is more effective.)
        
        **Reining it in:** Notice when you're speaking to yourself more harshly than you'd speak to a friend. The Parrot thinks it's helping, but it's not.
        
        **Psychological roots:** Inner Critic (IFS), Superego (Freud), Negative Self-Talk (CBT), Harsh Inner Voice (Compassion-Focused Therapy)
        """)
    
    with st.expander("🦚 **The Peacock** — Insecure Performer", expanded=False):
        st.markdown("""
        **Core fear:** "I'm only worth what I produce"
        
        **What it does:** The Peacock ties your entire self-worth to achievement, status, and 
        external validation. It's never satisfied — there's always another goal, another comparison.
        
        **How it sounds:**
        - "What have you accomplished lately?"
        - "You're falling behind your peers"
        - "If this fails, you're a failure"
        
        **The lie it tells:** That your worth is conditional on performance.
        
        **Reining it in:** Notice when you're conflating what you *do* with who you *are*. Your worth isn't up for performance review.
        
        **Psychological roots:** Contingent Self-Worth (Self-Determination Theory), Perfectionism (CBT), Achievement-Based Self-Esteem (Psychodynamic), Striver Part (IFS)
        """)
    
    with st.expander("🐙 **The Octopus** — Anxious Controller", expanded=False):
        st.markdown("""
        **Core fear:** "If I let go, disaster follows"
        
        **What it does:** The Octopus needs eight arms in everything. It micromanages, struggles 
        to delegate, and feels anxious when things are outside its control.
        
        **How it sounds:**
        - "If you're not in charge, everything falls apart"
        - "You can't trust anyone else to do it right"
        - "You need to stay on top of this"
        
        **The lie it tells:** That control equals safety.
        
        **Reining it in:** Notice when you're holding on so tight you're crushing the thing you're trying to protect. Sometimes letting go is the safest move.
        
        **Psychological roots:** Controller/Manager Part (IFS), Type A Behavior Pattern (Health Psychology), Hypervigilance (Trauma-Informed), Intolerance of Uncertainty (CBT)
        """)
    
    with st.expander("🐕 **The Golden Retriever** — Compulsive Pleaser", expanded=False):
        st.markdown("""
        **Core fear:** "I'll be rejected if I disappoint"
        
        **What it does:** The Golden Retriever compulsively prioritizes others' needs over your own. 
        It says yes when you mean no, over-gives until you're depleted.
        
        **How it sounds:**
        - "They need you"
        - "You can't let them down"
        - "What will they think of you?"
        
        **The lie it tells:** That love must be earned through endless giving.
        
        **Reining it in:** Notice when you're abandoning yourself to please others. A 'no' to them can be a 'yes' to you.
        
        **Psychological roots:** Caretaker Part (IFS), Fawn Response (Trauma/Polyvagal Theory), Codependency (Attachment Theory), People-Pleasing Schema (Schema Therapy)
        """)
    
    with st.expander("🐇 **The Rabbit** — Restless Escapist", expanded=False):
        st.markdown("""
        **Core fear:** "This present moment is unbearable"
        
        **What it does:** The Rabbit is always ready to bolt. It seeks the next opportunity, the 
        next distraction, the next escape route. It can't sit with discomfort.
        
        **How it sounds:**
        - "This isn't it"
        - "There's something better out there"
        - "Let's just move on to the next thing"
        
        **The lie it tells:** That escape will bring peace. (It just brings new problems.)
        
        **Reining it in:** Notice when the urge to run is really an urge to avoid. What happens if you stay?
        
        **Psychological roots:** Avoidant Coping (CBT), Experiential Avoidance (ACT), Novelty-Seeking (Temperament Theory), Flight Response (Polyvagal Theory), Distractor Part (IFS)
        """)
    
    st.markdown("---")
    
    # The Grounded Self
    with st.expander("🌿 **The Grounded Self** — Your True Voice", expanded=True):
        st.markdown("""
        The Grounded Self is not another pattern — it's the part of you that can observe all 
        the patterns without being controlled by them.
        
        **Qualities of the Grounded Self:**
        - **Calm** — not reactive
        - **Curious** — not judgmental
        - **Compassionate** — not harsh
        - **Clear** — can see what's actually happening
        
        When Nare responds, it speaks from this Grounded Self perspective — validating what 
        you're experiencing, naming the saboteur at play, and offering a question or reframe 
        that opens a door rather than lecturing.
        
        The goal isn't to eliminate your saboteurs (they're part of you), but to recognize 
        when they're driving and gently take back the wheel.
        
        **Psychological roots:** Self (IFS), Observing Self (ACT), Wise Mind (DBT), Mindful Awareness (MBCT), Self-Compassion (Compassion-Focused Therapy)
        """)
    
    st.markdown("---")
    
    # Psychological Foundation - expanded with links
    st.markdown("## 🧠 Psychological Foundation")
    st.markdown("""
    Nare's framework synthesizes concepts from established, evidence-based psychological approaches. 
    Here's the research behind the approach:
    """)
    
    with st.expander("**Internal Family Systems (IFS)**", expanded=False):
        st.markdown("""
        Developed by Dr. Richard Schwartz in the 1980s, IFS views the mind as containing multiple 
        "parts" — subpersonalities that developed to protect us. These parts aren't pathological; 
        they're adaptive strategies that may have outlived their usefulness.
        
        The "Self" in IFS (our "Grounded Self") is characterized by qualities like curiosity, 
        calm, compassion, and clarity — the same qualities we cultivate in Nare's responses.
        
        **Further reading:**
        - [IFS Institute - Official Resource](https://ifs-institute.com/)
        - [Internal Family Systems Therapy (Psychology Today)](https://www.psychologytoday.com/us/therapy-types/internal-family-systems-therapy)
        - Schwartz, R.C. (2021). *No Bad Parts: Healing Trauma and Restoring Wholeness with the Internal Family Systems Model*
        """)
    
    with st.expander("**Cognitive Behavioral Therapy (CBT)**", expanded=False):
        st.markdown("""
        CBT, developed by Dr. Aaron Beck, identifies predictable cognitive distortions — patterns 
        of thinking that feel true but aren't. Examples include catastrophizing, all-or-nothing 
        thinking, and mind-reading.
        
        By naming these patterns, we reduce their automatic power over us. This is the foundation 
        of Nare's approach: recognition precedes change.
        
        **Further reading:**
        - [What is CBT? (American Psychological Association)](https://www.apa.org/ptsd-guideline/patients-and-families/cognitive-behavioral)
        - [Cognitive Distortions (Beck Institute)](https://beckinstitute.org/blog/cognitive-distortions/)
        - Burns, D.D. (1980). *Feeling Good: The New Mood Therapy*
        """)
    
    with st.expander("**Acceptance and Commitment Therapy (ACT)**", expanded=False):
        st.markdown("""
        ACT, developed by Dr. Steven Hayes, emphasizes psychological flexibility — the ability to 
        be present, open up to difficult experiences, and take values-driven action.
        
        Key ACT concepts in Nare include "defusion" (separating yourself from your thoughts) and 
        the "observing self" (the part of you that can watch your thoughts without being them).
        
        **Further reading:**
        - [Association for Contextual Behavioral Science](https://contextualscience.org/act)
        - [ACT Overview (Psychology Today)](https://www.psychologytoday.com/us/therapy-types/acceptance-and-commitment-therapy)
        - Harris, R. (2008). *The Happiness Trap*
        """)
    
    with st.expander("**Compassion-Focused Therapy (CFT)**", expanded=False):
        st.markdown("""
        Developed by Dr. Paul Gilbert, CFT specifically addresses the harsh inner critic (our Parrot) 
        and helps people develop self-compassion. Research shows self-compassion is more motivating 
        than self-criticism.
        
        **Further reading:**
        - [The Compassionate Mind Foundation](https://www.compassionatemind.co.uk/)
        - [Self-Compassion Research (Dr. Kristin Neff)](https://self-compassion.org/the-research/)
        - Gilbert, P. (2009). *The Compassionate Mind*
        """)
    
    with st.expander("**Polyvagal Theory & Trauma-Informed Approaches**", expanded=False):
        st.markdown("""
        Dr. Stephen Porges' Polyvagal Theory explains how our nervous system responds to perceived 
        threat — including fight, flight, and fawn responses. Many saboteur patterns (Octopus's 
        control, Rabbit's escape, Golden Retriever's fawning) can be understood as nervous system 
        responses that once kept us safe.
        
        **Further reading:**
        - [Polyvagal Institute](https://www.polyvagalinstitute.org/)
        - [Understanding Polyvagal Theory (Psychology Today)](https://www.psychologytoday.com/us/basics/polyvagal-theory)
        - Dana, D. (2018). *The Polyvagal Theory in Therapy*
        """)
    
    st.markdown("---")
    
    # Disclaimers
    st.markdown("## ⚠️ Important Disclaimers")
    
    st.warning("""
    **Nare is not therapy.** This tool is designed for self-reflection and personal growth, 
    not as a substitute for professional mental health treatment.
    """)
    
    st.markdown("""
    **Please understand:**
    
    - **This is an AI tool**, not a licensed therapist, counselor, or mental health professional. 
      It cannot diagnose conditions, prescribe treatment, or provide clinical care.
    
    - **The saboteur framework is a simplified model** for self-reflection. Real human psychology 
      is more complex, and your experiences may not fit neatly into these categories.
    
    - **If you're experiencing a mental health crisis**, please contact a professional or crisis 
      service immediately:
      - **National Suicide Prevention Lifeline:** 988 (US)
      - **Crisis Text Line:** Text HOME to 741741
      - **International Association for Suicide Prevention:** https://www.iasp.info/resources/Crisis_Centres/
    
    - **AI can make mistakes.** Responses are generated by a language model that may occasionally 
      produce inaccurate, unhelpful, or inappropriate content. Use your own judgment.
    
    - **Your privacy is protected** but this is experimental software. See the Usage & Privacy 
      section for details on how your data is handled.
    
    By using Nare, you acknowledge that this is an experimental tool for self-reflection, 
    not a medical or therapeutic service.
    """)


def extract_saboteurs_from_response(response: str) -> list:
    """Extract detected saboteurs from LLM response."""
    detected = []
    pattern_keywords = {
        "parrot": ["parrot"],
        "peacock": ["peacock"],
        "octopus": ["octopus"],
        "golden_retriever": ["golden retriever"],
        "rabbit": ["rabbit"]
    }
    
    response_lower = response.lower()
    for pattern, keywords in pattern_keywords.items():
        for kw in keywords:
            if kw in response_lower:
                if pattern not in detected:
                    detected.append(pattern)
                break
    
    return detected


def run_evaluation(entries: list, api_key: str = None, use_rag: bool = True, use_ollama: bool = False, ollama_model: str = "llama3.1:8b") -> list:
    """Run evaluation on a list of golden dataset entries."""
    results = []
    
    for entry in entries:
        try:
            if use_ollama:
                response, stats = call_ollama(
                    ollama_model,
                    entry["context"],
                    entry["text"],
                    use_rag=use_rag
                )
            else:
                response, stats = call_anthropic(
                    api_key,
                    entry["context"],
                    entry["text"],
                    use_rag=use_rag
                )
                record_cost(stats['cost'])
            
            detected = extract_saboteurs_from_response(response)
            expected_primary = entry["primary_saboteur"]
            expected_all = [expected_primary] + entry.get("secondary_saboteurs", []) if expected_primary else []
            
            # Score the result
            primary_correct = expected_primary in detected if expected_primary else len(detected) == 0
            
            # False positives: detected but not in expected
            false_positives = [d for d in detected if d not in expected_all] if expected_all else detected
            
            # Missed: expected but not detected  
            missed = [e for e in expected_all if e not in detected] if expected_all else []
            
            results.append({
                "id": entry["id"],
                "context": entry["context"],
                "text": entry["text"],
                "expected_primary": expected_primary,
                "expected_secondary": entry.get("secondary_saboteurs", []),
                "detected": detected,
                "primary_correct": primary_correct,
                "false_positives": false_positives,
                "missed": missed,
                "response": response,
                "stats": stats,
                "notes": entry.get("notes", "")
            })
            
        except Exception as e:
            results.append({
                "id": entry["id"],
                "error": str(e)
            })
    
    return results


def render_eval_page():
    """Render the evaluation dashboard."""
    st.markdown("# 🧪 Evals")
    st.markdown("Test saboteur detection against the golden dataset.")
    
    # Import golden dataset
    try:
        from golden_dataset import GOLDEN_DATASET, get_by_saboteur, get_edge_cases
    except ImportError:
        st.error("Golden dataset not found. Make sure golden_dataset.py exists.")
        return
    
    # Check available backends
    ollama_available, ollama_models = check_ollama_available()
    has_api_key = bool(st.session_state.api_key)
    
    if not has_api_key and not ollama_available:
        st.warning("⚠️ No backend available. Add Claude API key or start Ollama.")
        return
    
    st.markdown("---")
    
    # Config
    col1, col2 = st.columns(2)
    
    with col1:
        # Backend selection
        backend_options = []
        if has_api_key:
            backend_options.append("Claude API")
        if ollama_available:
            backend_options.append("Ollama (Local)")
        if has_api_key and ollama_available:
            backend_options.append("Compare Both")
        
        backend = st.selectbox("Backend", backend_options)
    
    with col2:
        use_rag = st.checkbox("🔍 Use RAG", value=True)
    
    # Number of test cases slider
    total_cases = len(GOLDEN_DATASET)
    num_cases = st.slider(
        "Number of test cases",
        min_value=3,
        max_value=total_cases,
        value=min(10, total_cases),  # Default to 10 for faster runs
        help=f"Run a subset for quick testing, or all {total_cases} for full evaluation"
    )
    
    # Show estimated time (based on real-world testing: ~13s per case for Compare Both, ~6s for single)
    est_time_per_case = 13 if backend == "Compare Both" else 6  # seconds
    est_total_time = num_cases * est_time_per_case
    if est_total_time < 60:
        time_str = f"~{est_total_time:.0f} seconds"
    else:
        time_str = f"~{est_total_time/60:.1f} minutes"
    
    st.caption(f"**{num_cases}** of {total_cases} test cases · Estimated time: {time_str}")
    
    # Ollama model selection if needed
    ollama_model = "llama3.1:8b"
    if ollama_available and len(ollama_models) > 1:
        ollama_model = st.selectbox("Ollama Model", ollama_models)
    elif ollama_available and ollama_models:
        ollama_model = ollama_models[0]
    
    # Initialize results in session state
    if "eval_results" not in st.session_state:
        st.session_state.eval_results = None
    if "eval_results_compare" not in st.session_state:
        st.session_state.eval_results_compare = None
    
    # Select subset of test cases
    test_cases = GOLDEN_DATASET[:num_cases]
    
    # Run button
    if st.button("🚀 Run Evaluation", type="primary", use_container_width=True):
        progress = st.progress(0)
        status = st.empty()
        live_output = st.empty()
        
        # Helper to show live streaming output
        def show_live_update(entry_id, entry_text, detected, is_correct, backend_name=""):
            prefix = f"**[{backend_name}]** " if backend_name else ""
            snippet = entry_text[:80] + "..." if len(entry_text) > 80 else entry_text
            emoji = "✅" if is_correct else "❌"
            saboteurs = ", ".join([s.replace("_", " ").title() for s in detected]) if detected else "None"
            live_output.markdown(f"""
{prefix}**{entry_id}** {emoji}

> *"{snippet}"*

Detected: **{saboteurs}**

---
""")
        
        if backend == "Compare Both":
            # Run both backends
            claude_results = []
            ollama_results = []
            
            for i, entry in enumerate(test_cases):
                status.text(f"🔄 Testing {entry['id']} ({i+1}/{num_cases})...")
                progress.progress((i + 0.5) / num_cases)
                
                # Claude
                claude_result = run_evaluation(
                    [entry], 
                    api_key=st.session_state.api_key,
                    use_rag=use_rag,
                    use_ollama=False
                )
                claude_results.extend(claude_result)
                if claude_result and "error" not in claude_result[0]:
                    show_live_update(
                        entry['id'], 
                        entry['text'], 
                        claude_result[0]['detected'],
                        claude_result[0]['primary_correct'],
                        "Claude"
                    )
                
                progress.progress((i + 0.75) / num_cases)
                
                # Ollama
                ollama_result = run_evaluation(
                    [entry], 
                    use_rag=use_rag,
                    use_ollama=True,
                    ollama_model=ollama_model
                )
                ollama_results.extend(ollama_result)
                if ollama_result and "error" not in ollama_result[0]:
                    show_live_update(
                        entry['id'], 
                        entry['text'], 
                        ollama_result[0]['detected'],
                        ollama_result[0]['primary_correct'],
                        "Llama"
                    )
                
                progress.progress((i + 1) / num_cases)
            
            st.session_state.eval_results = claude_results
            st.session_state.eval_results_compare = ollama_results
            st.session_state.eval_backend = "Compare Both"
            st.session_state.eval_ollama_model = ollama_model
            st.session_state.eval_num_cases = num_cases
        else:
            # Single backend
            use_ollama = backend == "Ollama (Local)"
            results = []
            
            for i, entry in enumerate(test_cases):
                status.text(f"🔄 Testing {entry['id']} ({i+1}/{num_cases})...")
                progress.progress((i + 1) / num_cases)
                
                result = run_evaluation(
                    [entry], 
                    api_key=st.session_state.api_key,
                    use_rag=use_rag,
                    use_ollama=use_ollama,
                    ollama_model=ollama_model
                )
                results.extend(result)
                
                if result and "error" not in result[0]:
                    show_live_update(
                        entry['id'], 
                        entry['text'], 
                        result[0]['detected'],
                        result[0]['primary_correct']
                    )
            
            st.session_state.eval_results = results
            st.session_state.eval_results_compare = None
            st.session_state.eval_backend = backend
            st.session_state.eval_num_cases = num_cases
        
        progress.empty()
        status.empty()
        live_output.empty()
        st.rerun()
    
    # Show results if available
    if st.session_state.eval_results:
        st.markdown("---")
        
        # Show how many cases were run
        cases_run = st.session_state.get("eval_num_cases", len(st.session_state.eval_results))
        if cases_run < total_cases:
            st.caption(f"📊 Results based on {cases_run} of {total_cases} test cases")
        
        # Check if comparison mode
        if st.session_state.eval_results_compare:
            render_comparison_results(
                st.session_state.eval_results,
                st.session_state.eval_results_compare,
                st.session_state.get("eval_ollama_model", "Ollama")
            )
        else:
            render_single_results(st.session_state.eval_results, st.session_state.eval_backend)
        
        # Clear results button
        st.markdown("---")
        if st.button("🗑️ Clear Results"):
            st.session_state.eval_results = None
            st.session_state.eval_results_compare = None
            st.rerun()


def calculate_metrics(results: list) -> dict:
    """Calculate precision, recall, F1 from results."""
    successful = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]
    
    if not successful:
        return {"error": "No successful results"}
    
    primary_correct = sum(1 for r in successful if r["primary_correct"])
    total_fp = sum(len(r["false_positives"]) for r in successful)
    total_missed = sum(len(r["missed"]) for r in successful)
    
    # Calculate precision and recall
    total_detected = sum(len(r["detected"]) for r in successful)
    total_expected = sum(1 for r in successful if r["expected_primary"]) + sum(len(r["expected_secondary"]) for r in successful)
    
    # True positives = detected AND in expected
    true_positives = 0
    for r in successful:
        expected_all = [r["expected_primary"]] + r.get("expected_secondary", []) if r["expected_primary"] else []
        true_positives += len([d for d in r["detected"] if d in expected_all])
    
    precision = true_positives / total_detected if total_detected > 0 else 0
    recall = true_positives / total_expected if total_expected > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "successful": successful,
        "errors": errors,
        "primary_correct": primary_correct,
        "total": len(successful),
        "true_positives": true_positives,
        "false_positives": total_fp,
        "missed": total_missed,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def render_comparison_results(claude_results: list, ollama_results: list, ollama_model: str):
    """Render side-by-side comparison of Claude vs Ollama."""
    st.markdown("## 📊 Comparison: Claude API vs " + ollama_model)
    
    claude_metrics = calculate_metrics(claude_results)
    ollama_metrics = calculate_metrics(ollama_results)
    
    if "error" in claude_metrics or "error" in ollama_metrics:
        st.error("Error calculating metrics")
        return
    
    # Determine winner
    claude_wins = claude_metrics['f1'] > ollama_metrics['f1']
    winner = "Claude API" if claude_wins else ollama_model
    loser = ollama_model if claude_wins else "Claude API"
    winner_f1 = claude_metrics['f1'] if claude_wins else ollama_metrics['f1']
    loser_f1 = ollama_metrics['f1'] if claude_wins else claude_metrics['f1']
    winner_prec = claude_metrics['precision'] if claude_wins else ollama_metrics['precision']
    loser_prec = ollama_metrics['precision'] if claude_wins else claude_metrics['precision']
    winner_recall = claude_metrics['recall'] if claude_wins else ollama_metrics['recall']
    loser_recall = ollama_metrics['recall'] if claude_wins else claude_metrics['recall']
    winner_fp = claude_metrics['false_positives'] if claude_wins else ollama_metrics['false_positives']
    loser_fp = ollama_metrics['false_positives'] if claude_wins else claude_metrics['false_positives']
    
    # Summary FIRST - human readable paragraph
    st.markdown("### 🏆 Summary")
    
    if claude_metrics['f1'] == ollama_metrics['f1']:
        st.markdown(f"Both models performed equally with an **F1 score of {claude_metrics['f1']:.0%}**.")
    else:
        st.markdown(f"""
**{winner}** is the clear winner with an F1 score of **{winner_f1:.0%}** compared to {loser}'s {loser_f1:.0%}.

**What does this mean?**

- **F1 Score ({winner_f1:.0%} vs {loser_f1:.0%})**: F1 is the balanced average of precision and recall — it tells you how good the model is overall at finding the right saboteurs without making mistakes. A higher F1 means the model is both accurate and thorough.

- **Precision ({winner_prec:.0%} vs {loser_prec:.0%})**: When {winner} identifies a saboteur, it's correct {winner_prec:.0%} of the time. {loser} has more false alarms — it over-detects patterns that aren't really there.

- **Recall ({winner_recall:.0%} vs {loser_recall:.0%})**: {winner} catches {winner_recall:.0%} of the saboteurs that are actually present. Higher recall means fewer missed patterns.

- **False Positives ({winner_fp} vs {loser_fp})**: {loser} flagged {loser_fp} saboteurs that weren't in the expected labels, compared to just {winner_fp} for {winner}. This matters because over-detection can feel like the tool is "reading too much into things."

**Bottom line**: {winner} is more reliable for production use — it identifies the right patterns without crying wolf.
""")
    
    st.markdown("---")
    
    # Comparison table SECOND
    st.markdown("### 📈 Detailed Metrics")
    
    # Helper to format value with color
    def format_with_color(val, is_winner, is_percentage=False):
        color = "green" if is_winner else "red"
        if is_percentage:
            return f'<span style="color:{color}; font-weight:600;">{val:.0%}</span>'
        else:
            return f'<span style="color:{color}; font-weight:600;">{val}</span>'
    
    c_acc = claude_metrics['primary_correct'] / claude_metrics['total'] * 100
    o_acc = ollama_metrics['primary_correct'] / ollama_metrics['total'] * 100
    
    # Use Streamlit columns and metrics for better compatibility
    st.markdown(f"**Comparing Claude API vs {ollama_model}**")
    st.caption("💡 Green = better, Red = worse")
    
    # Header row
    col_metric, col_claude, col_ollama = st.columns([2, 1, 1])
    col_metric.markdown("**Metric**")
    col_claude.markdown("**Claude API**")
    col_ollama.markdown(f"**{ollama_model}**")
    
    st.markdown("---")
    
    # Helper function
    def metric_row(label, c_val, o_val, c_num, o_num, higher_better=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.markdown(f"**{label}**")
        
        if higher_better:
            c_better = c_num > o_num
            o_better = o_num > c_num
        else:
            c_better = c_num < o_num
            o_better = o_num < c_num
        
        c_icon = "✅" if c_better else ("❌" if o_better else "")
        o_icon = "✅" if o_better else ("❌" if c_better else "")
        
        col2.markdown(f"{c_icon} {c_val}")
        col3.markdown(f"{o_icon} {o_val}")
    
    metric_row("Primary Accuracy", 
               f"{claude_metrics['primary_correct']}/{claude_metrics['total']} ({c_acc:.0f}%)",
               f"{ollama_metrics['primary_correct']}/{ollama_metrics['total']} ({o_acc:.0f}%)",
               c_acc, o_acc)
    
    metric_row("Precision",
               f"{claude_metrics['precision']:.0%}",
               f"{ollama_metrics['precision']:.0%}",
               claude_metrics['precision'], ollama_metrics['precision'])
    
    metric_row("Recall",
               f"{claude_metrics['recall']:.0%}",
               f"{ollama_metrics['recall']:.0%}",
               claude_metrics['recall'], ollama_metrics['recall'])
    
    metric_row("F1 Score",
               f"{claude_metrics['f1']:.0%}",
               f"{ollama_metrics['f1']:.0%}",
               claude_metrics['f1'], ollama_metrics['f1'])
    
    metric_row("True Positives",
               str(claude_metrics['true_positives']),
               str(ollama_metrics['true_positives']),
               claude_metrics['true_positives'], ollama_metrics['true_positives'])
    
    metric_row("False Positives",
               str(claude_metrics['false_positives']),
               str(ollama_metrics['false_positives']),
               claude_metrics['false_positives'], ollama_metrics['false_positives'],
               higher_better=False)
    
    metric_row("Missed",
               str(claude_metrics['missed']),
               str(ollama_metrics['missed']),
               claude_metrics['missed'], ollama_metrics['missed'],
               higher_better=False)
    
    # Detailed results by entry
    st.markdown("---")
    st.markdown("### 🔍 Detailed Results for Each Test Case")
    st.caption("Showing entries where models disagreed or made errors")
    
    for i, (cr, or_) in enumerate(zip(claude_results, ollama_results)):
        if "error" in cr or "error" in or_:
            continue
        
        claude_correct = "✅" if cr["primary_correct"] else "❌"
        ollama_correct = "✅" if or_["primary_correct"] else "❌"
        
        # Only show if there's a difference or incorrect
        if cr["primary_correct"] != or_["primary_correct"] or not cr["primary_correct"]:
            with st.expander(f"**{cr['id']}** — Claude {claude_correct} | {ollama_model} {ollama_correct}"):
                st.markdown(f"**Input Text:** *\"{cr['text'][:150]}...\"*")
                st.markdown(f"**Expected Saboteur:** {cr['expected_primary'].replace('_', ' ').title() if cr['expected_primary'] else 'None'}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Claude detected:**")
                    detected_names = [s.replace('_', ' ').title() for s in cr['detected']] if cr['detected'] else ["None"]
                    st.write(", ".join(detected_names))
                    if cr['false_positives']:
                        fp_names = [s.replace('_', ' ').title() for s in cr['false_positives']]
                        st.warning(f"False Positives: {', '.join(fp_names)}")
                
                with col2:
                    st.markdown(f"**{ollama_model} detected:**")
                    detected_names = [s.replace('_', ' ').title() for s in or_['detected']] if or_['detected'] else ["None"]
                    st.write(", ".join(detected_names))
                    if or_['false_positives']:
                        fp_names = [s.replace('_', ' ').title() for s in or_['false_positives']]
                        st.warning(f"False Positives: {', '.join(fp_names)}")


def render_single_results(results: list, backend: str):
    """Render results for a single backend."""
    st.markdown(f"## 📊 Results ({backend})")
    
    metrics = calculate_metrics(results)
    
    if "error" in metrics:
        st.error(metrics["error"])
        return
    
    successful = metrics["successful"]
    errors = metrics["errors"]
    
    # Display metrics - Row 1
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Primary Accuracy", f"{metrics['primary_correct']}/{metrics['total']}", 
                f"{(metrics['primary_correct']/metrics['total']*100):.0f}%")
    col2.metric("Precision", f"{metrics['precision']:.0%}", help="Correct detections / Total detections")
    col3.metric("Recall", f"{metrics['recall']:.0%}", help="Correct detections / Total expected")
    col4.metric("F1 Score", f"{metrics['f1']:.0%}", help="Harmonic mean of precision and recall")
    
    # Display metrics - Row 2
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("True Positives", metrics['true_positives'])
    col2.metric("False Positives", metrics['false_positives'])
    col3.metric("Missed", metrics['missed'])
    col4.metric("Errors", len(errors))
    
    # Breakdown tabs
    st.markdown("---")
    st.markdown("## 🔍 Detailed Breakdown")
    
    tab1, tab2, tab3, tab4 = st.tabs(["By Saboteur", "By Result", "Edge Cases", "All Results"])
    
    with tab1:
        st.markdown("### Accuracy by Primary Saboteur")
        
        for saboteur in ["parrot", "peacock", "octopus", "golden_retriever", "rabbit"]:
            saboteur_results = [r for r in successful if r["expected_primary"] == saboteur]
            if saboteur_results:
                correct = sum(1 for r in saboteur_results if r["primary_correct"])
                emoji = {"parrot": "🦜", "peacock": "🦚", "octopus": "🐙", 
                         "golden_retriever": "🐕", "rabbit": "🐇"}[saboteur]
                
                with st.expander(f"{emoji} **{saboteur.replace('_', ' ').title()}**: {correct}/{len(saboteur_results)} correct"):
                    for r in saboteur_results:
                        status_icon = "✅" if r["primary_correct"] else "❌"
                        st.markdown(f"**{r['id']}** {status_icon}")
                        st.caption(f"Detected: {r['detected'] or 'None'}")
                        if r["false_positives"]:
                            st.caption(f"⚠️ False positives: {r['false_positives']}")
                        st.markdown(f"*\"{r['text'][:100]}...\"*")
                        st.markdown("---")
    
    with tab2:
        st.markdown("### Results by Outcome")
        
        # Correct
        correct_results = [r for r in successful if r["primary_correct"] and not r["false_positives"]]
        with st.expander(f"✅ **Fully Correct** ({len(correct_results)})"):
            for r in correct_results:
                st.markdown(f"**{r['id']}**: {r['detected'] or 'None (correct for edge case)'}")
        
        # Correct primary but with false positives
        partial_results = [r for r in successful if r["primary_correct"] and r["false_positives"]]
        with st.expander(f"⚠️ **Correct Primary + False Positives** ({len(partial_results)})"):
            for r in partial_results:
                st.markdown(f"**{r['id']}**: Detected {r['detected']}")
                st.caption(f"False positives: {r['false_positives']}")
        
        # Incorrect
        incorrect_results = [r for r in successful if not r["primary_correct"]]
        with st.expander(f"❌ **Incorrect Primary** ({len(incorrect_results)})"):
            for r in incorrect_results:
                st.markdown(f"**{r['id']}**")
                st.markdown(f"Expected: **{r['expected_primary']}** | Detected: **{r['detected']}**")
                st.caption(f"*\"{r['text'][:150]}...\"*")
                st.markdown("---")
    
    with tab3:
        st.markdown("### Edge Cases (No Saboteur Expected)")
        st.caption("These test whether the model correctly identifies when NO saboteur is present.")
        
        edge_results = [r for r in successful if r["expected_primary"] is None]
        for r in edge_results:
            status_icon = "✅" if r["primary_correct"] else "❌"
            with st.expander(f"{status_icon} **{r['id']}**"):
                st.markdown(f"*\"{r['text']}\"*")
                if r["detected"]:
                    st.warning(f"Incorrectly detected: {r['detected']}")
                else:
                    st.success("Correctly identified as no clear saboteur")
                st.caption(f"Notes: {r['notes']}")
    
    with tab4:
        st.markdown("### All Results")
        
        for r in results:
            if "error" in r:
                st.error(f"**{r['id']}**: {r['error']}")
            else:
                status_icon = "✅" if r["primary_correct"] else "❌"
                with st.expander(f"{status_icon} **{r['id']}** — Expected: {r['expected_primary'] or 'None'}, Got: {r['detected'] or 'None'}"):
                    st.markdown(f"**Input:** *\"{r['text']}\"*")
                    st.markdown(f"**Expected primary:** {r['expected_primary'] or 'None'}")
                    st.markdown(f"**Expected secondary:** {r['expected_secondary'] or 'None'}")
                    st.markdown(f"**Detected:** {r['detected'] or 'None'}")
                    if r["false_positives"]:
                        st.warning(f"False positives: {r['false_positives']}")
                    if r["missed"]:
                        st.warning(f"Missed: {r['missed']}")
                    st.markdown("---")
                    st.markdown("**Full Response:**")
                    st.markdown(r["response"])


# --- Main App ---
def main():
    # Render sidebar (navigation + quick reference only)
    render_sidebar()
    
    # Route to special pages
    if st.session_state.show_about:
        render_about_page()
        return
    
    if st.session_state.show_eval:
        render_eval_page()
        return
    
    if st.session_state.show_data:
        render_data_management_page()
        return
    
    # Main coaching flow - step by step
    render_main_flow()


def render_main_flow():
    """
    Main coaching flow with clear steps:
    1. Select context (5 options)
    2. Describe your situation
    3. Choose model (with inline API key setup)
    4. View results
    5. Stats + Feedback
    """
    
    # Progress indicator
    steps = ["1️⃣ Context", "2️⃣ Describe", "3️⃣ Model", "4️⃣ Results"]
    current_step = st.session_state.step
    
    step_map = {
        "select_context": 0,
        "journal": 1,
        "choose_model": 2,
        "results": 3
    }
    current_idx = step_map.get(current_step, 0)
    
    # Show progress bar
    st.progress((current_idx + 1) / len(steps))
    st.caption(f"Step {current_idx + 1} of {len(steps)}: {steps[current_idx]}")
    
    st.markdown("---")
    
    # STEP 1: Select Context
    if current_step == "select_context":
        render_step_1_context()
    
    # STEP 2: Describe Situation
    elif current_step == "journal":
        render_step_2_describe()
    
    # STEP 3: Choose Model
    elif current_step == "choose_model":
        render_step_3_model()
    
    # STEP 4: Results (includes stats + feedback)
    elif current_step == "results":
        render_step_4_results()


def render_step_1_context():
    """Step 1: Select what you need help with."""
    
    # App title and intro
    st.markdown("# 🎯 Nare")
    st.markdown("*The Narrative Reframer — spot the stories holding you back*")
    
    # Privacy notice - accurate about what we do
    st.success("""
    🔒 **This is a safe space. Your reflections stay private.**
    
    Coaching works best when you can be completely honest — so we built privacy into the core of this app:
    
    **Using Claude API?** Your words go directly from your browser to Anthropic using *your* API key. We (the app developers) never see, store, or have access to what you write.
    
    **Using Ollama?** Even better — everything runs 100% on your machine. Your reflections never leave your device.
    
    **Local data only.** Usage stats, feedback, and logs are stored on *your* device — never sent anywhere. You can view, export, or delete this data anytime in the Data tab.
    """)
    
    st.markdown("---")
    st.markdown("## What do you need help with?")
    st.markdown("")
    
    for key, ctx in CONTEXTS.items():
        col1, col2 = st.columns([1, 10])
        with col1:
            st.markdown(f"### {ctx['icon']}")
        with col2:
            if st.button(f"**{ctx['label']}**", key=f"ctx_{key}", use_container_width=True):
                st.session_state.context = key
                st.session_state.step = "journal"
                st.session_state.user_input = ""
                st.rerun()
            st.caption(ctx['intro'])
        st.markdown("")


def render_step_2_describe():
    """Step 2: Describe your situation with pre-filled example."""
    ctx = CONTEXTS[st.session_state.context]
    
    # Back button
    if st.button("← Back to context selection"):
        st.session_state.step = "select_context"
        st.session_state.user_input = ""  # Clear when going back
        st.rerun()
    
    st.markdown(f"## {ctx['icon']} {ctx['label']}")
    st.markdown(ctx['intro'])
    st.markdown("")
    
    st.markdown(f"**{ctx['prompt']}**")
    st.markdown("")
    
    # Pre-fill with sample text if empty
    if not st.session_state.user_input:
        st.session_state.user_input = SAMPLE_TEXTS.get(st.session_state.context, "")
    
    st.caption("Edit the example below or write your own:")
    
    # Journal entry with pre-filled example
    user_input = st.text_area(
        "Your thoughts",
        value=st.session_state.user_input,
        height=200,
        label_visibility="collapsed",
        key="journal_input_step2"
    )
    st.session_state.user_input = user_input
    
    # PII detection
    if user_input.strip():
        detected_pii = detect_pii(user_input)
        show_pii_warning(detected_pii)
    
    st.markdown("")
    
    if st.button("Continue →", type="primary", use_container_width=True, disabled=not user_input.strip()):
        st.session_state.step = "choose_model"
        st.rerun()


def render_step_3_model():
    """Step 3: Choose which model to use."""
    ctx = CONTEXTS[st.session_state.context]
    user_input = st.session_state.user_input
    
    # Back button
    if st.button("← Back to edit"):
        st.session_state.step = "journal"
        st.rerun()
    
    st.markdown("## Choose your AI model")
    st.markdown("")
    
    # Check what's available
    ollama_available, ollama_models = check_ollama_available()
    has_api_key = bool(st.session_state.api_key)
    
    # Show preview of what they wrote
    with st.expander("📝 Your entry", expanded=False):
        st.markdown(user_input)
    
    # Calculate and show token estimates
    user_tokens = len(user_input) // 4
    system_tokens = 500  # Approximate system prompt size
    use_rag = st.session_state.get("use_rag", True)
    rag_tokens = 300 if use_rag else 0
    estimated_output = 400  # Typical response size
    estimated_total = user_tokens + system_tokens + rag_tokens + estimated_output
    estimated_cost = ((user_tokens + system_tokens + rag_tokens) / 1_000_000) * 3.00 + (estimated_output / 1_000_000) * 15.00
    
    # Store estimates for later comparison
    st.session_state.estimated_tokens = {
        "user": user_tokens,
        "system": system_tokens,
        "rag": rag_tokens,
        "output": estimated_output,
        "total": estimated_total,
        "cost": estimated_cost
    }
    
    st.caption(f"💰 Estimated cost: **${estimated_cost:.4f}** · {estimated_total:,} tokens")
    st.markdown("")
    
    # Model options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ☁️ Claude API")
        st.caption("Best quality · ~$0.01/query")
        
        if has_api_key:
            st.success("✅ API key configured")
            if st.button("Use Claude", key="use_claude", type="primary", use_container_width=True):
                st.session_state.selected_model = "claude"
                st.session_state.step = "results"
                st.rerun()
        else:
            # Inline API key setup
            st.warning("API key required")
            
            with st.expander("🔑 Get API Key (2 min)", expanded=True):
                st.markdown("""
                1. Go to [console.anthropic.com](https://console.anthropic.com)
                2. Sign in or create account
                3. Click **Settings** → **API Keys**
                4. Click **Create Key**
                5. Paste below:
                """)
                
                new_key = st.text_input(
                    "API Key",
                    type="password",
                    placeholder="sk-ant-api03-...",
                    key="step3_api_key",
                    label_visibility="collapsed"
                )
                
                if new_key:
                    if new_key.startswith("sk-ant-"):
                        st.session_state.api_key = new_key
                        record_audit_event("api_key_added", {"method": "step3"})
                        st.success("✅ Saved!")
                        st.rerun()
                    else:
                        st.error("Should start with sk-ant-")
                
                st.caption("💡 May need to add billing first")
    
    with col2:
        st.markdown("### 🏠 Ollama (Local)")
        st.caption("Free · Private · Runs on your machine")
        
        if ollama_available:
            st.success(f"✅ {ollama_models[0]} ready")
            if st.button("Use Ollama", key="use_ollama", type="primary", use_container_width=True):
                st.session_state.selected_model = "ollama"
                st.session_state.selected_ollama_model = ollama_models[0]
                st.session_state.step = "results"
                st.rerun()
        else:
            st.warning("Not detected")
            with st.expander("How to install"):
                st.markdown("""
                1. Install [Ollama](https://ollama.ai)
                2. Run: `ollama pull llama3.1:8b`
                3. Run: `ollama serve`
                4. Refresh this page
                """)
    
    with col3:
        st.markdown("### ⚖️ Compare Both")
        st.caption("See both side-by-side")
        
        if has_api_key and ollama_available:
            st.success("✅ Both available")
            if st.button("Compare", key="use_compare", type="primary", use_container_width=True):
                st.session_state.selected_model = "compare"
                st.session_state.selected_ollama_model = ollama_models[0]
                st.session_state.step = "results"
                st.rerun()
        else:
            missing = []
            if not has_api_key:
                missing.append("Claude API key")
            if not ollama_available:
                missing.append("Ollama")
            st.info(f"Need: {', '.join(missing)}")
    
    st.markdown("---")
    
    # RAG option
    use_rag = st.checkbox("🔍 Use RAG grounding (recommended)", value=True, 
                          help="Ground responses in the saboteur framework for better accuracy")
    st.session_state.use_rag = use_rag


def render_step_4_results():
    """Step 4: Show results with stats and feedback."""
    ctx = CONTEXTS[st.session_state.context]
    user_input = st.session_state.user_input
    selected_model = st.session_state.get("selected_model", "claude")
    use_rag = st.session_state.get("use_rag", True)
    
    # Start over button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 Start Over"):
            # Clear all flow state
            st.session_state.step = "select_context"
            st.session_state.context = None
            st.session_state.user_input = ""
            st.session_state.response = None
            st.session_state.selected_model = None
            st.session_state.current_response = None
            st.session_state.current_response_model = None
            st.session_state.current_stats = None
            st.session_state.compare_claude_response = None
            st.session_state.compare_ollama_response = None
            st.session_state.compare_voted = False
            st.session_state.conversation_history = []  # Clear multi-turn history
            st.session_state.follow_up_mode = False
            st.session_state.regenerating = False
            st.rerun()
    
    st.markdown(f"## {ctx['icon']} The Grounded PM responds...")
    st.markdown("")
    
    # Generate response based on selected model
    if selected_model == "claude":
        render_claude_response(user_input, use_rag)
    elif selected_model == "ollama":
        render_ollama_response(user_input, use_rag)
    elif selected_model == "compare":
        render_compare_response(user_input, use_rag)


def render_claude_response(user_input: str, use_rag: bool):
    """Render Claude API response with stats, feedback, regenerate, and multi-turn."""
    api_key = st.session_state.api_key
    
    # Check rate limit before generating
    rate_ok, rate_msg = check_rate_limit()
    if not rate_ok:
        st.error(f"⏱️ {rate_msg}")
        return
    
    # Check if we already have a response cached in session (and not regenerating)
    if (st.session_state.get("current_response") and 
        st.session_state.get("current_response_model") == "claude" and
        not st.session_state.get("regenerating")):
        response = st.session_state.current_response
        stats = st.session_state.current_stats
        st.markdown(response)
    else:
        # Clear regenerating flag
        st.session_state.regenerating = False
        
        # Record request for rate limiting
        record_request()
        
        # Generate new response with streaming
        response_placeholder = st.empty()
        full_response = ""
        stats = None
        
        try:
            # Build conversation history for multi-turn
            conversation = st.session_state.conversation_history.copy()
            
            for chunk, usage_info in call_anthropic_streaming(
                api_key,
                st.session_state.context,
                user_input,
                use_rag=use_rag,
                conversation_history=conversation if conversation else None
            ):
                if chunk:
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                if usage_info:
                    stats = usage_info
            
            response_placeholder.markdown(full_response)
            
            # Cache response
            st.session_state.current_response = full_response
            st.session_state.current_response_model = "claude"
            st.session_state.current_stats = stats
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_input,
            })
            st.session_state.conversation_history.append({
                "role": "assistant", 
                "content": full_response,
                "stats": stats,
            })
            
            # Record cost
            record_cost(stats['cost'])
            
            # Log interaction
            log_interaction("response", {
                "context": st.session_state.context,
                "input": user_input,
                "output": full_response,
                "backend": "claude",
                "cost": stats.get('cost', 0),
                "latency": stats.get('time', 0),
                "turn": len([h for h in st.session_state.conversation_history if h['role'] == 'user']),
            }, include_content=True)
            
            record_audit_event("query", {
                "context": st.session_state.context,
                "backend": "claude",
                "input_length": len(user_input),
                "output_length": len(full_response),
                "cost": stats.get('cost', 0),
                "turn": len([h for h in st.session_state.conversation_history if h['role'] == 'user']),
            })
            
            response = full_response
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return
    
    # Stats section
    st.markdown("---")
    st.markdown("### 📊 Response Stats")
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⏱️ Time", f"{stats['time']:.1f}s")
        col2.metric("💰 Cost", f"${stats['cost']:.4f}")
        col3.metric("📥 Input", f"{stats['input_tokens']:,}")
        col4.metric("📤 Output", f"{stats['output_tokens']:,}")
        
        if stats.get('rag_used'):
            st.caption("🔍 RAG grounding was used")
        
        # Show comparison table if we have estimates
        estimated = st.session_state.get("estimated_tokens")
        if estimated:
            st.markdown("")
            st.markdown("**Estimated vs Actual:**")
            render_token_stats_table(stats, estimated, show_input_output=True)
    
    # Action buttons: Regenerate
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Regenerate", help="Get a different response"):
            st.session_state.regenerating = True
            st.session_state.current_response = None
            st.session_state.current_stats = None
            # Remove last assistant response from history
            if st.session_state.conversation_history and st.session_state.conversation_history[-1]['role'] == 'assistant':
                st.session_state.conversation_history.pop()
            if st.session_state.conversation_history and st.session_state.conversation_history[-1]['role'] == 'user':
                st.session_state.conversation_history.pop()
            st.rerun()
    
    with col2:
        # Show conversation turn count
        turns = len([h for h in st.session_state.conversation_history if h['role'] == 'user'])
        if turns > 0:
            st.caption(f"💬 Turn {turns}")
    
    # Feedback section
    render_feedback_section("claude", user_input, response)
    
    # Multi-turn: Follow-up question
    render_follow_up_section("claude")


def render_follow_up_section(backend: str):
    """Render follow-up question input for multi-turn conversation."""
    st.markdown("---")
    st.markdown("### 💬 Continue the conversation")
    
    follow_up = st.text_input(
        "Ask a follow-up question",
        placeholder="Tell me more about... / What if... / How do I...",
        key=f"follow_up_{backend}",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Send follow-up", type="primary", disabled=not follow_up.strip()):
            if follow_up.strip():
                # Update user input and clear current response to trigger new generation
                st.session_state.user_input = follow_up
                st.session_state.current_response = None
                st.session_state.current_stats = None
                st.session_state.follow_up_mode = True
                st.rerun()
    
    # Show conversation history
    if len(st.session_state.conversation_history) > 2:
        with st.expander(f"📜 Conversation history ({len(st.session_state.conversation_history) // 2} exchanges)", expanded=False):
            for i, entry in enumerate(st.session_state.conversation_history):
                if entry['role'] == 'user':
                    st.markdown(f"**You:** {entry['content'][:200]}{'...' if len(entry['content']) > 200 else ''}")
                else:
                    st.markdown(f"**Nare:** {entry['content'][:200]}{'...' if len(entry['content']) > 200 else ''}")
                    if entry.get('stats'):
                        st.caption(f"💰 ${entry['stats'].get('cost', 0):.4f}")


def render_ollama_response(user_input: str, use_rag: bool):
    """Render Ollama response with stats, feedback, regenerate, and multi-turn."""
    model = st.session_state.get("selected_ollama_model", "llama3.1:8b")
    
    # Check cache (and not regenerating)
    if (st.session_state.get("current_response") and 
        st.session_state.get("current_response_model") == "ollama" and
        not st.session_state.get("regenerating")):
        response = st.session_state.current_response
        stats = st.session_state.current_stats
        st.markdown(response)
    else:
        # Clear regenerating flag
        st.session_state.regenerating = False
        
        with st.spinner(f"Asking {model}..."):
            try:
                response, stats = call_ollama(
                    model,
                    st.session_state.context,
                    user_input,
                    use_rag=use_rag
                )
                
                st.markdown(response)
                
                # Cache
                st.session_state.current_response = response
                st.session_state.current_response_model = "ollama"
                st.session_state.current_stats = stats
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "role": "user",
                    "content": user_input,
                })
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": response,
                    "stats": stats,
                })
                
                # Log
                log_interaction("response", {
                    "context": st.session_state.context,
                    "input": user_input,
                    "output": response,
                    "backend": "ollama",
                    "cost": 0,
                    "latency": stats.get('time', 0),
                    "turn": len([h for h in st.session_state.conversation_history if h['role'] == 'user']),
                }, include_content=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                return
    
    # Stats section
    st.markdown("---")
    st.markdown("### 📊 Response Stats")
    
    if stats:
        col1, col2 = st.columns(2)
        col1.metric("⏱️ Time", f"{stats['time']:.1f}s")
        col2.metric("💰 Cost", "Free")
        
        if stats.get('rag_used'):
            st.caption("🔍 RAG grounding was used")
    
    # Action buttons: Regenerate
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Regenerate", key="regen_ollama", help="Get a different response"):
            st.session_state.regenerating = True
            st.session_state.current_response = None
            st.session_state.current_stats = None
            # Remove last exchange from history
            if st.session_state.conversation_history and st.session_state.conversation_history[-1]['role'] == 'assistant':
                st.session_state.conversation_history.pop()
            if st.session_state.conversation_history and st.session_state.conversation_history[-1]['role'] == 'user':
                st.session_state.conversation_history.pop()
            st.rerun()
    
    with col2:
        turns = len([h for h in st.session_state.conversation_history if h['role'] == 'user'])
        if turns > 0:
            st.caption(f"💬 Turn {turns}")
    
    # Feedback
    render_feedback_section("ollama", user_input, response)
    
    # Multi-turn: Follow-up question
    render_follow_up_section("ollama")


def render_compare_response(user_input: str, use_rag: bool):
    """Render side-by-side comparison with voting."""
    api_key = st.session_state.api_key
    ollama_model = st.session_state.get("selected_ollama_model", "llama3.1:8b")
    
    col1, col2 = st.columns(2)
    
    # Claude response
    with col1:
        st.markdown("### ☁️ Claude")
        
        if st.session_state.get("compare_claude_response"):
            st.markdown(st.session_state.compare_claude_response)
            stats = st.session_state.compare_claude_stats
        else:
            response_placeholder = st.empty()
            full_response = ""
            stats = None
            
            try:
                for chunk, usage_info in call_anthropic_streaming(
                    api_key,
                    st.session_state.context,
                    user_input,
                    use_rag=use_rag
                ):
                    if chunk:
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                    if usage_info:
                        stats = usage_info
                
                response_placeholder.markdown(full_response)
                st.session_state.compare_claude_response = full_response
                st.session_state.compare_claude_stats = stats
                record_cost(stats['cost'])
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        if stats:
            st.caption(f"⏱️ {stats['time']:.1f}s · 💰 ${stats['cost']:.4f}")
    
    # Ollama response
    with col2:
        st.markdown(f"### 🏠 {ollama_model}")
        
        if st.session_state.get("compare_ollama_response"):
            st.markdown(st.session_state.compare_ollama_response)
            stats = st.session_state.compare_ollama_stats
        else:
            with st.spinner("Generating..."):
                try:
                    response, stats = call_ollama(
                        ollama_model,
                        st.session_state.context,
                        user_input,
                        use_rag=use_rag
                    )
                    st.markdown(response)
                    st.session_state.compare_ollama_response = response
                    st.session_state.compare_ollama_stats = stats
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if stats:
            st.caption(f"⏱️ {stats['time']:.1f}s · 💰 Free")
    
    # Voting section
    st.markdown("---")
    st.markdown("### 🗳️ Which response was more helpful?")
    
    if not st.session_state.get("compare_voted"):
        vote_col1, vote_col2, vote_col3 = st.columns(3)
        
        with vote_col1:
            if st.button("☁️ Claude was better", use_container_width=True):
                record_preference("claude", st.session_state.context)
                st.session_state.compare_voted = True
                st.rerun()
        
        with vote_col2:
            if st.button("🤝 About equal", use_container_width=True):
                st.session_state.compare_voted = True
                st.rerun()
        
        with vote_col3:
            if st.button("🏠 Ollama was better", use_container_width=True):
                record_preference("llama", st.session_state.context)
                st.session_state.compare_voted = True
                st.rerun()
    else:
        st.success("Thanks for voting!")


def render_feedback_section(backend: str, user_input: str, response: str):
    """Render feedback buttons."""
    st.markdown("---")
    st.markdown("### Was this helpful?")
    
    feedback_key = f"feedback_{backend}_{hash(user_input)}"
    
    if not st.session_state.get(feedback_key):
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("👍 Yes", key=f"thumbs_up_{backend}"):
                record_feedback("up", st.session_state.context, user_input, response, backend)
                st.session_state[feedback_key] = "up"
                st.rerun()
        
        with col2:
            if st.button("👎 No", key=f"thumbs_down_{backend}"):
                record_feedback("down", st.session_state.context, user_input, response, backend)
                st.session_state[feedback_key] = "down"
                st.rerun()
    else:
        if st.session_state[feedback_key] == "up":
            st.success("Thanks for the feedback! 👍")
        else:
            st.info("Thanks — we'll use this to improve.")


if __name__ == "__main__":
    main()
