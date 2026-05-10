"""
RAG Service — Retrieval-Augmented Generation using ChromaDB.
Stores kitchen knowledge (recipes, SOPs, food safety) and retrieves relevant context.
"""

import os
import chromadb
from chromadb.config import Settings
from loguru import logger

# Persistent storage
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chromadb")
os.makedirs(CHROMA_DIR, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(
    name="kitchen_knowledge",
    metadata={"hnsw:space": "cosine"},
)


def add_document(doc_id: str, text: str, metadata: dict | None = None):
    """Add a document to the knowledge base."""
    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata or {"source": "manual"}],
    )
    logger.info(f"[RAG] Added document: {doc_id}")


def add_documents_batch(docs: list[dict]):
    """Add multiple documents. Each: {"id": str, "text": str, "metadata": dict}"""
    collection.upsert(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[d.get("metadata", {"source": "batch"}) for d in docs],
    )
    logger.info(f"[RAG] Added {len(docs)} documents")


def search(query: str, n_results: int = 3) -> list[dict]:
    """Search knowledge base and return relevant documents."""
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = []
    for i, doc in enumerate(results["documents"][0]):
        docs.append({
            "id": results["ids"][0][i],
            "text": doc,
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else 0,
        })
    return docs


def get_doc_count() -> int:
    return collection.count()


def delete_document(doc_id: str):
    collection.delete(ids=[doc_id])


def list_documents(limit: int = 50) -> list[dict]:
    """List all documents in the knowledge base."""
    result = collection.get(limit=limit)
    docs = []
    for i, doc_id in enumerate(result["ids"]):
        docs.append({
            "id": doc_id,
            "text": result["documents"][i][:200] + "..." if len(result["documents"][i]) > 200 else result["documents"][i],
            "metadata": result["metadatas"][i] if result["metadatas"] else {},
        })
    return docs
