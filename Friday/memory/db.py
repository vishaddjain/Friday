import sqlite3
import chromadb
from pathlib import Path
from config.settings import DB_DIR

# ── SQLite setup ───────────────────────────────────────────────────────────────
SQLITE_PATH = DB_DIR / "episodic.db"

def get_sqlite_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

def init_sqlite():
    """Create tables if they don't exist."""
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            role        TEXT NOT NULL,       -- 'user' or 'assistant'
            content     TEXT NOT NULL,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            summary     TEXT NOT NULL,       -- short description of what happened
            detail      TEXT,                -- full detail if needed
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
    print("[db] SQLite initialized")

# ── ChromaDB setup ─────────────────────────────────────────────────────────────
CHROMA_PATH = DB_DIR / "chroma"

chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# collections = tables in ChromaDB
semantic_collection = chroma_client.get_or_create_collection(
    name="semantic_memory",
    metadata={"hnsw:space": "cosine"}  # cosine similarity for meaning matching
)

procedural_collection = chroma_client.get_or_create_collection(
    name="procedural_memory",
    metadata={"hnsw:space": "cosine"}
)

print("[db] ChromaDB initialized")

# ── Initialize everything ──────────────────────────────────────────────────────
def init_db():
    init_sqlite()
    print(f"[db] SQLite path: {SQLITE_PATH}")
    print(f"[db] ChromaDB path: {CHROMA_PATH}")
    print(f"[db] Semantic facts stored: {semantic_collection.count()}")