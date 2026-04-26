import os
from functools import lru_cache
from pathlib import Path

# Force HuggingFace Hub to use only the local cache. Without this, every
# SentenceTransformerEmbeddingFunction() instantiation makes a network call
# to the HF CDN to check for model updates, and that call sometimes hangs
# indefinitely behind a load balancer in CLOSE_WAIT state (observed locally
# during the Apr 26 smoke test).
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# Disable joblib/loky multiprocessing inside sentence-transformers. On macOS
# with the default `spawn` start method, the embedding function can hang on
# a leaked POSIX semaphore when called outside an `if __name__ == "__main__":`
# guard (Streamlit and `python -c` invocations). Single-thread is plenty fast
# for our ~50-doc corpus.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


@lru_cache(maxsize=4)
def _get_collection(store_dir_str: str):
    """Cache the (client, embedding fn, collection) trio per vector-store path
    so each retrieve() call after the first does not re-load sentence-transformers.
    """
    client = chromadb.PersistentClient(path=store_dir_str)
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return client.get_collection("campaigns", embedding_function=ef)


def retrieve(query: str, store_dir: Path, k: int = 3) -> list[str]:
    """Return the k most relevant document chunks for a query."""
    collection = _get_collection(str(store_dir))
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]
