import uuid
from memory.db import semantic_collection

def store_fact(fact: str, metadata: dict = None):
    """
    Store a fact about the user in semantic memory.
    fact = natural language string
    metadata = optional tags like {"category": "preference"}
    """
    fact_id = str(uuid.uuid4())
    
    if metadata is None:
        metadata = {"category": "general"}
    
    semantic_collection.add(
        documents=[fact],
        ids=[fact_id],
        metadatas=[metadata] if metadata else None
    )
    print(f"[semantic] Stored: {fact}")

def search_facts(query: str, n_results: int = 3) -> list[str]:
    """
    Search for facts relevant to a query.
    Returns list of matching fact strings.
    """
    count = semantic_collection.count()
    if count == 0:
        return []

    # don't request more results than we have
    n = min(n_results, count)

    results = semantic_collection.query(
        query_texts=[query],
        n_results=n
    )
    return results["documents"][0]

def get_all_facts() -> list[str]:
    """Returns all stored facts."""
    count = semantic_collection.count()
    if count == 0:
        return []
    
    results = semantic_collection.get()
    return results["documents"]

def delete_fact_by_content(content: str):
    """Delete a fact by matching its content exactly."""
    results = semantic_collection.get()
    
    for doc, id_ in zip(results["documents"], results["ids"]):
        if doc == content:
            semantic_collection.delete(ids=[id_])
            print(f"[semantic] Deleted: {content}")
            return
    
    print(f"[semantic] Fact not found: {content}")