# PM Saboteurs Test Suite
# Synthetic journal entries for testing saboteur detection

"""
Test entries designed to:
1. Cover all 5 PM Saboteurs
2. Cover all 5 contexts
3. Range from obvious to subtle
4. Include PM-specific language and scenarios
"""

TEST_ENTRIES = {
    # --- SETBACK CONTEXT ---
    "setback_parrot_obvious": {
        "context": "setback",
        "entry": "I didn't get the job. The interviewer asked about my technical decisions and I fumbled. I'm just not technical enough to be a real PM. Everyone else in that loop probably had CS degrees. I got lucky in my current role but I can't fake it forever.",
        "expected_patterns": ["parrot"],
        "difficulty": "obvious"
    },
    
    "setback_peacock_obvious": {
        "context": "setback",
        "entry": "Our launch only hit 60% of the target. Two quarters of work and we missed. My promo packet is dead now. The PM on the other team hit 150% and everyone's celebrating them. I should be further along in my career by now.",
        "expected_patterns": ["peacock"],
        "difficulty": "obvious"
    },
    
    "setback_mixed_subtle": {
        "context": "setback",
        "entry": "Got passed over for the senior role. Part of me thinks I should just start interviewing elsewhere — fresh start, no one knows my failures. But I also wonder if I should have pushed harder on that last feature, done more launches. The feedback was vague but I keep replaying what I could have done differently.",
        "expected_patterns": ["rabbit", "peacock", "parrot"],
        "difficulty": "subtle"
    },
    
    # --- DECISION CONTEXT ---
    "decision_octopus_obvious": {
        "context": "decision",
        "entry": "I can't decide whether to let the team run with their approach or step in. They want to build it one way but I've been burned before when I wasn't in the details. I've made a doc with all the risks. I need to review their designs before they start coding. What if they miss something critical?",
        "expected_patterns": ["octopus"],
        "difficulty": "obvious"
    },
    
    "decision_rabbit_obvious": {
        "context": "decision",
        "entry": "I'm trying to decide whether to stay on my current product or move to the new AI initiative. My current thing is fine but it's all optimization now, nothing exciting. The AI team is doing 0-to-1 work. I've been here 14 months and I'm getting bored. Maybe I need a fresh challenge.",
        "expected_patterns": ["rabbit"],
        "difficulty": "obvious"
    },
    
    "decision_mixed_subtle": {
        "context": "decision",
        "entry": "Should I push back on the exec's feature request or just find a way to fit it in? My roadmap is already packed because I said yes to three other stakeholders. If I push back people might think I'm not collaborative. But if I don't, we'll ship mediocre stuff.",
        "expected_patterns": ["golden_retriever", "peacock"],
        "difficulty": "subtle"
    },
    
    # --- PROCRASTINATING CONTEXT ---
    "procrastinating_rabbit_obvious": {
        "context": "procrastinating",
        "entry": "I have this PRD due but I keep finding other things to do. I redesigned the team's Notion. Read some articles about AI strategy. Started outlining a proposal for a new initiative. The PRD is just boring — it's incremental improvements, nothing transformative.",
        "expected_patterns": ["rabbit"],
        "difficulty": "obvious"
    },
    
    "procrastinating_parrot_subtle": {
        "context": "procrastinating",
        "entry": "I need to present the technical architecture decision to eng leadership but I keep pushing it. I've reviewed the options 20 times. Made extra slides. What if they ask something I can't answer? The senior PMs seem so confident in these meetings.",
        "expected_patterns": ["parrot", "octopus"],
        "difficulty": "subtle"
    },
    
    # --- IMPOSTER CONTEXT ---
    "imposter_parrot_obvious": {
        "context": "imposter",
        "entry": "Started the new job two weeks ago and I'm drowning. Everyone uses acronyms I don't know. The eng lead asked about my experience with distributed systems and I had to admit I don't have much. I'm waiting for them to realize they made a hiring mistake.",
        "expected_patterns": ["parrot"],
        "difficulty": "obvious"
    },
    
    "imposter_mixed_subtle": {
        "context": "imposter",
        "entry": "Got promoted to Group PM but I feel like a fraud. I look at other GPMs and they seem so strategic, so confident with execs. I've just been grinding on execution. Maybe I should take on something more visible to prove I belong at this level. Or maybe I should have turned down the promo.",
        "expected_patterns": ["parrot", "peacock", "rabbit"],
        "difficulty": "subtle"
    },
    
    # --- OVERWHELMED CONTEXT ---
    "overwhelmed_golden_retriever_obvious": {
        "context": "overwhelmed",
        "entry": "I have 6 stakeholders who all think their thing is the priority. I said I'd look into all of them. Sales needs a feature for a deal. Customer success has escalations. The exec has a pet project. I'm in meetings 8 hours a day and can't think. But I can't say no — they're all important.",
        "expected_patterns": ["golden_retriever"],
        "difficulty": "obvious"
    },
    
    "overwhelmed_octopus_obvious": {
        "context": "overwhelmed",
        "entry": "There's too much happening and I don't trust that it's being handled. I'm in every standup, every design review, every stakeholder sync. I review every PR description. My team keeps asking why I need to be in everything but last time I stepped back, we had an outage.",
        "expected_patterns": ["octopus"],
        "difficulty": "obvious"
    },
    
    "overwhelmed_mixed_subtle": {
        "context": "overwhelmed",
        "entry": "I've got too much on my plate but somehow I just agreed to mentor a new PM and join a cross-functional initiative. I keep thinking maybe I should switch to a smaller company where I can actually focus. I should be able to handle this workload — other PMs seem fine.",
        "expected_patterns": ["golden_retriever", "rabbit", "parrot"],
        "difficulty": "subtle"
    },
    
    # --- EDGE CASES ---
    "edge_minimal": {
        "context": "setback",
        "entry": "Just frustrated with how things are going.",
        "expected_patterns": [],
        "difficulty": "edge"
    },
    
    "edge_healthy": {
        "context": "decision",
        "entry": "Trying to decide between two good options for Q3 priorities. Both have merit, just need to pick one and commit.",
        "expected_patterns": [],
        "difficulty": "edge"
    },
    
    "edge_external": {
        "context": "setback",
        "entry": "Company announced layoffs and my team might be affected. Nothing I could have done differently.",
        "expected_patterns": [],
        "difficulty": "edge"
    }
}


