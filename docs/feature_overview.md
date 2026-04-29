# MerchAI — Feature Overview

> The AI merchandiser every Walmart has, but the 500-store chain can't afford.

## Key Metrics

| Target market | Revenue range | Pricing model | Gross margin | LLM cost / day | Customer ROI |
|---------------|---------------|---------------|--------------|----------------|--------------|
| 50-500 store retailers | €100M - €2B | €200-500 / store / mo | 75%+ | €0.10 - 0.30 | ~4x on €500M retailer |

---

## Built Features

🟢 New / added feature &nbsp;&nbsp; 🔵 Core (original draft)

| Feature / Module | What it does | Tech / data source | Rubric criterion |
|------------------|--------------|-------------------|-----------------|
| 🔵 **Daily agent briefing** | Every morning: markdown candidates, restock priorities, promo watchlist - each cited to underlying data with accept/reject actions. | LightGBM forecasting, LLM reasoning layer, M5 dataset | Technical execution, Commercial feasibility |
| 🔵 **Markdown engine** | Identifies slow-moving SKUs (forecast trending down) and recommends a discount to clear stock before it ages. | Sell-through velocity via LightGBM delta_pct, M5 dataset | Commercial innovation |
| 🔵 **Restock priorities** | Flags SKUs with moderate upward forecast momentum to avoid stockout. | LightGBM demand forecast, delta_pct signal | Technical execution |
| 🟢 **Promote This module** | Identifies SKUs forecast >+15% above 28-day baseline - strong momentum worth amplifying. Recommends channel action (end-cap, flyer, BOGO) via Claude. | delta_pct threshold logic, LLM channel reasoning | Commercial innovation |
| 🟢 **RAG knowledge base** | Retrieves relevant M5-derived context (SNAP lift, event effects, YoY trends, price elasticity) before each LLM call. Grounds output in real data. | ChromaDB, all-MiniLM-L6-v2 embeddings, 57 M5 context docs | Technical execution, Defensibility |
| 🟢 **Hallucination guard** | Every LLM claim is fact-checked against forecast data before reaching the manager. Intent check (54 retail action phrases) + numeric check (cited % vs actual delta). Mismatches are flagged and surfaced with full transparency - visible on every briefing card. | Output verification layer, regex numeric extraction | Defensibility & Safety |
| 🟢 **Confidence display** | Each briefing card shows a High / Medium / Low confidence badge (green / amber / red) derived from delta_pct magnitude, plus the exact delta. Gives managers an at-a-glance signal strength indicator. | delta_pct thresholds (>100% High, 30-100% Medium, <30% Low) | Defensibility & Safety |
| 🟢 **Conversational "Ask Your Data"** | Natural language Q&A over store data below the briefing. "Why is FOODS_3 spiking?" - Claude answers using live forecast summary + RAG context, with citations. | src/llm/qa.py, reuses forecast + RAG + Claude layer | Technical execution, Presentation |
| 🔵 **Feedback learning loop** | Manager accepts / rejects / modifies - decision logged to audit trail with timestamp. Foundation for preference learning. | Streamlit session state, audit trail component | Defensibility (moat) |
| 🔵 **Full-stack dashboard** | Per-manager briefing cards (colour-coded by type), accept/reject buttons, audit trail, guard check expander, Ask Your Data section. | Streamlit frontend | Technical execution (deliverable) |

---

## Planned Features - Not Yet Built

| Feature / Module | What it does | Effort | Grade gain | Priority |
|------------------|--------------|--------|------------|----------|
| 🟢 **Sentiment signal layer** | Scrapes product reviews / social mentions and runs sentiment analysis for early demand signals. | **High** - needs external API, M5 has no sentiment data so output would be synthetic | **Low** - hard to demo credibly with fake data | Skip |
| 🟢 **Multimodal competitor monitor** | Ingests competitor flyer PDFs / screenshots and extracts pricing data for the reasoning layer. | **High** - needs real competitor data source, PDF/image parsing | **Low** - nothing credible to show without real flyers | Skip |
| 🟢 **Agentic execution mode** | Low-risk actions execute automatically above a confidence threshold, manager notified only. | **Medium** - confidence threshold + auto-execute logic | **Low** - demo becomes risky; a bad auto-action during presentation is a disaster | Skip |
