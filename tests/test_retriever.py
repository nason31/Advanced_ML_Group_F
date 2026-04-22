from src.rag.ingest import ingest_docs
from src.rag.retriever import retrieve


def test_retrieve_returns_strings(tmp_path):
    doc = tmp_path / "campaign.txt"
    doc.write_text("50% off FOODS items drove +12% units in Week 3.")
    store_dir = tmp_path / "store"
    ingest_docs([doc], store_dir)
    results = retrieve("promotion discount", store_dir, k=1)
    assert isinstance(results, list)
    assert len(results) >= 1
    assert isinstance(results[0], str)
