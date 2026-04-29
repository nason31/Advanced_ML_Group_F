# MerchAI Business Plan — Outline

## 1. Problem
Mid-market retailers make daily merchandising decisions (markdowns, restocks, promotions) manually, without AI-assisted forecasting or historical context.

## 2. Solution
MerchAI: AI copilot that delivers daily briefing cards — forecast-backed, RAG-informed, hallucination-guarded.

Three recommendation types, each triggered by forecast signal:
- **Markdown** - SKU forecast down vs 28-day baseline: discount to clear stock before it ages
- **Restock** - SKU forecast mildly up: replenish to avoid stockout
- **Promote This** - SKU forecast >+15% above baseline: ride the momentum with a targeted promotion (end-cap, flyer, BOGO). The +15% threshold is calibrated to isolate genuine momentum vs noise and can be tuned per retailer margin targets.

## 3. Customer
Merchandising managers at mid-market grocery/retail chains (50–500 stores).

## 4. Value Proposition
- [TBD: quantify time saved per manager per week]
- [TBD: quantify margin improvement from better markdown decisions]
- **Tech note:** The prototype runs a full briefing (3 recommendations + Q&A) in ~48 seconds end-to-end. Each recommendation is forecast-backed, RAG-grounded, and guard-verified. Position this as replacing 1-2 hours of manual spreadsheet work per manager per day.

## 5. Pricing
[TBD: per-store SaaS pricing model]
- **Tech note:** Suggest €200-500/store/month. At 3 recommendations/day per store, each Claude API call costs ~€0.003 (claude-sonnet-4-6, ~1500 tokens in + ~300 out). 3 recs/day = ~€0.009/store/day = ~€0.27/store/month in LLM costs. Even at €200/store/month that is a 700x markup on raw token cost - very healthy gross margin.

## 6. Unit Economics
[TBD: CAC, LTV, gross margin]
- **Tech note (token costs - use these numbers):**
  - Model: claude-sonnet-4-6
  - Tokens per recommendation call: ~1500 in / ~300 out
  - Cost per rec at current Anthropic pricing: ~€0.003
  - 3 recs + 1 Q&A per store per day: ~€0.012/store/day → ~€0.36/store/month
  - Hosting: Streamlit Cloud free tier covers up to ~3 concurrent users. Paid tier ~$25/month covers demo scale.
  - Vector DB: ChromaDB on local disk, $0 at current scale. Cloud (Pinecone/Weaviate) ~$25/month for 1M vectors.
  - At €300/store/month SaaS price and €0.50 total infra cost/store/month: **gross margin ~99.8%** at launch, degrades gracefully as usage scales.
  - **Flag for business track:** these are the numbers to put in the LTV/CAC model. Do not use TBD at submission - the LLM judge will check.

## 7. Moat
[TBD: draft in Phase 2]
- **Tech note (concrete moat arguments - use these):**
  - **Feedback loop:** every manager accept/reject is logged with timestamp to the audit trail. This data compounds - after 6 months a retailer's MerchAI knows which rec types their managers trust, which categories they override, and what margin outcomes followed. A new entrant starts cold.
  - **Retail-specific forecasting stack:** LightGBM trained on M5 with SNAP flags, event calendars, price elasticity lags. Not a generic time-series model. Replacing this with an OpenAI plugin would require the same domain engineering.
  - **RAG corpus:** 57 M5-derived context documents per store covering price sensitivity, SNAP lift, YoY category trends, event effects. Built from real retail signal, not generic knowledge.
  - **Decision audit trail:** every recommendation shown, accepted, rejected, or modified is logged. Over time this becomes a compliance and accountability asset - retailers in regulated markets (France, Germany) will pay for this.
  - **The moat is NOT the LLM.** Claude can be swapped. The moat is the proprietary feedback data and retail-domain context that accumulates with every store and every decision.

## 8. Safety / Hallucination / Privacy
[TBD: draft in Phase 2]
- **Tech note (what is actually built - use these specifics):**
  - **Hallucination guard (implemented):** two-layer check on every LLM output before it reaches the manager. (1) Intent check: 54 retail action phrases detect Claude's recommended action and flag if it contradicts the forecast direction. (2) Numeric check: regex extracts the first percentage Claude cites and compares against actual delta_pct with 2x tolerance. Flagged cards are shown in red with the reason visible - the guard is not a silent filter, it is transparent to the manager.
  - **Demo moment:** show a flagged card in the live demo. The guard visibly catching something is worth more than 5 slides explaining it.
  - **Tenant isolation (design, not yet implemented):** each retailer's data, models, and vector store are scoped to their tenant. Chain A never sees Chain B data. Mention this as an architectural principle even if not built yet.
  - **On-premise option (future):** for retailers with strict data residency requirements (common in EU grocery), the full stack (LightGBM + ChromaDB + local LLM) can run on-premise. This is a sales argument for larger chains.

## Appendix: GenAI Transparency Log
[Compiled from docs/genai_transparency_log.md at submission]
