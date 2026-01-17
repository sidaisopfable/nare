# PM Saboteurs Golden Dataset
# Human-labeled examples for evaluation

"""
Each entry has:
- id: Unique identifier
- context: Which entry point (setback, decision, procrastinating, imposter, overwhelmed)
- text: The journal entry
- primary_saboteur: The MAIN saboteur (required)
- secondary_saboteurs: Other saboteurs present (optional, can be empty)
- notes: Why this labeling (for documentation)

Labeling guidelines:
- Primary saboteur = the dominant pattern driving the behavior
- Secondary = clearly present but not the main driver
- If unsure, leave secondary empty
- Edge cases (healthy responses, external factors) have primary_saboteur = None
"""

GOLDEN_DATASET = [
    # === PARROT (Inner Critic) ===
    {
        "id": "parrot_01",
        "context": "setback",
        "text": "I didn't get the job. The recruiter said they went with someone with more 'technical depth.' I've been a PM for 6 years but I keep hitting this wall. Maybe I'm just not cut out for these senior roles.",
        "primary_saboteur": "parrot",
        "secondary_saboteurs": [],
        "notes": "Classic Parrot - 'not cut out for' is self-doubt, not metrics-focused"
    },
    {
        "id": "parrot_02",
        "context": "imposter",
        "text": "Started at a new company two weeks ago and I'm drowning. Everyone speaks in acronyms I don't understand. My manager keeps saying 'you'll pick it up' but I'm not so sure. I think they made a hiring mistake.",
        "primary_saboteur": "parrot",
        "secondary_saboteurs": [],
        "notes": "'Hiring mistake' = core Parrot belief that you don't belong"
    },
    {
        "id": "parrot_03",
        "context": "imposter",
        "text": "An engineer challenged my prioritization decision in front of the whole team today. I defended it but honestly I wasn't sure I was right. Now I keep second-guessing myself. Do I actually know what I'm doing?",
        "primary_saboteur": "parrot",
        "secondary_saboteurs": [],
        "notes": "Self-doubt after being challenged, questioning competence"
    },
    {
        "id": "parrot_04",
        "context": "procrastinating",
        "text": "I need to present the technical architecture decision but I keep pushing it. I've reviewed the options 20 times. Made extra slides. I just need a bit more information before I can be confident.",
        "primary_saboteur": "parrot",
        "secondary_saboteurs": ["octopus"],
        "notes": "Root cause is self-doubt ('not confident'), behavior manifests as over-preparation (Octopus-like control)."
    },
    {
        "id": "parrot_05",
        "context": "setback",
        "text": "I got critical feedback in my perf review. My manager said I need to be more 'strategic.' I thought I was doing well. Clearly I can't even accurately assess my own performance. What else am I wrong about?",
        "primary_saboteur": "parrot",
        "secondary_saboteurs": [],
        "notes": "Spiraling self-doubt from feedback, questioning all self-assessment"
    },
    {
        "id": "parrot_06",
        "context": "decision",
        "text": "I need to make a call on this vendor but what if I pick wrong? Last time I made a big decision like this it didn't go well. I don't trust my judgment on these things anymore.",
        "primary_saboteur": "parrot",
        "secondary_saboteurs": [],
        "notes": "Past failure has undermined confidence in decision-making ability"
    },
    
    # === PEACOCK (Metrics Obsessed / Achievement-Based Worth) ===
    {
        "id": "peacock_01",
        "context": "setback",
        "text": "Our Q3 launch completely missed targets — we hit 45% of the projected adoption. My skip-level asked what happened. Now I'm dreading the performance review. I should be further along in my career by now.",
        "primary_saboteur": "peacock",
        "secondary_saboteurs": [],
        "notes": "Focus on metrics, career progression, comparing to expectations"
    },
    {
        "id": "peacock_02",
        "context": "setback",
        "text": "Got passed over for the promotion again. They gave it to someone who's been here half as long as me. I need to find something more impressive to work on or I'll never catch up.",
        "primary_saboteur": "peacock",
        "secondary_saboteurs": [],
        "notes": "Worth = achievements. 'Impressive work' is about proving value, not escaping boredom."
    },
    {
        "id": "peacock_03",
        "context": "imposter",
        "text": "I just got promoted to Group PM but I feel like I need to prove I deserve it. In meetings with other GPMs they have such impressive track records. I need a big win fast.",
        "primary_saboteur": "peacock",
        "secondary_saboteurs": ["parrot"],
        "notes": "Primary: need to prove via wins. Secondary: comparison to others"
    },
    {
        "id": "peacock_04",
        "context": "overwhelmed",
        "text": "I've been refreshing LinkedIn all week watching people announce their promotions and new roles. Meanwhile I'm stuck on maintenance work that no one will ever notice. My career is stalling while everyone else moves up.",
        "primary_saboteur": "peacock",
        "secondary_saboteurs": [],
        "notes": "Social comparison, career anxiety, worth tied to visible achievements"
    },
    {
        "id": "peacock_05",
        "context": "procrastinating",
        "text": "I should be working on the roadmap but I keep checking our feature usage dashboards. If the numbers don't improve by EOQ my review is going to be rough. I need to find a way to show more impact.",
        "primary_saboteur": "peacock",
        "secondary_saboteurs": [],
        "notes": "Obsessing over metrics, self-worth tied to numbers"
    },
    
    # === OCTOPUS (Can't Let Go / Control) ===
    {
        "id": "octopus_01",
        "context": "decision",
        "text": "I can't decide whether to let the team run with their approach or step in. They want to build it one way but I've been burned before. I need to review their designs before they start coding. What if they miss something?",
        "primary_saboteur": "octopus",
        "secondary_saboteurs": [],
        "notes": "Classic Octopus - can't delegate, fear of mistakes, need to review everything"
    },
    {
        "id": "octopus_02",
        "context": "overwhelmed",
        "text": "There's too much happening and I don't trust that it's being handled. I'm in every standup, every design review. My team keeps asking why I need to be in everything but last time I stepped back, we had an outage.",
        "primary_saboteur": "octopus",
        "secondary_saboteurs": [],
        "notes": "Overwhelmed BY control, not by saying yes. Past trauma justifies control."
    },
    {
        "id": "octopus_03",
        "context": "decision",
        "text": "My designer presented three options but I'm not satisfied with any of them. I ended up spending the weekend creating my own mockups. I know I should trust her expertise but I can't ship something I haven't fully thought through myself.",
        "primary_saboteur": "octopus",
        "secondary_saboteurs": [],
        "notes": "Can't delegate creative decisions, needs personal control over output."
    },
    {
        "id": "octopus_04",
        "context": "procrastinating",
        "text": "I was supposed to hand off the feature to the new PM but I keep finding reasons to stay involved. The launch is in 2 weeks and I don't think they understand all the edge cases. I'll just do a few more reviews to make sure it's right.",
        "primary_saboteur": "octopus",
        "secondary_saboteurs": [],
        "notes": "Can't let go of ownership, difficulty with handoffs"
    },
    {
        "id": "octopus_05",
        "context": "setback",
        "text": "The feature launched with a bug because I wasn't in the final review meeting. I knew I should have been there. From now on I'm not letting anything ship without my sign-off, even if it slows us down.",
        "primary_saboteur": "octopus",
        "secondary_saboteurs": [],
        "notes": "Setback reinforces need for control, doubling down on oversight"
    },
    
    # === GOLDEN RETRIEVER (Can't Say No / People Pleasing) ===
    {
        "id": "golden_retriever_01",
        "context": "overwhelmed",
        "text": "I have 6 stakeholders who all think their thing is the priority. I said I'd look into all of them. Sales needs a feature. Customer success has escalations. The exec has a pet project. I can't say no — they're all important.",
        "primary_saboteur": "golden_retriever",
        "secondary_saboteurs": [],
        "notes": "Classic Golden Retriever - said yes to everyone, now drowning"
    },
    {
        "id": "golden_retriever_02",
        "context": "decision",
        "text": "Should I push back on the exec's feature request or just find a way to fit it in? My roadmap is already packed because I said yes to three other stakeholders. If I push back people might think I'm not collaborative.",
        "primary_saboteur": "golden_retriever",
        "secondary_saboteurs": [],
        "notes": "Fear of being seen as 'not collaborative' is core Golden Retriever"
    },
    {
        "id": "golden_retriever_03",
        "context": "overwhelmed",
        "text": "I've got too much on my plate but somehow I just agreed to mentor a new PM and join a cross-functional initiative. I should be able to say no but they asked so nicely and it felt important to them.",
        "primary_saboteur": "golden_retriever",
        "secondary_saboteurs": [],
        "notes": "Can't say no even when already overwhelmed"
    },
    {
        "id": "golden_retriever_04",
        "context": "setback",
        "text": "I worked all weekend to get that customer's request in, and now they've changed their mind. I should have pushed back but they seemed so desperate. Now my team is frustrated because we bumped other priorities for nothing.",
        "primary_saboteur": "golden_retriever",
        "secondary_saboteurs": [],
        "notes": "Over-accommodated, now dealing with consequences"
    },
    {
        "id": "golden_retriever_05",
        "context": "decision",
        "text": "The engineering lead and the design lead want different things. I've been trying to find a compromise that makes everyone happy but nothing works. I hate conflict and I just want everyone to feel heard.",
        "primary_saboteur": "golden_retriever",
        "secondary_saboteurs": [],
        "notes": "Conflict avoidance, trying to please all parties"
    },
    
    # === RABBIT (Shiny Object / Escape) ===
    {
        "id": "rabbit_01",
        "context": "decision",
        "text": "I'm trying to decide whether to stay on my current product or move to the new AI initiative. My current thing is fine but it's all optimization now, nothing exciting. The AI team is doing 0-to-1 work. I've been here 14 months and I'm getting bored.",
        "primary_saboteur": "rabbit",
        "secondary_saboteurs": [],
        "notes": "Classic Rabbit - bored with current, attracted to shiny new thing"
    },
    {
        "id": "rabbit_02",
        "context": "procrastinating",
        "text": "I have a PRD due tomorrow and I haven't started. Every time I open the doc I find something else to do — reorganized my task list, read articles about AI strategy, started outlining a proposal for a new initiative. The PRD is boring.",
        "primary_saboteur": "rabbit",
        "secondary_saboteurs": [],
        "notes": "Escaping boring work into shiny distractions"
    },
    {
        "id": "rabbit_03",
        "context": "setback",
        "text": "Got passed over for the senior role. Part of me thinks I should just start interviewing elsewhere — fresh start, no one knows my failures. Maybe a new company would be more exciting anyway.",
        "primary_saboteur": "rabbit",
        "secondary_saboteurs": ["parrot"],
        "notes": "Primary: escape to new context. Secondary: 'my failures' is Parrot"
    },
    {
        "id": "rabbit_04",
        "context": "decision",
        "text": "My manager wants me to commit to this product for another year but I keep thinking about the startup my friend is joining. It's risky but they're working on something genuinely new. I'm tired of iterating on the same features.",
        "primary_saboteur": "rabbit",
        "secondary_saboteurs": [],
        "notes": "Grass-is-greener thinking, difficulty committing"
    },
    {
        "id": "rabbit_05",
        "context": "overwhelmed",
        "text": "Everything feels like a slog right now. I keep fantasizing about quitting and traveling for a few months. Or maybe going back to school. Anything but these endless stakeholder meetings about incremental improvements.",
        "primary_saboteur": "rabbit",
        "secondary_saboteurs": [],
        "notes": "Escape fantasy when present moment feels hard"
    },
    
    # === MIXED / SUBTLE (multiple saboteurs, one primary) ===
    {
        "id": "mixed_01",
        "context": "imposter",
        "text": "Got promoted to Group PM but I feel like a fraud. I look at other GPMs and they seem so strategic. I've just been grinding on execution. Maybe I should take on something more visible to prove I belong.",
        "primary_saboteur": "parrot",
        "secondary_saboteurs": ["peacock"],
        "notes": "Primary: 'fraud/not belonging' is core Parrot. Secondary: 'prove via visible work' is Peacock (achievement), not Rabbit (escape)."
    },
    {
        "id": "mixed_02",
        "context": "overwhelmed",
        "text": "I've got too much on my plate but somehow I just agreed to mentor a new PM. I keep thinking maybe I should switch to a smaller company where I can actually focus. I should be able to handle this — other PMs seem fine.",
        "primary_saboteur": "golden_retriever",
        "secondary_saboteurs": ["rabbit", "parrot"],
        "notes": "Primary: can't say no. Secondary: escape fantasy (Rabbit), 'should handle it' (Parrot)"
    },
    {
        "id": "mixed_03",
        "context": "procrastinating",
        "text": "I've been avoiding the difficult stakeholder conversation for a week. I keep telling myself I need more data first, but really I'm worried they'll be upset with me. I hate confrontation.",
        "primary_saboteur": "golden_retriever",
        "secondary_saboteurs": ["octopus"],
        "notes": "Primary: conflict avoidance (GR). Secondary: 'need more data' is Octopus-like control seeking"
    },
    {
        "id": "mixed_04",
        "context": "setback",
        "text": "The launch flopped and I can't stop checking the metrics dashboard. Down another 5% today. My manager says it's not my fault but I should have caught this earlier. Maybe I should look for a role where the stakes aren't so high.",
        "primary_saboteur": "peacock",
        "secondary_saboteurs": ["parrot", "rabbit"],
        "notes": "Primary: obsessing over metrics (Peacock). Secondary: self-blame (Parrot), escape fantasy (Rabbit)"
    },
    
    # === EDGE CASES (no saboteur or healthy response) ===
    {
        "id": "edge_healthy_01",
        "context": "decision",
        "text": "Trying to decide between two good options for Q3 priorities. Both have merit, just need to pick one and commit. Going to sleep on it and decide tomorrow.",
        "primary_saboteur": None,
        "secondary_saboteurs": [],
        "notes": "Healthy decision-making, no saboteur pattern"
    },
    {
        "id": "edge_external_01",
        "context": "setback",
        "text": "Company announced layoffs and my team might be affected. Nothing I could have done differently. Just waiting to hear more.",
        "primary_saboteur": None,
        "secondary_saboteurs": [],
        "notes": "External circumstance, not a saboteur pattern"
    },
    {
        "id": "edge_minimal_01",
        "context": "procrastinating",
        "text": "Just not feeling it today.",
        "primary_saboteur": None,
        "secondary_saboteurs": [],
        "notes": "Too minimal to identify pattern"
    },
    {
        "id": "edge_healthy_02",
        "context": "overwhelmed",
        "text": "I have a lot going on but I've blocked time to prioritize tomorrow. Going to cut some things from my list — not everything is actually urgent even though it feels that way.",
        "primary_saboteur": None,
        "secondary_saboteurs": [],
        "notes": "Healthy coping: acknowledging overwhelm, planning to prioritize"
    },
    {
        "id": "edge_healthy_03",
        "context": "imposter",
        "text": "Starting a new role and there's a lot I don't know yet. That's normal — no one expects me to have all the answers in week one. I'll ask questions and learn.",
        "primary_saboteur": None,
        "secondary_saboteurs": [],
        "notes": "Healthy perspective on new role uncertainty - SOUNDS like imposter but isn't"
    },
    {
        "id": "edge_healthy_04",
        "context": "setback",
        "text": "The feature didn't perform as expected. I'm disappointed but we learned a lot. Already have ideas for the next iteration based on the data.",
        "primary_saboteur": None,
        "secondary_saboteurs": [],
        "notes": "Healthy response to failure - growth mindset, not ruminating"
    },
    {
        "id": "edge_healthy_05",
        "context": "decision",
        "text": "I've been offered a role on a new team. Taking time to think through the pros and cons carefully. Either choice has trade-offs and that's okay.",
        "primary_saboteur": None,
        "secondary_saboteurs": [],
        "notes": "Healthy deliberation - could look like Rabbit (new opportunity) but lacks escape motive"
    },
]


