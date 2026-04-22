from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def retrieve(query: str, store_dir: Path, k: int = 3) -> list[str]:
    """Return the k most relevant document chunks for a query."""
    client = chromadb.PersistentClient(path=str(store_dir))
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_collection("campaigns", embedding_function=ef)
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]
