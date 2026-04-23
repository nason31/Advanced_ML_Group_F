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

<!-- Add entries below — newest first -->

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
AI Contribution: Claude converted the full HTML feature overview table into a clean GitHub-compatible markdown file (feature_overview.md), preserving the core vs. new feature tags as emoji indicators (🔵 / 🟢), the metrics table, and all 14 feature rows with tech stack and rubric columns.
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
Human Review: Reviewed all tasks against the rubric requirements and confirmed coverage of both deliverables (business plan + prototype). Identified that the PDF was Claude.ai-environment-dependent when opened in Safari — prompted conversion to PDF format for team sharing.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Creating a high-level 3-week project plan and role split for a team of 4
AI Contribution: Claude generated a structured week-by-week plan covering: Week 1 (foundation & alignment — kickoff, data setup, business plan draft), Week 2 (prototype build — LLM layer, RAG, Promote This, dashboard, deployment), Week 3 (polish & rehearse — demo hardening, hallucination guard, dry runs, Q&A prep). Included suggested team split: 2 tech, 1 business, 1 floats.
Human Review: Confirmed the 3-week structure fits the course timeline. Adopted the 2-tech / 1-business / 1-float role split. Requested a more detailed day-by-day breakdown as a follow-up.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Adding a marketing recommendation dimension to the product — identifying which products to promote and how
AI Contribution: Claude proposed a "Promote This" module using sell-through velocity, competitor stock signals, and margin data to surface SKUs worth actively marketing. It also suggested layering sentiment analysis (Week 1 course content) on product reviews to detect early demand signals, and a channel recommendation logic (email vs social vs in-store placement) based on product profile.
Human Review: Confirmed the "Promote This" module and channel recommendation logic as concrete additions. Adopted the sentiment signal idea as a differentiating feature. Kept the implementation rule-based (rules drive logic, LLM writes copy) to reduce hallucination risk.

---

Date: 2026-04-22
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Expanding the feature set to make the product more AI-native and better aligned with the course curriculum
AI Contribution: Claude proposed 7 new features: RAG-powered category intelligence, a conversational "Ask Your Data" interface, multimodal competitor monitoring, an agentic execution loop, a hallucination guard layer, confidence & uncertainty display, and a data privacy architecture. Each was linked to a specific course week (Weeks 3–5).
Human Review: Confirmed RAG layer, hallucination guard, and conversational interface as the three priority additions. Deferred multimodal and agentic mode to nice-to-have status. Merged confidence display into the hallucination guard concept rather than treating it as a standalone feature.
