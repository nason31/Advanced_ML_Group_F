# GenAI Transparency Log

**Project:** MerchAI  
**Required:** All team members log AI-assisted work daily.

## Log Format

```
Date: YYYY-MM-DD
Team Member: [name]
Tool Used: [Claude / ChatGPT / Copilot / etc.]
Task: [what you were working on]
AI Contribution: [what the AI generated or suggested]
Human Review: [what you changed, verified, or rejected]
```

---

## Entries

Date: 2026-04-22
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7)
Task: Scaffolding the entire MerchAI repository skeleton - directory structure, stubs for every pipeline layer, and supporting docs, so the Tech and Business tracks could start working in parallel without stepping on each other.
AI Contribution: Claude Code produced 10 commits (ef7697f through c2867bd) that built the repo from scratch:
  (1) Repo hygiene: .gitignore covering data/raw, data/processed, vector_store, .env, Python caches; .env.example documenting ANTHROPIC_API_KEY and Kaggle slots; requirements.txt pinning pandas, numpy, lightgbm, chromadb, sentence-transformers, anthropic, streamlit, and dev tools.
  (2) Directory scaffolding: src/{data,forecast,rag,llm,recommendations} plus app/, tests/, docs/, scripts/, notebooks/, with __init__.py files and data/ placeholder directories.
  (3) Layer stubs with realistic function signatures so teammates could fill them in without redesigning the API: src/data/loader.py (load_m5), src/data/features.py (build_features), src/forecast/model.py (train, predict), src/forecast/evaluate.py (wrmsse), src/rag/ingest.py + retriever.py (ChromaDB with all-MiniLM-L6-v2 embeddings, real not stubbed), src/llm/reasoner.py (Claude call wrapper), src/llm/prompts.py (system + user prompt builder), src/llm/guard.py (direction-mismatch hallucination guard), src/recommendations/engine.py (Rec dataclass plus empty run_pipeline).
  (4) Streamlit app scaffold: app/main.py with store/date sidebar and Generate Briefing button, app/components/briefing_card.py (accept / reject with flagged-warning styling) and audit_trail.py, all wired to Rec from the recommendations engine.
  (5) Docs: docs/architecture.md with the full data-flow diagram, docs/genai_transparency_log.md with the required-deliverable template, docs/business_plan/outline.md skeleton, scripts/download_data.py (Kaggle CLI wrapper for the M5 competition).
  (6) A tests/ suite with hand-written unit tests exercising every stubbed layer so the baseline green-CI state was visible: test_loader, test_model (train/predict shape plus wrmsse perfect-prediction), test_retriever (ingest round-trip), test_reasoner (mocked Anthropic client plus guard behaviour), test_engine (dataclass plus empty-list invariant).
  (7) README rewrite: one-command setup block (venv -> pip install -> .env -> download -> streamlit run), team roles table with TBD owners per area, pointers to architecture and transparency-log docs.
