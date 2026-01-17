# 📝 LinkedIn Post — The Journey of Building Nare

**Post format:** Text + embedded video (demo)

---

## THE POST

```
I spent 2 weeks pair-programming with Claude to build an AI app from scratch.

No tutorial. No boilerplate. Just me and an LLM figuring it out together.

Here's what I learned about building GenAI products — and working with AI as a collaborator.

🎯 THE APP: Nare (pronounced "Narry" — Narrative Reframer)

An AI coach that helps PMs recognize self-sabotaging mental patterns. You describe what's going on, it identifies which "saboteur" is running the show, and responds with a grounded perspective.

The 5 saboteurs:
🦜 Parrot (inner critic)
🦚 Peacock (achievement-obsessed)
🐙 Octopus (control freak)
🐕 Golden Retriever (people pleaser)
🐇 Rabbit (escape artist)

[Video demo attached 👇]

---

🛠️ THE PROCESS:

I didn't start with a grand vision. I started with a mass of interests I wanted to learn: RAG, evals, prompt engineering, cost optimization.

Session 1 was just brainstorming with Claude: "Here's what I want to learn, here are some ideas, help me pick." We explored 5-6 directions before landing on the coaching angle — something I actually cared about, not just a tech demo.

Then I just... started building. The first version was ugly. The prompt was 52% accurate. The UI was a mess. But it worked, and that momentum carried everything.

I threw away more code than I shipped. Early features got cut. The name changed 3 times. That's the process — you can't think your way to a good product, you have to build your way there.

---

🔧 WHAT I LEARNED:

1. "Evals are everything"

My first prompt had 52% accuracy. After building a 37-example golden dataset and iterating on the prompt, I got to 89%.

You can't improve what you can't measure. Every GenAI product needs a way to know if it's actually working.

2. "RAG is simpler than you think"

I assumed retrieval-augmented generation required complex infrastructure. Turns out: sentence-transformers + ChromaDB + 6 markdown files = grounded responses that don't hallucinate.

Total infrastructure cost: $0.

3. "Streaming isn't optional"

Users thought the app was broken when responses took 3 seconds with no feedback. Adding streaming made the exact same latency feel instant. Perception > reality.

4. "Batch your feedback like you would with a human"

Early on, I gave Claude feedback one drip at a time: "fix this button," then "change that color," then "move this text."

It was slow and the results were inconsistent.

Later I learned to batch: collect 5-6 pieces of feedback, explain the full picture, let it make changes holistically. Just like you'd do in a design review with a human.

The AI worked better when I treated it like a collaborator, not a command line.

5. "The hardest bugs are in the prompt"

The model kept "hallucinating" saboteurs that weren't in the user's text. I assumed it was a code bug. Spent an hour debugging.

The fix? Adding 12 words to the prompt: "quote ONLY words that appear EXACTLY in the user's entry."

Prompt debugging is a new skill. Treat prompts like code: version them, test them, review them.

---

🏢 ENTERPRISE PATTERNS I IMPLEMENTED:

For anyone building GenAI at work, here's what I'd now consider table stakes:

✅ Golden dataset + eval dashboard
✅ Prompt versioning
✅ Rate limiting + cost caps
✅ Token counting (estimated vs actual)
✅ Request/response logging
✅ PII detection
✅ Streaming responses
✅ Multi-turn conversation with context

---

💡 THE META-LESSON:

The biggest thing I learned wasn't technical.

It was that starting beats planning. My first version was embarrassing. But each session built on the last. By the end of 2 weeks, I had something I'm genuinely proud of.

If I'd tried to design the "perfect" app upfront, I'd still be staring at a blank doc.

---

🔓 IT'S OPEN SOURCE

GitHub: [link]

If you're a PM who's ever spiraled after a rejection, or an engineer curious about GenAI patterns — take a look.

What's been your biggest learning building with LLMs?

#GenAI #ProductManagement #AI #BuildInPublic #OpenSource
```

---

## SHORTER VERSION (If character limit is tight)

```
I spent 2 weeks pair-programming with Claude to build an AI app.

No tutorial. No boilerplate. Just me and an LLM figuring it out.

The app (Nare) helps PMs recognize self-sabotaging patterns. But the real value was in the process.

What I learned:

1️⃣ Start ugly, iterate fast
First version: 52% accuracy, messy UI. By week 2: 89% accuracy, polished UX. You can't think your way to good — you build your way there.

2️⃣ Evals are everything
Built a 37-example golden dataset. Couldn't improve the prompt without a way to measure it.

3️⃣ Batch feedback like you would with a human
Drip-feeding Claude one fix at a time = slow, inconsistent. Batching 5-6 comments = faster, better results. Treat AI like a collaborator, not a command line.

4️⃣ RAG is simpler than you think
sentence-transformers + ChromaDB + markdown files. Total infra cost: $0.

5️⃣ Prompt bugs are the hardest bugs
Model hallucinated patterns. Fix wasn't code — it was 12 words in the prompt.

Demo attached 👇
Open source: [GitHub link]

What's your biggest learning building with LLMs?

#GenAI #ProductManagement #BuildInPublic
```

---

## VIDEO CAPTION

```
🎯 Nare — built in 2 weeks pair-programming with Claude

0:00 - The problem (PM mental spirals)
0:20 - The 5 saboteurs framework
0:50 - Full walkthrough
1:50 - Eval dashboard (52% → 89%)
2:20 - Privacy architecture

Open source → [GitHub link]
```

---

## POSTING STRATEGY

**Day 1: Main post**
- Post the long version with video embedded
- First comment: GitHub link + "Happy to answer questions about the build process"

**Day 3-5: Follow-up post (evals deep-dive)**
```
"My AI had a 52% accuracy problem.

Here's how I built an eval system that got it to 89%..."

[Details on golden dataset, labeling, metrics, iteration loop]
```

**Day 7-10: Follow-up post (working with AI)**
```
"The moment I started treating Claude like a colleague instead of a tool, everything changed.

Here's what I mean..."

[Details on batching feedback, explaining context, collaborative iteration]
```

**Day 14: Follow-up post (prompt engineering)**
```
"The bug that took me 3 hours to find was 12 words.

Debugging prompts is a skill no one teaches you..."

[Details on the hallucination fix, prompt versioning, treating prompts like code]
```

---

## KEY NARRATIVE BEATS

| Beat | Purpose |
|------|---------|
| "No tutorial, no boilerplate" | Establishes authenticity, relatability |
| "Started with brainstorming, not building" | Shows thoughtful process |
| "First version was ugly" | Permission for others to start imperfect |
| "Threw away more than I shipped" | Real product development |
| "Batch feedback like a human" | Novel insight, actionable |
| "Starting beats planning" | Inspiring close, call to action |

---

## ENGAGEMENT HOOKS

Questions to ask / reply with:

- "What's been your experience pair-programming with AI?"
- "Anyone else find batching feedback makes a huge difference?"
- "What would you add to the 'enterprise GenAI table stakes' list?"
- "What's the weirdest prompt bug you've encountered?"

---

## ASSETS CHECKLIST

- [ ] Demo video (2-3 min, use script from DEMO_VIDEO_SCRIPT.md)
- [ ] GitHub repo public and polished
- [ ] Screenshots in repo for link preview
- [ ] Video thumbnail with text overlay
