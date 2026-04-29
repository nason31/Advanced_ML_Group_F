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

<!-- Append new entries at the TOP (newest-first order). -->

Date: 2026-04-29
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Hardening the hallucination guard and tightening the LLM system prompt to reduce false flags and catch real hallucinations.
AI Contribution: Claude implemented changes across 4 files in 4 commits on leticia-branch:
  (1) src/llm/prompts.py - rewrote system prompt with strict data rules: verbatim number citation, one recommendation per response, no passing mentions of other rec types. Updated build_user_prompt to explicitly ask Claude to reference the exact delta percentage.
  (2) src/llm/guard.py - full rewrite. Two checks: (a) Intent check using ~54 hardcoded retail action phrases across markdown / restock / promote categories - detects Claude's recommended action and flags if it contradicts the forecast direction. (b) Numeric check using regex to extract the first percentage from Claude's text, compared against actual delta_pct with 2x tolerance - catches fabricated figures. Returns intent_check and numeric_check result strings for UI display.
  (3) src/recommendations/engine.py - passes delta_pct from seed data into check(), adds intent_check and numeric_check fields to the Rec dataclass so the UI can display them.
  (4) app/components/briefing_card.py - adds a "Guard checks" expander to every card showing intent and numeric check outcomes. Collapsed by default, auto-expands when a card is flagged.
  Also discussed the decision not to use a second Claude API call for intent classification (doubles cost and latency, hurts unit economics story) and the rationale for 2x numeric tolerance (catches hallucinations, not rounding).
Human Review: Defined the phrase lists collaboratively - reviewed all ~54 phrases for retail relevance and confirmed coverage. Decided on hardcoded phrases over an ML classifier after weighing demo reliability vs accuracy. Set the 2x tolerance threshold based on what counts as a plausible rounding vs a fabricated number. Confirmed the expander UX - collapsed by default so the UI is not cluttered, but auto-opens on flagged cards so the guard moment is visible to demo audience without manual interaction.

Date: 2026-04-29
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Implementing the "Promote This" recommendation module - the third rec type alongside markdown and restock - and documenting its business logic in the plan.
AI Contribution: Claude implemented the feature across 4 files in 4 separate commits on leticia-branch:
  (1) src/recommendations/summarize.py - added promote_candidate flag (delta_pct > +15% above 28-day baseline) to each rec seed, with an explanatory note appended to the focus_line so the LLM knows it is a strong-momentum SKU.
  (2) src/recommendations/engine.py - updated rec_type assignment logic: "markdown" for down-trending SKUs, "promote" for promote_candidate=True, "restock" for everything else.
  (3) src/llm/prompts.py - added explicit definitions of all three rec types to the system prompt, including channel-action guidance for PROMOTE THIS (end-cap placement, weekly flyer, BOGO) so Claude generates actionable promotion copy rather than generic restock advice.
  (4) app/components/briefing_card.py - colour-coded briefing cards: green for promote, red for guard-flagged, blue for markdown/restock.
  Also updated docs/business_plan/outline.md to document the threshold logic (>+15% = momentum signal worth amplifying) for the business track teammates.
  Also updated docs/project_plan.md to mark Week 2 checkboxes (LLM layer, RAG layer, dashboard UI) as complete based on Justus's Apr 24/26 commits, and noted remaining gaps (Promote This - now done, deployment URL, business deliverables).
Human Review: Defined the +15% threshold based on business reasoning - strong enough signal to isolate genuine momentum from noise, defensible in Q&A as calibratable per retailer margin targets. Verified the priority order in engine.py (markdown takes precedence over promote, promote over restock) reflects correct merchandising logic. Confirmed the system prompt additions do not contradict the existing hallucination guard instruction. Reviewed all 4 diffs before each commit was pushed.

---

