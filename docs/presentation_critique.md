# MerchAI - Pre-Presentation Checklist

Generated from five evaluation rounds: VC + professor, AI infrastructure expert, LLM-as-a-Judge wrapper risk, full panel grading, and code review. Triaged for one-week execution by a four-person student team.

Status key: `[ ]` Not started | `[~]` In progress | `[x]` Done

Owner abbreviations: L = Leticia | J = Justus | A = Alex | M = Marie

**Triage lens:** The LLM judge checks unit economics, deployability, AI necessity, and moat. Human judges check business logic, technical execution, and presentation quality. Everything here maps directly to one of those.

---

## Block 1 - Business Plan Fixes (Owner: Alex)

Text changes only. Each item is one paragraph or one table row. Do these first - the LLM judge reads the business plan directly and these are the specific vulnerabilities it will probe.

- [ ] **Add cash burn curve and funding ask.** The financial model proves break-even at 79 stores but never shows how long it takes to get there or how much capital is needed. Add a Month 0-12 cash position view. Formula: €21,500/month x 7 months to first revenue = ~€150k minimum burn before break-even.

- [ ] **Replace "91% gross margin" with "72% fully-loaded gross margin."** Silicon-only margin is 91%. Fully loaded (adding implementation time per retailer + customer success + support) is 70-75%. Use the correct figure and add one sentence explaining the distinction. The LLM judge will specifically cross-check this number.

- [ ] **Add SAP, Oracle, and Salesforce to the competitive table.** These three own the ERP relationships of every retailer in the target segment and have active AI roadmaps (SAP Joule, Salesforce Einstein). The mitigation is defensible - they require IT-heavy enterprise deployments that a Head of Buying cannot approve as a 90-day experiment - but it must appear in the document. Its absence is the most visible gap in the competitive section.

- [ ] **Acknowledge the 0.5% ROI claim is borrowed from enterprise deployments.** Nextail, McKinsey, and BCG references are from fully integrated enterprise tools. Add one sentence: "We anchor at the floor of independently published ranges; the 90-day pilot business review will produce the first MerchAI-specific data point." Honest framing is stronger than an unqualified claim.

- [ ] **Fix the Phase 1 CAC calculation.** €8,000 values founder time at zero. Two engineers at 50% of their time for 6 months = ~€30,000 in allocated salary cost alone. Revise to €20,000-€35,000. The LTV/CAC ratio is still healthy at 43-75:1 - no need to hide this.

- [ ] **Fix the moat argument hierarchy.** The four moat claims are given equal weight but have radically different defensibility. Reorder: (1) decision audit trail - the real compounding moat; (2) workflow embedment - genuine switching cost once habituated; (3) per-retailer trained models - proprietary once real data is ingested; (4) guard and RAG - product quality, not defensibility. The guard is not a moat. Say so explicitly.

- [ ] **Address the cold-start problem in the moat section.** One sentence: "The free pilot is how we acquire the first customer before the moat exists. Day 1 of the pilot is Day 1 of proprietary data collection." This closes the circular argument (moat needs customers, customers need moat) that a judge will raise.

- [ ] **Add one sentence on liability.** "MerchAI is a recommendation tool; the manager retains final authority on every action. The audit trail records which recommendations were accepted and what outcomes followed." This belongs in the defensibility or risk section.

- [ ] **Add the M5-to-real-data transition paragraph.** The RAG corpus contains SNAP benefit patterns - a US government programme that does not exist in DACH or Iberia. Add explicitly: "The M5-derived corpus is replaced with EU-specific seasonal calendar events and retailer promotional history during the design partner pilot. LightGBM is retrained on 12 months of the chain's own POS data. This takes two days of data engineering per retailer."

- [ ] **Add churn sensitivity row to the LTV table.** One extra row: LTV at 30% churn = €270,000 / 0.30 = €900,000 per customer. Still healthy. Showing this proves you have stress-tested your own numbers.

- [ ] **Fix the ChromaDB self-hosting claim in the cost table.** State the actual deployment (committed vector store files read by PersistentClient) and its real cost. The current "zero marginal cost self-hosted" claim is inconsistent with a Streamlit Cloud deployment.

---

## Block 2 - Code Fixes (Owner: Leticia + Justus)

