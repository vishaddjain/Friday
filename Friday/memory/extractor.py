import json
import requests
import re
from memory.semantic import store_fact
from config.settings import OLLAMA_URL, OLLAMA_MODEL

EXTRACTOR_PROMPT = """You are a memory extractor for an AI assistant called Friday.
Your job is to read a conversation and extract facts worth remembering long term about the user.

Rules:
- Only extract facts about the USER, not Friday's responses
- Only extract things that are stable and reusable (preferences, habits, projects, personal info)
- Ignore small talk, greetings, one-off questions
- If nothing is worth remembering, return empty list
- Be concise — one sentence per fact

Respond ONLY with a JSON array of strings. No explanation, no markdown, no preamble.

Example output:
["Vishad is learning Rust.", "Vishad prefers dark mode.", "Vishad wakes up at 6am."]

If nothing to extract:
[]
"""

def extract_and_store(conversation: list[dict]):
    """
    Takes recent conversation turns and extracts memorable facts.
    conversation = [{"role": "user", "content": "..."}, ...]
    """
    if not conversation:
        return

    # format conversation for the prompt
    convo_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation
    )

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": EXTRACTOR_PROMPT},
                    {"role": "user", "content": f"Extract facts from this conversation:\n\n{convo_text}"}
                ],
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        raw = response.json()["message"]["content"].strip()

        # strip markdown code fences if model adds them
        raw = raw.replace("```json", "").replace("```", "").strip()

        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if not match:
            print(f"[extractor] No JSON array found in: {raw}")
            return

        facts = json.loads(match.group())

        if not isinstance(facts, list):
            return

        for fact in facts:
            if isinstance(fact, str) and fact.strip():
                store_fact(fact.strip(), metadata={"source": "auto"})

        if facts:
            print(f"[extractor] Stored {len(facts)} new facts")
        else:
            print("[extractor] Nothing worth remembering")

    except json.JSONDecodeError:
        print(f"[extractor] Failed to parse JSON: {raw}")
    except Exception as e:
        print(f"[extractor] Error: {e}")