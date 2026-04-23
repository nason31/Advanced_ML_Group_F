# MerchAI — Feature Overview

> The AI merchandiser every Walmart has, but the 500-store chain can't afford.

## Key Metrics

| Target market | Revenue range | Pricing model | Gross margin | LLM cost / day | Customer ROI |
|---------------|---------------|---------------|--------------|----------------|--------------|
| 50–500 store retailers | €100M – €2B | €200–500 / store / mo | 75%+ | €0.10 – 0.30 | ~4× on €500M retailer |

---

## Feature Table

🟢 New / added feature &nbsp;&nbsp; 🔵 Core (original draft)

| Feature / Module | What it does | Tech / data source | Rubric criterion |
|------------------|--------------|-------------------|-----------------|
| 🔵 **Daily agent briefing** *(per store / buyer)* | Every morning: markdown candidates, restock priorities, promo watchlist, category insights — each cited to underlying data with one-click execute. | POS (CSV → live), LightGBM / N-BEATS / Chronos forecasting, LLM reasoning layer | Technical execution, Commercial feasibility |
| 🔵 **Markdown engine** | Identifies slow-moving SKUs and recommends optimal discount depth with projected margin impact vs. holding. | Sell-through velocity, competitor pricing scrape, calendar events | Commercial innovation |
| 🔵 **Restock priorities** | Flags SKUs at risk of stockout based on demand forecast + current stock cover, with expedite recommendation. | Hierarchical time-series models, weather API, local event calendar | Technical execution |
| 🟢 **Promote This module** | Identifies high sell-through, high-margin SKUs worth actively marketing. Recommends channel: email, social push, or in-store placement based on product profile. | Promotion flags from M5 dataset, sell-through velocity, margin data | Commercial innovation |
| 🟢 **Sentiment signal layer** | Scrapes product reviews / social mentions and runs sentiment analysis. Rising positive sentiment + flat in-store sales = early "push this" signal. | Sentiment analysis (Week 1 course content), Google Reviews / social API | Technical execution, AI-first design |
| 🟢 **RAG knowledge base** | Retrieves relevant past campaign results, seasonal playbooks, and competitor history before LLM generates each recommendation. Grounds output in real context. | RAG + embeddings (Week 3 content), vector store of historical retailer data | Technical execution, Defensibility |
| 🟢 **Conversational "Ask Your Data"** | Natural language queries over store data: "Why did running shoes underperform last week?" Best demo moment in the pitch. | LLM + RAG over POS data, prompt engineering | Technical execution, Presentation |
| 🟢 **Multimodal competitor monitor** | Ingests competitor flyer PDFs or screenshots and extracts pricing / promo data automatically for the reasoning layer. | Multimodal LLM (Week 3), PDF / image parsing | Technical execution, Defensibility |
| 🟢 **Agentic execution mode** | Optional autonomous mode: low-risk, high-confidence actions (e.g. routine restocks below threshold) execute automatically with manager notification only. | Agentic AI / tool-calling (Week 4), confidence threshold logic | Technical execution, AI-first design |
| 🟢 **Hallucination guard** | Every LLM claim is fact-checked against the underlying database before reaching the manager. Mismatches are suppressed, not surfaced. | AI Safety (Week 5), output verification layer | Defensibility & Safety |
| 🟢 **Confidence display** | Each recommendation shows model confidence (e.g. 90% vs 55%) derived from forecast prediction intervals. Builds manager trust. | Prediction intervals from forecasting models | Defensibility & Safety |
| 🔵 **Feedback learning loop** | Manager accepts / rejects / modifies → outcome measured → preference data fed back to improve next iteration. The moat compounds over time. | Action logging, outcome tracking, preference fine-tuning | Defensibility (moat) |
| 🟢 **Data privacy architecture** | Tenant isolation (Chain A never sees Chain B data), option for on-premise / private cloud deployment for sensitive clients. | Auth layer, tenant-scoped data stores | Defensibility & Safety |
| 🔵 **Full-stack dashboard** | Per-manager views with briefing cards, accept/reject actions, audit trail of past decisions and outcomes. | Streamlit or Next.js frontend | Technical execution (deliverable) |
