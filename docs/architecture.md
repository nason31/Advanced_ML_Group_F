# MerchAI Architecture

## Training pipeline (offline, via scripts/train_forecast.py)

```
data/raw/ (M5 CSVs)
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
    ▼
src/forecast/evaluate.py ← WRMSSE metric logging
    │
    ▼
data/processed/          ← model_*.pkl, features_*.parquet, idmap_*.parquet
```

## Serve pipeline (live, on every Generate Briefing click)

```
data/processed/ (pre-trained artifacts)
    │
    ▼
src/forecast/serve.py         ← forecast_with_names(): load model, score latest
                                 features, attach human-readable SKU names
    │
    ▼
src/recommendations/summarize.py  ← summarize_forecast(): rank top-K SKUs by
                                     abs delta, flag promote candidates (>+15%)
    │
    ├─────────────────────────────────────────┐
    ▼                                         ▼
src/rag/retriever.py                  (per-SKU loop)
← retrieve(): ChromaDB vector search
  returns 3 context docs per SKU
    │
    ▼
src/llm/reasoner.py           ← reason(): Claude API call with forecast
                                 summary + RAG context → rec text
    │
    ▼
src/llm/guard.py              ← check(): intent check (54 retail phrases) +
                                 numeric check (cited % vs actual delta_pct)
    │
    ▼
src/recommendations/engine.py ← run_pipeline(): assembles list[Rec]
                                 with rec_type, text, flagged, guard results
    │
    ▼
app/main.py                   ← Streamlit UI: briefing cards (colour-coded),
                                 accept/reject buttons, audit trail
```
