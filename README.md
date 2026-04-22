# MerchAI

AI-driven daily merchandising copilot for mid-market retailers.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY
python scripts/download_data.py   # requires Kaggle credentials in .env
streamlit run app/main.py
```

## Team Roles

| Area | Owner | Key files |
|------|-------|-----------|
| Data + Forecasting | TBD | `src/data/`, `src/forecast/` |
| LLM + RAG + Frontend | TBD | `src/llm/`, `src/rag/`, `app/` |
| Business Plan | TBD | `docs/business_plan/` |
| Floater / Demo | TBD | `docs/genai_transparency_log.md` |

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

See [docs/architecture.md](docs/architecture.md) for the full data-flow diagram.

## GenAI Transparency Log

All AI-assisted work must be logged in [docs/genai_transparency_log.md](docs/genai_transparency_log.md) — daily, not compiled at the end.