Date: 2026-04-26
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7)
Task: Live end-to-end smoke test of the run_pipeline branch from Apr 24 - get the Streamlit app actually generating Claude-backed briefings on real M5 data, fix whatever surfaces, then commit the artifacts and push so the branch is ready to deploy to Streamlit Cloud.
AI Contribution: Two debugging-and-fix commits plus the artifact commit, all on branch feat/wire-run-pipeline-and-deploy:
  (1) 1bfb1f2 fix: unblock end-to-end Streamlit smoke test. Three independent issues surfaced when the Streamlit run was first attempted; Claude diagnosed each one from process state and wrote the fix:
      - app/main.py: ModuleNotFoundError: No module named 'app' on launch. streamlit run app/main.py puts app/ on sys.path, not the repo root. Added the same sys.path.insert(repo_root) hack we used for the scripts.
      - src/rag/retriever.py: pipeline hung indefinitely on the first retrieve() call. Diagnosed via lsof showing an ESTABLISHED connection to a HuggingFace CDN in CLOSE_WAIT state - SentenceTransformerEmbeddingFunction makes a network "is your cached model up to date" call on every instantiation, and that call was hanging behind the HF load balancer. Fix: HF_HUB_OFFLINE=1 + TRANSFORMERS_OFFLINE=1 + lru_cache on the (client, ef, collection) trio so retrieve() loads sentence-transformers exactly once.
      - src/rag/retriever.py: a separate hang showed up on a leaked loky POSIX semaphore (/loky-PID-XXX) when the script ran outside an `if __name__ == "__main__":` guard - sentence-transformers spawns a worker pool via joblib that deadlocks on macOS spawn. Fix: TOKENIZERS_PARALLELISM=false + OMP_NUM_THREADS=1.
      - requirements.txt: anthropic 0.39.0 raises TypeError: Client.__init__() got an unexpected keyword argument 'proxies' against modern httpx. Bumped to 0.97.0 (the latest at time of fix).
  (2) b6fd25d chore(data): commit the serve-time artifacts. data/processed/model_*.pkl + features_*.parquet + idmap_*.parquet (~3MB), data/rag_source/*.txt (57 blurbs, ~5KB), data/vector_store/ (~2.5MB ChromaDB). 72 files, ~5.6MB total. Necessary because Streamlit Cloud has no Kaggle credentials and would otherwise hit the no-trained-model error path.
  Plus instrumented engine.py with timing prints during diagnosis (later removed pre-commit).
  Live smoke test result on CA_1: 3 well-formed Restock recommendations (FOODS_3_785 +419.6%, FOODS_3_324 +395.9%, HOBBIES_1_232 +359.2%) in ~48 seconds end-to-end. All 3 over-flagged by the keyword-match guard (Claude mentions "markdown" in passing as one of the available rec types; flagged for tightening in a follow-up branch).
Human Review: Drove the diagnostic process - rejected the first hypothesis (Streamlit's threading model) when the same hang reproduced from a plain python -c invocation. Authorised each force-kill before issuing it. Switched the Python env from venv 3.9 to a conda merchai env at 3.12 mid-session after PEP 604 union syntax errors surfaced. Generated a fresh Kaggle legacy API token after Claude flagged that the original "KGAT..." string was a Kaggle competition submission token, not the API credential. Approved the requirements.txt anthropic bump from 0.39.0 to 0.97.0 only after confirming the failure reproduced and the bump fixed it. After tests went green (18 passed including the previously-hanging test_retriever), pushed the branch and opened the PR via the GitHub web UI manually because gh CLI is not installed locally. Logged this entry per the mandatory end-of-session rule we added to CLAUDE.md yesterday.

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

Date: 2026-04-23
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Building the LightGBM baseline pipeline - data loader, feature engineering, training notebook
AI Contribution: Claude implemented three components from scratch. (1) Fixed src/data/loader.py to load all three M5 tables (sales, calendar, sell_prices). (2) Replaced the stub in src/data/features.py with full feature engineering: wide-to-long melt, calendar join (wday, month, SNAP flags), price join via wm_yr_wk, lag features at 7/14/28 days, rolling means shifted by 28 days to prevent leakage, and categorical encoding for LightGBM. (3) Created notebooks/01_baseline.ipynb with a full train/eval pipeline scoped to store CA_1, using a tweedie objective and early stopping, producing a WRMSSE of 0.74 and RMSE of 2.15 on a 28-day holdout. Claude also created CLAUDE.md project context file and updated the Week 1 checklist in docs/project_plan.md.
Human Review: Verified the feature matrix shape (5.8M rows, 22 columns) and confirmed the lag/rolling logic is leakage-free. Confirmed tweedie objective is appropriate for sparse retail count data. Accepted WRMSSE 0.74 as a solid Week 1 baseline (top 10% on M5 is ~0.50, room to improve in Week 2). Ticked off LightGBM baseline running in project plan.

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
Tool Used: Claude (claude.ai)
Task: Converting the 3-week project plan into a markdown file for GitHub tracking
AI Contribution: Claude converted the interactive HTML project plan into a structured markdown file (project_plan.md) with GitHub-renderable tables per week, interactive task checkboxes (- [ ]), a Q&A preparation table, and risk callouts. Structured for the docs/ folder alongside the existing genai_transparency_log.md.
Human Review: Confirmed structure matches the repo layout visible in the GitHub screenshot. Verified checkboxes render correctly on GitHub. Approved file for commit into docs/.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Generating a detailed 3-week project plan PDF broken down by day, task, owner, and subtasks
AI Contribution: Claude produced a multi-page PDF (MerchAI_3Week_Plan.pdf) with day-by-day task breakdowns across all three weeks, including owner badges (Tech / Business / Whole team / Presentation), detailed subtask lists, end-of-week checklists, risk warnings, and a team split recommendation.
Human Review: Reviewed all tasks against the rubric requirements and confirmed coverage of both deliverables (business plan + prototype). Identified that the PDF was Claude.ai-environment-dependent when opened in Safari - prompted conversion to PDF format for team sharing.

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
Task: Adding a marketing recommendation dimension to the product - identifying which products to promote and how
AI Contribution: Claude proposed a "Promote This" module using sell-through velocity, competitor stock signals, and margin data to surface SKUs worth actively marketing. It also suggested layering sentiment analysis (Week 1 course content) on product reviews to detect early demand signals, and a channel recommendation logic (email vs social vs in-store placement) based on product profile.
Human Review: Confirmed the "Promote This" module and channel recommendation logic as concrete additions. Adopted the sentiment signal idea as a differentiating feature. Kept the implementation rule-based (rules drive logic, LLM writes copy) to reduce hallucination risk.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Expanding the feature set to make the product more AI-native and better aligned with the course curriculum
AI Contribution: Claude proposed 7 new features: RAG-powered category intelligence, a conversational "Ask Your Data" interface, multimodal competitor monitoring, an agentic execution loop, a hallucination guard layer, confidence & uncertainty display, and a data privacy architecture. Each was linked to a specific course week (Weeks 3-5).
Human Review: Confirmed RAG layer, hallucination guard, and conversational interface as the three priority additions. Deferred multimodal and agentic mode to nice-to-have status. Merged confidence display into the hallucination guard concept rather than treating it as a standalone feature.

---

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