def get_test_entry(key: str) -> dict:
    """Get a specific test entry by key."""
    return TEST_ENTRIES.get(key)


def get_entries_by_pattern(pattern: str) -> list:
    """Get all entries that should trigger a specific pattern."""
    return [
        (k, v) for k, v in TEST_ENTRIES.items() 
        if pattern in v.get("expected_patterns", [])
    ]


def get_entries_by_context(context: str) -> list:
    """Get all entries for a specific context."""
    return [
        (k, v) for k, v in TEST_ENTRIES.items() 
        if v["context"] == context
    ]


def get_entries_by_difficulty(difficulty: str) -> list:
    """Get entries by difficulty level."""
    return [
        (k, v) for k, v in TEST_ENTRIES.items() 
        if v.get("difficulty") == difficulty
    ]


if __name__ == "__main__":
    print("=== PM SABOTEURS TEST SUITE ===\n")
    print(f"Total entries: {len(TEST_ENTRIES)}\n")
    
    print("By saboteur:")
    for pattern in ["parrot", "peacock", "octopus", "golden_retriever", "rabbit"]:
        entries = get_entries_by_pattern(pattern)
        print(f"  {pattern}: {len(entries)} entries")
    
    print("\nBy context:")
    for context in ["setback", "decision", "procrastinating", "imposter", "overwhelmed"]:
        entries = get_entries_by_context(context)
        print(f"  {context}: {len(entries)} entries")
    
    print("\nBy difficulty:")
    for diff in ["obvious", "subtle", "edge"]:
        entries = get_entries_by_difficulty(diff)
        print(f"  {diff}: {len(entries)} entries")
