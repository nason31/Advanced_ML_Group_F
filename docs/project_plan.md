# MerchAI — 3-Week Project Plan

> The AI merchandiser every Walmart has, but the 500-store chain can't afford.

**Course:** 2758-T4 Advanced Topics in Machine Learning — Nova SBE  
**Team size:** 4 students | **Presentation:** Week 6

**Team split:** 2 on Tech (data + LLM + frontend) · 1 on Business plan + pitch deck · 1 floats between both and owns demo script + GenAI log. Rotate presentation speaking parts equally.

---

## Legend

| Badge | Role |
|-------|------|
| 🔵 Business | Alex |
| 🟢 Tech | Leticia, Justus |
| 🟠 Presentation | Marie |
| ⚪ Whole team | Leticia, Justus, Alex, Marie |

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

| Owner | Task | Status | Description |
|-------|------|--------|-------------|
| 🟢 Tech | Hallucination guard | ✅ Done | Intent check (54 phrases) + numeric check (cited % vs actual delta). Visible on every card. |
| 🟢 Tech | Confidence display | ✅ Done | High / Medium / Low badge on every card derived from delta_pct. |
| 🟢 Tech | Ask Your Data | ✅ Done | Natural language Q&A grounded in live forecast + RAG context. |
| 🟢 Tech | Deploy to live URL | ❌ Open | Push to Streamlit Cloud, confirm live URL works, add ANTHROPIC_API_KEY to secrets UI. Biggest remaining blocker. |
| 🟢 Tech | Lock demo scenario | ❌ Open | Pick store (CA_1 recommended), pick date, run once, screenshot the output. Script: generate briefing → review confidence badges + guard checks → accept one → ask a question. |
| 🟢 Tech | UI polish | ❌ Open | Check app looks professional on a large screen. Font sizes, spacing, card layout. This is a demo to investors - it must not look like a student project. |
| 🟢 Tech | Model improvement | Optional | WRMSSE currently 0.74 - goal was <0.60. Tune num_leaves, add more lag windows. Only attempt if deployment is confirmed stable. |
| 🔵 Business | Business plan - unit economics | ❌ Open | Tech notes already in outline.md with exact numbers. Alex to write up the full section - no TBDs allowed at submission. |
| 🔵 Business | Business plan - moat & safety | ❌ Open | Tech notes already in outline.md with 4 moat arguments and guard specifics. Alex to write up. |
| 🔵 Business | ROI numbers + competitor research | ❌ Open | 0.5% margin improvement story needs real comparable numbers. Research 1-2 competitors (Relex, Blue Yonder) for the "why not them" answer. |
| 🟠 Presentation | Pitch deck design | ❌ Open | Marie owns. Slide order: problem → solution → demo → tech stack → business model → moat → ask. Investor pitch tone, no walls of text. |
| 🟠 Presentation | Demo script | ❌ Open | Marie owns. Write exact words for each section. Lock which team member says what. |
| ⚪ Whole team | GenAI transparency log | ❌ Ongoing | Everyone logs own sessions. Marie compiles final appendix. LLM judge checks for completeness - no back-filling. |
| ⚪ Whole team | Finalize pitch deck | ❌ Open | Full design pass. Every slide earns its place. |
| 🟠 Presentation | Dry runs | ❌ Open | At least 2 full run-throughs with the live demo cold (fresh browser, no cached state). Time it. |
| 🟠 Presentation | Q&A prep | ❌ Open | Practice answers to: what's your moat, why not OpenAI, hallucination risk, data privacy, forecasting accuracy, GTM first customer. |

### Presentation day checklist
- [ ] Demo works on presentation laptop (cold start, fresh browser)
- [ ] Backup video recorded
- [ ] Live URL confirmed up
- [ ] GenAI log finalized and complete for all 4 members
- [ ] Business plan TBDs all filled - no placeholders at submission
- [ ] All Q&A answers practiced out loud
- [ ] Pitch timed at 10-12 min
- [ ] Everyone knows their section
- [x] Hallucination guard demo ready
- [x] Confidence display live
- [x] Ask Your Data live

> ⚠️ **Risk:** After Day 17 the answer to "should we add X?" is always **no**. A stable demo beats a feature-rich broken one every time.

---

## Key Q&A to prepare

| Question | Answer |
|----------|--------|
| Why can't OpenAI just build this? | Requires POS integration, retail-specific forecasting stack, and a decision log that compounds — none of which OpenAI will build as a general feature. |
| How do you handle hallucinations? | Two-layer guard on every LLM output: intent check (54 retail action phrases detect contradictions with forecast direction) + numeric check (cited % vs actual delta_pct, 2x tolerance). Mismatches are flagged and shown to the manager - transparent, not silently suppressed. |
| What's your forecasting accuracy? | LightGBM baseline achieves WRMSSE 0.74 on M5 holdout across CA_1, CA_2, TX_1. Top 10% on M5 leaderboard is ~0.50 - room to improve with further tuning. |
| How do you get your first customer? | Direct outreach to regional chains, or partnership with an ERP vendor as a distribution channel. |
| What's the data privacy story? | Tenant isolation (Chain A never sees Chain B data), GDPR compliance, on-premise deployment option. |
