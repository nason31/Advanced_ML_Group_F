# MerchAI — Claude Context File

> The AI merchandiser every Walmart has, but the 500-store chain can't afford.

This file gives Claude instant context on the project, the grading criteria, how we work together, and what "winning" looks like.

---

## 1. What This Project Is

**MerchAI** is an AI-powered merchandising copilot for mid-market retail chains (50-500 stores). Every morning it delivers a daily briefing: forecast-backed markdown recommendations, restock priorities, and promotion candidates. Managers accept, reject, or modify. The system learns from every decision.

**Target customer:** Merchandising managers at grocery and general retail chains who currently make these decisions manually in spreadsheets.

**The core value:** 0.5% margin improvement on a €500M retailer = €2.5M/year. The software costs €600k/year. That is a 4x ROI story.

**Tech stack:** Python, LightGBM, ChromaDB (RAG), Claude API (LLM reasoning), Streamlit (frontend), M5 Forecasting dataset.

---

## 2. Course & Grading Context

**Course:** 2758-T4 Advanced Topics in Machine Learning
**Institution:** Nova School of Business and Economics, Portugal
**Program:** Masters in Business Analytics
**Professor:** Qiwei Han, Ph.D.
**Presentation:** Week 6 (3-week project, teams of 4)

### The 4 Evaluation Criteria

| # | Criterion | What it really means |
|---|-----------|---------------------|
| 1 | **Commercial Innovation & Feasibility** | Real pain point, credible market size, sustainable unit economics (token costs, margins, CAC, LTV) |
| 2 | **Technical Execution & Prototype** | Full-stack solution that actually runs. UI + AI backend. Deployed to a live URL. |
| 3 | **Defensibility & Safety** | A real moat (not just features). Hallucination guard. Data privacy / tenant isolation. |
| 4 | **Presentation & Delivery** | Investor-pitch quality. Confident live demo. Handles hard Q&A. |

### The Judging Panel

Grading is done by **two judges in parallel:**

- **Human judges:** PhD-level faculty evaluating business logic, market fit, and presentation skills.
- **LLM-as-a-Judge:** The business plan and technical architecture are fed into a specialised evaluation LLM. It pressure-tests logic, simulates edge cases, and evaluates cost structure.

**Critical warning from the brief:** The AI judge is highly critical of "wrapper" startups with no real moat. A thin Claude API wrapper with a pretty UI will score poorly. We need genuine defensibility arguments: the feedback loop, the retail-specific forecasting stack, the POS data integration, the decision audit trail that compounds over time.

### Academic Integrity

All GenAI usage must be logged in `docs/genai_transparency_log.md`. Unacknowledged use results in grade deduction or zero. Log every session.

---

## 3. Deliverables

### Deliverable 1: Business Plan
- Target market, value proposition, GTM strategy
- Unit economics: token costs per transaction, hosting, vector DB storage, gross margin
- GenAI Transparency Log as appendix (compiled from `docs/genai_transparency_log.md`)
- **Done when:** every TBD in `docs/business_plan/outline.md` is filled with real numbers

### Deliverable 2: Full-Stack Deployable Solution
- Working prototype with UI (Streamlit) and AI backend
- Deployed to a live URL (Streamlit Cloud target)
- Step-by-step execution visible: from prompt engineering to system integration
- No command-line-only tools
- **Done when:** a non-technical person can open the URL and use it without instructions

---

## 4. Team & Roles

| Person | Track | Owns |
|--------|-------|------|
| Leticia | Tech | Data pipeline, LLM layer, frontend, GenAI log |
| [Teammate 2] | Tech | Forecasting model, RAG layer, deployment |
| [Teammate 3] | Business | Business plan, pitch deck, ROI story |
| [Teammate 4] | Float | Demo script, GenAI log, presentation bridge |

---

## 5. Architecture & Key Files

```
data/raw/               M5 Forecasting dataset (CSV files)
src/data/loader.py      load_m5() - raw DataFrames
src/data/features.py    build_features() - feature matrix
src/forecast/model.py   train() / predict() via LightGBM
src/forecast/evaluate.py WRMSSE metric logging
src/rag/retriever.py    retrieve() - ChromaDB vector store
src/llm/reasoner.py     reason() - Claude API call with forecast + RAG context
src/llm/guard.py        check() - hallucination guard, cross-checks LLM claims
src/recommendations/engine.py  run_pipeline() - returns list[Rec]
app/main.py             Streamlit UI: briefing cards, accept/reject, audit trail
docs/project_plan.md    3-week plan with checklists
docs/genai_transparency_log.md  Required deliverable - log every AI session here
docs/business_plan/outline.md  Business plan (many TBDs still to fill)
docs/architecture.md    Full stack diagram
docs/feature_overview.md       Feature table with rubric mapping
```

---

## 6. Working Style

**Always explain before doing.** For every task: say what you want to do and how, wait for confirmation, then execute step by step with clear structure. Never do everything at once.

**Push for the highest grade.** If you see something that is mediocre, say so and suggest what good looks like. Do not just complete the task as asked.

**UX matters.** The Streamlit app needs to look genuinely good. This is a demo to investors (and an LLM judge). If something looks like a student project, flag it and fix it.

**No long dashes.** Use short dashes (-) only, never em dashes or double dashes.

**GenAI log discipline.** After any substantive session, remind Leticia to add an entry to `docs/genai_transparency_log.md`. It is a required deliverable and must be honest.

---

## 7. Grade Pushes — Things to Flag Proactively

These are the places where "good enough" will cost points. Raise them whenever relevant:

- **Moat argument:** Can we articulate why MerchAI cannot be replicated by OpenAI adding a retail plugin? The answer must be specific: proprietary feedback loop, POS integration depth, decision audit trail that compounds. Push this in every business plan section.
- **Unit economics:** The business plan needs real numbers. Token cost per briefing, vector DB cost per store, gross margin at scale. No TBDs at submission.
- **Live demo reliability:** The demo must work every single time. Flaky demos lose investor pitches. Test it cold, on a clean machine, at least twice before presentation day.
- **Hallucination guard visibility:** The guard must be *visible in the demo*, not just implemented. Show it catching something. That is a Defensibility point sitting on the table.
- **Confidence scores:** Show prediction intervals on recommendations. Builds trust, maps directly to a rubric criterion.
- **GenAI log completeness:** The log must cover ideation, coding, AND writing. If a section of the business plan was AI-assisted, it needs an entry. The LLM judge will check this.