Human Review: Walked through every file before committing to confirm the function signatures matched the architecture diagram and would not force Week 2 refactors on whoever filled them in. Kept the guard.check() implementation intentionally thin (keyword-level direction check rather than full LLM verification) to avoid premature complexity - Week 3 can harden it. Accepted Streamlit over Next.js after weighing deploy simplicity. Drafted the README bootstrap so a teammate on a clean machine could get to the "Generate Briefing" button with no help. Merged everything to main because scaffolding was uncontroversial and nobody else had branched yet.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Expanding the feature set to make the product more AI-native and better aligned with the course curriculum
AI Contribution: Claude proposed 7 new features: RAG-powered category intelligence, a conversational "Ask Your Data" interface, multimodal competitor monitoring, an agentic execution loop, a hallucination guard layer, confidence & uncertainty display, and a data privacy architecture. Each was linked to a specific course week (Weeks 3-5).
Human Review: Confirmed RAG layer, hallucination guard, and conversational interface as the three priority additions. Deferred multimodal and agentic mode to nice-to-have status. Merged confidence display into the hallucination guard concept rather than treating it as a standalone feature.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Adding a marketing recommendation dimension to the product - identifying which products to promote and how
AI Contribution: Claude proposed a "Promote This" module using sell-through velocity, competitor stock signals, and margin data to surface SKUs worth actively marketing. It also suggested layering sentiment analysis (Week 1 course content) on product reviews to detect early demand signals, and a channel recommendation logic (email vs social vs in-store placement) based on product profile.
Human Review: Confirmed the "Promote This" module and channel recommendation logic as concrete additions. Adopted the sentiment signal idea as a differentiating feature. Kept the implementation rule-based (rules drive logic, LLM writes copy) to reduce hallucination risk.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Creating a high-level 3-week project plan and role split for a team of 4
AI Contribution: Claude generated a structured week-by-week plan covering: Week 1 (foundation & alignment - kickoff, data setup, business plan draft), Week 2 (prototype build - LLM layer, RAG, Promote This, dashboard, deployment), Week 3 (polish & rehearse - demo hardening, hallucination guard, dry runs, Q&A prep). Included suggested team split: 2 tech, 1 business, 1 floats.
Human Review: Confirmed the 3-week structure fits the course timeline. Adopted the 2-tech / 1-business / 1-float role split. Requested a more detailed day-by-day breakdown as a follow-up.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Generating a detailed 3-week project plan PDF broken down by day, task, owner, and subtasks
AI Contribution: Claude produced a multi-page PDF (MerchAI_3Week_Plan.pdf) with day-by-day task breakdowns across all three weeks, including owner badges (Tech / Business / Whole team / Presentation), detailed subtask lists, end-of-week checklists, risk warnings, and a team split recommendation.
Human Review: Reviewed all tasks against the rubric requirements and confirmed coverage of both deliverables (business plan + prototype). Identified that the PDF was Claude.ai-environment-dependent when opened in Safari - prompted conversion to PDF format for team sharing.

---

Date: 2026-04-23
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Converting the 3-week project plan into a markdown file for GitHub tracking
AI Contribution: Claude converted the interactive HTML project plan into a structured markdown file (project_plan.md) with GitHub-renderable tables per week, interactive task checkboxes (- [ ]), a Q&A preparation table, and risk callouts. Structured for the docs/ folder alongside the existing genai_transparency_log.md.
Human Review: Confirmed structure matches the repo layout visible in the GitHub screenshot. Verified checkboxes render correctly on GitHub. Approved file for commit into docs/.

---

Date: 2026-04-23
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Converting the feature overview widget into a markdown file for the GitHub repo
AI Contribution: Claude converted the full HTML feature overview table into a clean GitHub-compatible markdown file (feature_overview.md), preserving the core vs. new feature tags as emoji indicators (blue / green), the metrics table, and all 14 feature rows with tech stack and rubric columns.
Human Review: Verified all 14 features were correctly carried over. Confirmed emoji legend as a suitable replacement for the colour-coded HTML tags. File dropped into docs/ folder in the repo.

---

Date: 2026-04-23
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Building the LightGBM baseline pipeline - data loader, feature engineering, training notebook
AI Contribution: Claude implemented three components from scratch. (1) Fixed src/data/loader.py to load all three M5 tables (sales, calendar, sell_prices). (2) Replaced the stub in src/data/features.py with full feature engineering: wide-to-long melt, calendar join (wday, month, SNAP flags), price join via wm_yr_wk, lag features at 7/14/28 days, rolling means shifted by 28 days to prevent leakage, and categorical encoding for LightGBM. (3) Created notebooks/01_baseline.ipynb with a full train/eval pipeline scoped to store CA_1, using a tweedie objective and early stopping, producing a WRMSSE of 0.74 and RMSE of 2.15 on a 28-day holdout. Claude also created CLAUDE.md project context file and updated the Week 1 checklist in docs/project_plan.md.
Human Review: Verified the feature matrix shape (5.8M rows, 22 columns) and confirmed the lag/rolling logic is leakage-free. Confirmed tweedie objective is appropriate for sparse retail count data. Accepted WRMSSE 0.74 as a solid Week 1 baseline (top 10% on M5 is ~0.50, room to improve in Week 2). Ticked off LightGBM baseline running in project plan.