These are all small changes. None introduces new logic that could break the demo. Each is directly visible during the live presentation.

- [x] **Cap concurrent Claude calls and add retry in `reasoner.py`.** `engine.py` currently fires `ThreadPoolExecutor(max_workers=len(rec_seeds))` - up to 9 simultaneous API calls. On Streamlit Cloud during a live demo this will hit Anthropic's rate limit and produce `[Recommendation unavailable - ...]` cards on stage. Two fixes: cap `max_workers=3` in `run_pipeline`, and wrap the `client.messages.create` call in `reasoner.py` with a simple retry (3 attempts, 2s backoff). Highest-risk unaddressed item in the codebase.

- [x] **Write guard flags to the audit CSV.** `_append_audit` in `main.py` logs accept/reject but not whether the recommendation was flagged. A manager can accept a guard-flagged recommendation with zero record of it. Add `guard_flagged: bool` as a field to the `_append_audit` call and pass `rec.flagged` from the briefing card actions. Directly contradicts the "AI Safety" defensibility claim if absent.

- [x] **Enable prompt caching in `reasoner.py`.** 4 lines of code. Add `"cache_control": {"type": "ephemeral"}` to the system message content block. The business plan explicitly claims this optimisation - the code currently does not implement it. The LLM judge will check whether stated optimisations are real.

- [x] **Fix `_extract_sku` in `briefing_card.py`.** Add `sku: str = ""` as a field to the `Rec` dataclass in `engine.py`, populate it from `seed["item_id"]` in `_process_seed`, and use `rec.sku` in `briefing_card.py` instead of the regex on LLM text. If Claude's response omits the SKU code, the current regex returns `"-"` and the Product and Department columns go blank mid-demo.

- [x] **Make the AI disclaimer legible.** In `briefing_card.py:104-108`, change `font-size:0.75em` to `font-size:0.85em` and `color:#9ca3af` to `color:#374151`. Move it above the Accept/Reject buttons. The EU AI Act requires AI outputs to be identifiably AI-generated. A grey caption below the buttons that no one reads does not meet that standard. Two CSS value changes.

- [x] **Add the demo mode banner.** One line at the top of the main area in `main.py`: `st.info("Demo mode: running on historical Walmart (M5) data. Recommendations are illustrative - not calibrated to European retail.")`. Prevents a judge from misinterpreting M5 Walmart forecasts as real European retail signals.

- [x] **Rename "High / Medium / Low" confidence to "Strong / Moderate / Weak Signal".** In `engine.py:_compute_confidence` change the return strings. In `briefing_card.py` update `_CONFIDENCE_STYLE` keys. Update the column header from "Confidence" to "Signal". One search-and-replace. Directly addresses the LLM judge's likely challenge: "a delta_pct magnitude is not a confidence interval."

- [x] **Add confirmation dialog for Low/Weak Signal accepts.** A manager can accept a Weak Signal recommendation with one click and no friction. Add a `st.warning` prompt when Accept is clicked on a `confidence == "Low"` (or "Weak Signal" after rename) card: "This recommendation has a weak forecast signal. Confirm?" One conditional in `briefing_card.py`. Directly demonstrable as a safety feature during the live demo.

- [x] **Show the retrieved RAG context in the Details expander.** Pass `context_docs` through from `_process_seed` to the `Rec` dataclass (add `context_docs: list[str] = field(default_factory=list)`). In `briefing_card.py`, add a `st.expander("Context Sources")` below Claude's recommendation text showing the retrieved documents. This makes the RAG architecture visible during the demo - judges can see what Claude was grounded in. Currently RAG is claimed but invisible to anyone watching the demo.

---

## Block 3 - Presentation / Slides (Owner: Marie + Alex)

- [ ] **Add one architecture diagram.** Six-stage pipeline: POS data → LightGBM → RAG retrieval → Claude → Hallucination guard → Briefing UI. Label which stages are deterministic vs. LLM. Show where the audit trail writes. One diagram replaces three pages of prose for a judge seeing the product for the first time.

- [x] **Reframe the moat as a timeline.** One slide or section: "Year 1 we build the data asset. Year 2 we close the retraining loop. Year 3 the moat is structural." More credible than claiming current defensibility from a session-state CSV.

