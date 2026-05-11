from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


@lru_cache(maxsize=4)
def _get_collection(store_dir_str: str):
    """Cache the (client, embedding fn, collection) trio per vector-store path
    so each retrieve() call after the first does not re-load the embedder.
    """
    client = chromadb.PersistentClient(path=store_dir_str)
    ef = DefaultEmbeddingFunction()
    return client.get_collection("campaigns", embedding_function=ef)


def retrieve(query: str, store_dir: Path, k: int = 3) -> list[str]:
    """Return the k most relevant document chunks for a query."""
    collection = _get_collection(str(store_dir))
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]