def get_golden_dataset():
    """Return the full golden dataset."""
    return GOLDEN_DATASET


def get_by_saboteur(saboteur: str):
    """Get all entries where this saboteur is primary."""
    return [e for e in GOLDEN_DATASET if e["primary_saboteur"] == saboteur]


def get_by_context(context: str):
    """Get all entries for a specific context."""
    return [e for e in GOLDEN_DATASET if e["context"] == context]


def get_edge_cases():
    """Get entries with no clear saboteur."""
    return [e for e in GOLDEN_DATASET if e["primary_saboteur"] is None]


def summary():
    """Print dataset summary."""
    print(f"=== GOLDEN DATASET SUMMARY ===\n")
    print(f"Total entries: {len(GOLDEN_DATASET)}\n")
    
    print("By primary saboteur:")
    for s in ["parrot", "peacock", "octopus", "golden_retriever", "rabbit", None]:
        count = len([e for e in GOLDEN_DATASET if e["primary_saboteur"] == s])
        label = s if s else "None (edge cases)"
        print(f"  {label}: {count}")
    
    print("\nBy context:")
    for c in ["setback", "decision", "procrastinating", "imposter", "overwhelmed"]:
        count = len(get_by_context(c))
        print(f"  {c}: {count}")


if __name__ == "__main__":
    summary()