- [x] **Clarify that M5-trained models are the prototype and per-retailer models are the product.** One sentence on the slides: "The demo runs on Walmart M5 data. A pilot retailer's recommendations are generated from models trained on 12 months of their own POS history - genuinely proprietary, impossible to replicate without running the product in that chain." This directly answers the LLM judge's wrapper critique.

- [ ] **Add WRMSSE score to README and slides.** Run `src/forecast/evaluate.py` once and record the WRMSSE. Put it in the README and one slide. Closes "how accurate is the forecast?" cold from any judge. Without a number the answer is "we don't know."

- [ ] **Strengthen the team slide.** Replace "Nova SBE alumni network" with any specific real connection - a named professor contact in retail, an internship at a relevant company, a named association. Vague network language signals no specific lead. If there is no specific lead, say "our entry point is through academia - a research pilot framed as a case study bypasses commercial procurement entirely."

---

## Block 4 - Demo Day Preparation (Owner: Marie)

Talking points to have ready. These questions will be asked. Stumbling is worse than a prepared answer.

- [ ] **"Is this real-time data?"** Prepared answer: "The prototype runs on the M5 Walmart dataset as a stand-in for live POS data. In a real pilot, a daily CSV export from the retailer's ERP replaces this layer - the rest of the pipeline is identical." Say it before they ask, during the demo intro. Do not wait to be caught.

- [ ] **"Where is the audit trail stored?"** Prepared answer: "In this Streamlit demo, decisions persist within a session. In a production pilot, they write to a persistent database from Day 1 - that is the proprietary data asset we are building." Do not refresh the browser mid-demo.

- [ ] **"What makes this more than a Claude wrapper?"** Prepared answer (3 points, in this order): "The LightGBM forecasting stack generates the signal - Claude only translates it into language. The LLM cannot change the numbers. Second, the RAG layer grounds every response in retrieved retail context - Claude is constrained, not freeform. Third, every manager decision is logged and becomes training data that compounds for that specific chain - OpenAI cannot buy that."

- [ ] **Run the demo cold on a clean browser session, twice, before presentation day.** First load takes 10-15 seconds. Click Generate Briefing before starting your intro so the spinner runs during your opening sentence, not mid-demonstration. Verify Accept/Reject buttons log to the audit trail. Verify Ask Your Data returns an answer. Confirm there are no blank SKU fields.

---

## Known Limitations - Prepare, Don't Hide

These are real gaps. Judges who find them via the LLM judge prompts will respect a team that names them first more than one that papers over them.

- **Audit trail is session-scoped in the demo.** The CSV writes to a filesystem that resets on Streamlit Cloud container restart. Decisions persist within a session. Cross-session persistence requires a hosted database - a Phase 1 prerequisite before any real pilot begins.

- **Forecasts are deterministic per date, not real-time.** The date selector maps to the M5 historical range cyclically. A real pilot replaces this with daily POS ingestion.

- **The M5 RAG corpus encodes US demand patterns.** SNAP references, US holiday cycles, and California/Texas consumer behaviour are not applicable to European retail. The corpus is rebuilt from EU data in the design partner pilot.

- **Ask Your Data re-runs the full forecast on every question.** `qa.py:answer_question` calls `forecast_with_names` independently of the main pipeline. The `lru_cache` on `load_model` and `_load_features` avoids re-loading, but `forecast_store` scores the full feature matrix again. Visible as ~2-4s lag on each Q&A response. Low priority - won't crash the demo.

- **Prompt caching is stated but not yet enabled.** The unit economics numbers are correct with caching active. Enabling it is a 4-line change (see Block 2).

---

## Score Summary (Panel Evaluation)

| Criterion | Current Score | Realistic After Fixes | Max |
|---|---|---|---|
| Commercial Innovation & Feasibility | 7.5 | 8.5 | 10 |
| Technical Execution & Prototype | 8.0 | 8.5 | 10 |
| Defensibility & Safety | 6.0 | 7.5 | 10 |
| Presentation Clarity | 8.0 | 9.0 | 10 |
| **Composite** | **7.4** | **8.4** | **10** |

The business plan fixes (Block 1) move Commercial and Defensibility. The code fixes (Block 2) move Technical and are directly visible during the demo. The architecture diagram (Block 3) moves Presentation Clarity more than any other single action.
