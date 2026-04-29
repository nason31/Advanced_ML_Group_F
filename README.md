# MerchAI

AI-driven daily merchandising copilot for mid-market retailers.

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

## Team Roles

| Area | Owner | Key files |
|------|-------|-----------|
| Data pipeline + LLM + Recommendations | Leticia | `src/data/`, `src/llm/`, `src/recommendations/`, `app/` |
| Forecasting + RAG + Scripts | Justus | `src/forecast/`, `src/rag/`, `scripts/`, `notebooks/`, `app/` |
| Business Plan | Alex | `docs/business_plan/` |
| Pitch deck + Demo script + GenAI log | Marie | `docs/` |

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

See [docs/architecture.md](docs/architecture.md) for the full data-flow diagram.

## GenAI Transparency Log

All AI-assisted work must be logged in [docs/genai_transparency_log.md](docs/genai_transparency_log.md) - daily, not compiled at the end.
