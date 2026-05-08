# run this once to set up Friday's default behavior for you
from memory.db import init_db
from memory.procedural import store_rule
from memory.semantic import store_fact

init_db()

# ── Behavioral rules ───────────────────────────────────────────────────────────
rules = [
    "Always keep responses concise — under 2 sentences unless user asks for detail.",
    "Never suggest cloud-based or paid services. User prefers local and open source.",
    "Always confirm before taking any action on the computer or file system.",
    "User prefers direct answers — no fluff, no filler phrases like 'certainly' or 'of course'.",
]

# ── Core facts about Vishad ────────────────────────────────────────────────────
facts = [
    "User's name is Vishad. He is a student from Jaipur, India.",
    "Vishad is building a local AI assistant called Friday.",
    "Vishad uses a MacBook M1 Air with 8GB RAM.",
    "Vishad prefers concise, direct answers without fluff.",
    "Vishad prefers local and open source solutions over cloud services until its free.",
     "Vishad is learning OSTEP Book.",  
]

print("Seeding procedural rules...")
for rule in rules:
    store_rule(rule)

print("\nSeeding core facts...")
for fact in facts:
    store_fact(fact, metadata={"source": "manual"})

print("\nDone! Friday's memory is seeded.")