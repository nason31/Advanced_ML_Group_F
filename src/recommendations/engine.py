from dataclasses import dataclass
from pathlib import Path


@dataclass
class Rec:
    rec_type: str        # "markdown" | "restock" | "promote"
    text: str
    flagged: bool
    flag_reason: str


def run_pipeline(store_id: str, date: str, data_dir: Path, vector_store_dir: Path) -> list[Rec]:
    """Orchestrate data → forecast → RAG → LLM → guard → Rec list.

    Placeholder — returns empty list until each layer is wired in Phase 2.
    """
    return []
