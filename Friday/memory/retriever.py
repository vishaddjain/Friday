from memory.semantic import search_facts
from memory.episodic import get_recent_conversations

# minimum similarity score to include a fact
# ChromaDB returns distances — lower = more similar
# 0.7 is a good cutoff for cosine distance
RELEVANCE_THRESHOLD = 0.7

def get_relevant_context(user_message: str, n_facts: int = 3, n_messages: int = 6) -> str:
    """
    Given the user's message, retrieve relevant memory context.
    Returns a formatted string ready to inject into LLM prompt.
    """
    context_parts = []

    # ── Semantic memory — relevant facts ──────────────────────────────────────
    facts = search_facts(user_message, n_results=n_facts)
    if facts:
        facts_text = "\n".join(f"- {fact}" for fact in facts)
        context_parts.append(f"What you know about the user:\n{facts_text}")

    # ── Episodic memory — recent conversation ─────────────────────────────────
    recent = get_recent_conversations(limit=n_messages)
    if recent:
        lines = []
        for msg in recent:
            time = msg["timestamp"][:16]
            lines.append(f"[{time}] {msg['role'].upper()}: {msg['content']}")
        history_text = "\n".join(lines)
        context_parts.append(f"Recent conversation history:\n{history_text}")

    if not context_parts:
        return ""

    return "\n\n".join(context_parts)


def build_system_prompt(base_prompt: str, user_message: str) -> str:
    """
    Takes the base system prompt and enriches it with memory context.
    This is what gets sent to the LLM every turn.
    """
    context = get_relevant_context(user_message)

    if not context:
        return base_prompt

    return f"""{base_prompt}

── Memory Context ──
{context}
────────────────────"""