import requests
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from memory.db import init_db
from memory.episodic import log_message, get_recent_conversations
from memory.extractor import extract_and_store
from memory.retriever import build_system_prompt
from memory.procedural import get_all_rules

# initialize memory on startup
init_db()

BASE_PROMPT = """You are Friday, a personal AI assistant. You are:
- Concise and direct — no fluff, no filler words
- Conversational — you're being spoken aloud, so never use bullet points, markdown, or lists
- Smart but not arrogant
- Honest — if you don't know something, say so

Keep responses short unless the user asks for detail.
You are running locally on the user's machine."""


def think(user_input: str) -> str:
    """
    Core brain loop with memory:
    1. Build context-aware system prompt from memory
    2. Send to Ollama with recent history
    3. Log conversation
    4. Extract and store new facts
    """

    # ── Step 1: build memory-enriched system prompt ───────────────────────────
    system_prompt = build_system_prompt(BASE_PROMPT, user_input)

    # ── Step 2: inject procedural rules ───────────────────────────────────────
    rules = get_all_rules()
    if rules:
        rules_text = "\n".join(f"- {r}" for r in rules)
        system_prompt += f"\n\nBehavioral rules to always follow:\n{rules_text}"

    # ── Step 3: get recent conversation for context ───────────────────────────
    recent = get_recent_conversations(limit=6)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in recent:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    # ── Step 4: call Ollama ───────────────────────────────────────────────────
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        reply = response.json()["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        reply = "I can't reach Ollama. Make sure it's running."
    except requests.exceptions.Timeout:
        reply = "That took too long. Ollama might be overloaded."
    except Exception as e:
        reply = f"Something went wrong: {str(e)}"

    # ── Step 5: log to episodic memory ────────────────────────────────────────
    log_message("user", user_input)
    log_message("assistant", reply)

    # ── Step 6: extract new facts in background ───────────────────────────────
    recent_for_extraction = get_recent_conversations(limit=4)
    extract_and_store(recent_for_extraction)

    return reply


def reset_history():
    """Nothing to reset — history lives in SQLite now."""
    pass# friday/core/brain.py

import requests
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from memory.db import init_db
from memory.episodic import log_message, get_recent_conversations
from memory.extractor import extract_and_store
from memory.retriever import build_system_prompt
from memory.procedural import get_all_rules

# initialize memory on startup
init_db()

BASE_PROMPT = """You are Friday, a personal AI assistant. You are:
- Concise and direct — no fluff, no filler words
- Conversational — you're being spoken aloud, so never use bullet points, markdown, or lists
- Smart but not arrogant
- Honest — if you don't know something, say so

Keep responses short unless the user asks for detail.
You are running locally on the user's machine."""


def think(user_input: str) -> str:
    """
    Core brain loop with memory:
    1. Build context-aware system prompt from memory
    2. Send to Ollama with recent history
    3. Log conversation
    4. Extract and store new facts
    """

    # ── Step 1: build memory-enriched system prompt ───────────────────────────
    system_prompt = build_system_prompt(BASE_PROMPT, user_input)

    # ── Step 2: inject procedural rules ───────────────────────────────────────
    rules = get_all_rules()
    if rules:
        rules_text = "\n".join(f"- {r}" for r in rules)
        system_prompt += f"\n\nBehavioral rules to always follow:\n{rules_text}"

    # ── Step 3: get recent conversation for context ───────────────────────────
    recent = get_recent_conversations(limit=6)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in recent:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    # ── Step 4: call Ollama ───────────────────────────────────────────────────
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        reply = response.json()["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        reply = "I can't reach Ollama. Make sure it's running."
    except requests.exceptions.Timeout:
        reply = "That took too long. Ollama might be overloaded."
    except Exception as e:
        reply = f"Something went wrong: {str(e)}"

    # ── Step 5: log to episodic memory ────────────────────────────────────────
    log_message("user", user_input)
    log_message("assistant", reply)

    # ── Step 6: extract new facts in background ───────────────────────────────
    recent_for_extraction = get_recent_conversations(limit=4)
    extract_and_store(recent_for_extraction)

    return reply


def reset_history():
    """Nothing to reset — history lives in SQLite now."""
    pass