---

Date: 2026-04-24
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7)
Task: Wiring run_pipeline end-to-end and preparing the app for Streamlit Cloud deploy. Took the repo from a scaffolded state (every layer a stub except LightGBM baseline) to a working briefing pipeline: forecast -> RAG retrieve -> Claude reason -> hallucination guard -> Rec list, rendered in the existing Streamlit UI.
AI Contribution: Claude drafted and committed 9 changes on branch feat/wire-run-pipeline-and-deploy (total +725/-21 across 13 files):
  (1) scripts/train_forecast.py - per-store LightGBM training with 28-day holdout WRMSSE logging, persists model/features/idmap parquet artifacts to data/processed/. Produced WRMSSE 0.7425 / 0.7259 / 0.7615 on CA_1 / CA_2 / TX_1.
  (2) src/forecast/serve.py - load_model, forecast_store (latest-row-per-SKU predict plus baseline/delta_pct/direction), and forecast_with_names that re-attaches human-readable item_id / dept_id / cat_id via the idmap parquet so the LLM can cite specific SKUs. All file loads wrapped with functools.lru_cache.
  (3) scripts/build_rag_corpus.py - derived 57 M5-grounded context blurbs (SNAP lift, event day effect, weekday peak, price drop elasticity, YoY category trend) per store. Ingested to ChromaDB at data/vector_store/ via the existing ingest_docs() helper.
  (4) src/recommendations/summarize.py - top-K ranker that filters SKUs below a min_baseline floor (default 1 unit/day) before sorting by abs(delta_pct), returns prompt-ready summary text plus per-SKU seed dicts.
  (5) src/recommendations/engine.py - replaced the empty-list placeholder with real orchestration wiring forecast_with_names -> summarize_forecast -> retrieve -> reason -> guard.check -> Rec. Public signature unchanged so app/main.py continued to work.
  (6) app/main.py - added explicit error UI when the model or vector store are missing, wrapped run_pipeline in try/except, added a subheader for store/date.
  (7) .streamlit/config.toml and secrets.toml.example - theme plus headless server, plus template for ANTHROPIC_API_KEY in the Streamlit Cloud secrets UI.
  (8) .gitignore - re-included data/processed/*.pkl, *.parquet, and data/vector_store/** so the deployed app can read artifacts at runtime while keeping data/raw/ fully ignored.
  (9) requirements.txt - added joblib==1.4.2, bumped anthropic 0.28.0 -> 0.39.0 to match the claude-sonnet-4-6 model string.
  Plus tests: tests/test_summarize.py (7 new tests, all passing) and a rewritten tests/test_engine.py (4 tests, monkeypatches forecast/retrieve/reason, asserts guard catches contradictory output).
Human Review: Reviewed every diff before committing. Rejected two Claude suggestions mid-session: (a) using st.cache_resource inside app/main.py because it would have forced a run_pipeline signature change - switched to functools.lru_cache inside serve.py instead; (b) accepting commits on main - redirected all work to branch feat/wire-run-pipeline-and-deploy. Switched the local Python env from venv 3.9 to a conda merchai env at Python 3.12 after hitting PEP 604 compatibility errors. Fixed Kaggle 401 auth by generating a fresh legacy API token (the initial "KGAT..." Kaggle submission token was the wrong credential type). Confirmed WRMSSE scores match the 0.74 baseline Leticia reported on Apr 23, confirming the new script produces the same model as the notebook.

---

<!-- Append new entries below this line, in chronological (oldest-first) order. Follow the template at the top of the file. -->

