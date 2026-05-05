import requests
from config.settings import OLLAMA_URL, OLLAMA_MODEL

# ── System prompt — Friday's personality ──────────────────────────────────────
SYSTEM_PROMPT = """You are Friday, a personal AI assistant. You are:
- Concise and direct — no fluff, no filler words
- Conversational — you're being spoken aloud, so never use bullet points, markdown, or lists
- Smart but not arrogant
- Honest — if you don't know something, say so

Keep responses short unless the user asks for detail. 
You are running locally on the user's machine."""

# ── Conversation history ───────────────────────────────────────────────────────
history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


def think(user_input: str) -> str:
    """
    Send user input to Ollama, get a response.
    Maintains conversation history across turns.
    """
    global history

    # add user message to history
    history.append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": history,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        reply = response.json()["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        reply = "I can't reach Ollama. Make sure it's running with ollama serve."
    except requests.exceptions.Timeout:
        reply = "That took too long. Ollama might be overloaded."
    except Exception as e:
        reply = f"Something went wrong: {str(e)}"

    # add assistant response to history
    history.append({"role": "assistant", "content": reply})

    return reply


def reset_history():
    """Clear conversation history, keep system prompt."""
    global history
    history = [{"role": "system", "content": SYSTEM_PROMPT}]