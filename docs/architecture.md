# MerchAI Architecture

```
M5 CSV Data
    │
    ▼
src/data/loader.py       ← load_m5() returns raw DataFrames
    │
    ▼
src/data/features.py     ← build_features() returns feature matrix
    │
    ▼
src/forecast/model.py    ← train() / predict() via LightGBM
    │
    ├──────────────────────────────────────────────┐
    ▼                                              ▼
src/rag/retriever.py                   src/forecast/evaluate.py
(retrieve campaign context)            (WRMSSE logging)
    │
    ▼
src/llm/reasoner.py      ← reason() calls Claude with forecast + RAG context
    │
    ▼
src/llm/guard.py         ← check() flags contradictory recommendations
    │
    ▼
src/recommendations/engine.py  ← run_pipeline() returns list[Rec]
    │
    ▼
app/main.py              ← Streamlit UI: briefing cards + accept/reject + audit
```
