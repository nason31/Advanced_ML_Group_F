# MerchAI

AI-powered daily merchandising copilot for mid-market retail chains (50-500 stores). Every morning it delivers a briefing: forecast-backed markdown recommendations, restock priorities, and promotion candidates. Managers accept or reject. Every decision is logged.

**The value:** 0.5% margin improvement on a €500M retailer = €2.5M/year. The software costs €600k/year. That is a 4x ROI.

## Live Demo

**https://advancedmlgroupf-6rpnzwmnplfct2jjiiy3n6.streamlit.app/**

Select a store, click "Generate Today's Briefing", review the recommendations, and try the Ask Your Data box. First call after a cold container takes ~10-15s; subsequent calls are ~5-10s.

## How It Works

1. **Forecast** - LightGBM trained on M5 Walmart data predicts next-period sales per SKU. Top movers are selected as recommendation candidates.
2. **RAG + Reasoning** - ChromaDB retrieves relevant retail context (seasonality, promotions, category trends). Claude synthesises forecast signal and context into a plain-language recommendation with a cited percentage.
3. **Hallucination Guard** - Every recommendation is cross-checked: does the action contradict the forecast direction? Is the actual delta cited? Flagged recommendations are shown with a warning. The manager's decision and the guard result are both written to the audit trail.
4. **Briefing UI** - Streamlit dashboard with accept/reject controls, confidence signals, and a Q&A assistant grounded in the same data.

## Tech Stack

LightGBM - ChromaDB (RAG) - Claude API (claude-sonnet-4-6) - Streamlit - M5 Forecasting dataset - Python 3.12

## Forecast Accuracy

LightGBM baseline evaluated on a held-out 28-day validation window (M5 benchmark data):

| Store | WRMSSE |
|-------|--------|
| CA_1 | 0.74 |
| CA_2 | 0.73 |
| TX_1 | 0.76 |

**Average WRMSSE: 0.74.** A score below 1.0 means the model outperforms the naive "same as yesterday" baseline. Top M5 competition ensembles score ~0.50; this is a single LightGBM trained on the full feature set.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # add your ANTHROPIC_API_KEY
python scripts/download_data.py   # requires Kaggle credentials in .env
python scripts/train_forecast.py  # train per-store LightGBM + persist artifacts
python scripts/build_rag_corpus.py # build M5-derived RAG context + ingest to ChromaDB
streamlit run app/main.py
```

## Running Tests

```bash
pytest tests/ -v
```

19 tests covering the forecast pipeline, RAG retriever, guard logic, and recommendation engine.

## Docs

- [Architecture](docs/architecture.md) - full data-flow diagram and component overview
- [Feature Overview](docs/feature_overview.md) - feature table with rubric mapping
- [Business Plan](docs/deliverables/business_plan/) - market sizing, unit economics, GTM strategy
- [GenAI Transparency Log](docs/deliverables/business_plan/genai_transparency_log.md) - required deliverable, logged per session

## Team

| Area | Owner | Key files |
|------|-------|-----------|
| Data pipeline + LLM + Recommendations | Leticia | `src/data/`, `src/llm/`, `src/recommendations/`, `app/` |
| Forecasting + RAG + Scripts | Justus | `src/forecast/`, `src/rag/`, `scripts/`, `notebooks/`, `app/` |
| Business Plan | Alex | `docs/deliverables/business_plan/` |
| Pitch deck + Demo script + GenAI log | Marie | `docs/deliverables/` |
