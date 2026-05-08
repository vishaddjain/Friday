import uuid
from memory.db import procedural_collection

def store_rule(rule: str, metadata: dict = {}):
    """
    Store a behavioral rule for Friday.
    rule = natural language instruction
    """
    rule_id = str(uuid.uuid4())
    
    procedural_collection.add(
        documents=[rule],
        ids=[rule_id],
        metadatas=[metadata] if metadata else None
    )
    print(f"[procedural] Stored rule: {rule}")

def get_all_rules() -> list[str]:
    """Returns all stored behavioral rules."""
    count = procedural_collection.count()
    if count == 0:
        return []
    
    results = procedural_collection.get()
    return results["documents"]

def get_relevant_rules(context: str, n_results: int = 3) -> list[str]:
    """
    Search for rules relevant to the current context.
    """
    count = procedural_collection.count()
    if count == 0:
        return []

    n = min(n_results, count)
    results = procedural_collection.query(
        query_texts=[context],
        n_results=n
    )
    return results["documents"][0]

def delete_rule(rule: str):
    """Delete a rule by matching content."""
    results = procedural_collection.get()
    
    for doc, id_ in zip(results["documents"], results["ids"]):
        if doc == rule:
            procedural_collection.delete(ids=[id_])
            print(f"[procedural] Deleted rule: {rule}")
            return
    
    print(f"[procedural] Rule not found: {rule}")