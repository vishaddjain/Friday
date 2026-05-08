from datetime import datetime
from memory.db import get_sqlite_connection

def log_message(role: str, content: str):
    """
    Log a single message to episodic memory.
    role = 'user' or 'assistant'
    """
    conn = get_sqlite_connection()
    conn.execute(
        "INSERT INTO conversations (role, content) VALUES (?, ?)",
        (role, content)
    )
    conn.commit()
    conn.close()

def get_recent_conversations(limit: int = 10) -> list[dict]:
    """
    Fetch the last N messages from conversation history.
    """
    conn = get_sqlite_connection()
    cursor = conn.execute(
        """
        SELECT role, content, timestamp 
        FROM conversations 
        ORDER BY id DESC 
        LIMIT ?
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    # reverse so oldest is first
    return [dict(row) for row in reversed(rows)]

def get_conversations_since(since: str) -> list[dict]:
    """
    Fetch conversations since a given timestamp.
    since = '2024-01-01' or '2024-01-01 10:00:00'
    """
    conn = get_sqlite_connection()
    cursor = conn.execute(
        """
        SELECT role, content, timestamp
        FROM conversations
        WHERE timestamp >= ?
        ORDER BY timestamp ASC
        """,
        (since,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_conversation_summary(limit: int = 20) -> str:
    """
    Returns recent conversation as a readable string.
    Used to inject context into LLM prompt.
    """
    messages = get_recent_conversations(limit)
    if not messages:
        return "No previous conversation history."

    lines = []
    for msg in messages:
        time = msg["timestamp"][:16]  # trim to 'YYYY-MM-DD HH:MM'
        lines.append(f"[{time}] {msg['role'].upper()}: {msg['content']}")

    return "\n".join(lines)