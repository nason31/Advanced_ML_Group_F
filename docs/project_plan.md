# MerchAI — 3-Week Project Plan

> The AI merchandiser every Walmart has, but the 500-store chain can't afford.

**Course:** 2758-T4 Advanced Topics in Machine Learning — Nova SBE  
**Team size:** 4 students | **Presentation:** Week 6

**Team split:** 2 on Tech (data + LLM + frontend) · 1 on Business plan + pitch deck · 1 floats between both and owns demo script + GenAI log. Rotate presentation speaking parts equally.

---

## Legend

| Badge | Role |
|-------|------|
| 🔵 Business | 1–2 people |
| 🟢 Tech | 1–2 people |
| 🟠 Presentation | — |
| ⚪ Whole team | — |

---

## Week 1 — Foundation & Alignment
> **Goal:** Everyone aligned, work split clearly, data in hand, and the business case skeleton written before the weekend of Day 7.

| Owner | Task | Description |
|-------|------|-------------|
| ⚪ Whole team | Kick-off meeting | Agree on final feature scope, name (MerchAI?), tech stack, and who owns what. Split into Biz track and Tech track. |
| 🔵 Business | Business plan draft | Target market, value proposition, GTM strategy, pricing model, and unit economics (token costs, margin). |
| 🔵 Business | ROI story | Build the "0.5% margin improvement on €500M retailer = €2.5M/year vs €600k software bill" narrative with numbers. |
| 🟢 Tech | Data setup | Download M5 Forecasting dataset from Kaggle. Explore and clean. Set up basic forecasting model (LightGBM baseline). |
| 🟢 Tech | Architecture design | Map out the full stack: data layer → forecasting → LLM reasoning → RAG → frontend. Choose Streamlit or Next.js. |
| ⚪ Whole team | Start GenAI log | Required deliverable. Start documenting every AI tool used (Claude, ChatGPT) with prompts, outputs, and decisions made. |

### End of Week 1 checklist
- [x] Team roles agreed
- [x] GenAI log started
- [x] M5 data downloaded
- [x] LightGBM baseline running
- [x] GitHub repo set up
- [x] Business plan draft started
- [ ] ROI numbers calculated
- [ ] Competitor research done

> ⚠️ **Risk:** Tech getting lost in model tuning. Week 1 forecasting only needs to be "good enough to demo" — a MAPE of 25% is fine.

---

## Week 2 — Build the Prototype
> **Goal:** A working, deployed prototype by end of week. The LLM must be generating real recommendations from real M5 data on a real URL.

| Owner | Task | Description |
|-------|------|-------------|
| 🟢 Tech | LLM reasoning layer | Connect LightGBM outputs to an LLM prompt. Generate human-readable markdown + restock recommendations with citations. |
| 🟢 Tech | RAG layer | Build a small vector store of historical campaign data. Retrieve context before each LLM call. Show it grounding a recommendation. |
| 🟢 Tech | Promote This module | Identify high sell-through, high-margin SKUs. Add sentiment signal if time allows. Output channel recommendation. |
| 🟢 Tech | Frontend dashboard | Build the Streamlit / Next.js UI. Daily briefing cards, accept/reject buttons, audit trail. Must be deployable (Firebase / Streamlit Cloud). |
| 🔵 Business | Moat & safety section | Write up: feedback loop moat, hallucination guard approach, data privacy / tenant isolation policy. |
| 🔵 Business | Pitch deck skeleton | Draft slide outline: problem → solution → demo → tech stack → business model → moat → ask. No full design yet. |

### End of Week 2 checklist
- [x] LLM reasoning layer working
- [x] RAG layer returning context
- [x] Promote This module done
- [x] Dashboard UI built
- [ ] Deployed to live URL (config ready, not confirmed live)
- [ ] Business plan draft complete
- [ ] Pitch deck first draft done
- [ ] Moat & safety section written

> ⚠️ **Risk:** Deployment always takes longer than expected. Deploy a "hello world" version by Day 10 so you know the pipeline works, then iterate on top of it.

---

## Week 3 — Polish & Rehearse
> **Goal:** A rehearsed, confident pitch with a live demo that works every time. No surprises on presentation day.

| Owner | Task | Description |
|-------|------|-------------|
| 🟢 Tech | Demo scenario | Lock the live walkthrough: "Store #7, Monday morning. 3 markdown recs, 1 promo alert. Accept one — show margin impact + audit trail." |
| 🟢 Tech | Hallucination guard | ✅ Implement output verification: LLM claim vs database cross-check. Show it catching a discrepancy in the demo. |
| ⚪ Whole team | Finalize pitch deck | Full design pass on slides. Tight narrative, no walls of text. Investor pitch tone — every slide earns its place. |
| 🔵 Business | GenAI transparency log | Compile the full appendix of AI tool usage. Required for Deliverable 1. Include prompts, outputs, and what you changed manually. |
| 🟠 Presentation | Dry runs | At least 2 full run-throughs with the live demo. Time it. Practice the "what's your moat?" and "why not OpenAI?" questions. |
| 🟠 Presentation | Q&A prep | Prepare answers: hallucination risk, data privacy, forecasting accuracy claims, GTM first customer, pricing justification. |

### Presentation day checklist
- [ ] Demo works on presentation laptop
- [ ] Backup video recorded
- [ ] Live URL confirmed up
- [ ] GenAI log finalized
- [ ] All Q&A answers practiced
- [ ] Pitch timed at 10–12 min
- [ ] Everyone knows their section
- [x] Hallucination guard demo ready

> ⚠️ **Risk:** After Day 17 the answer to "should we add X?" is always **no**. A stable demo beats a feature-rich broken one every time.

---

## Key Q&A to prepare

| Question | Answer |
|----------|--------|
| Why can't OpenAI just build this? | Requires POS integration, retail-specific forecasting stack, and a decision log that compounds — none of which OpenAI will build as a general feature. |
| How do you handle hallucinations? | Output verification layer: every numeric LLM claim cross-checked against source data before display. Mismatches are suppressed. |
| What's your forecasting accuracy? | M5 benchmark, top 10% leaderboard is the target. LightGBM baseline is the starting point. |
| How do you get your first customer? | Direct outreach to regional chains, or partnership with an ERP vendor as a distribution channel. |
| What's the data privacy story? | Tenant isolation (Chain A never sees Chain B data), GDPR compliance, on-premise deployment option. |
