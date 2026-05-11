from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


def ingest_docs(paths: list[Path], store_dir: Path) -> None:
    """Embed text files and persist them in a ChromaDB collection."""
    store_dir = Path(store_dir)
    client = chromadb.PersistentClient(path=str(store_dir))
    ef = DefaultEmbeddingFunction()
    collection = client.get_or_create_collection("campaigns", embedding_function=ef)
    for path in paths:
        text = Path(path).read_text()
        collection.upsert(documents=[text], ids=[Path(path).stem])
