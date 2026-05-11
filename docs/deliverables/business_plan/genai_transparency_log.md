# GenAI Transparency Log

**Project:** MerchAI  
**Required deliverable** - missing or incomplete entries reduce the grade. The LLM judge will check for back-filling patterns, so log as the work happens.

## Who needs to log

- **Leticia** (Tech - LLM layer, frontend, features): every coding session using Claude Code or claude.ai
- **Justus** (Tech - forecasting, RAG, deployment): every coding session using Claude Code or claude.ai
- **Alex** (Business - business plan, pitch deck): every writing session where AI helped draft or edit
- **Marie** (Product - demo script, presentation): every session where AI helped with slides, script, or Q&A prep

**Rule:** If you used an AI tool and it influenced the output - code, writing, design, analysis - it needs an entry. When in doubt, log it.

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

Date: 2026-05-11
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7)
Task: Closing the cloud-deploy debugging arc - verify the ONNX migration on the live URL, document the verified deploy, advise on API-key exposure, fix a stale path bug noticed during the README edit.
AI Contribution: Four commits on branch docs/tick-deploy-done.
  Verification:
  - Started Streamlit locally, walked through the full UI: Generate Today's Briefing returned 9 recs (3 PROMOTE / 3 RESTOCK / 3 MARKDOWN) on CA_1, switched to CA_2 and TX_1 to confirm all three stores load, expanded Guard checks, ran an Ask Your Data query. All features work end-to-end with ONNX embeddings.
  - User confirmed the live Streamlit Cloud URL also renders briefings end-to-end after the PR #8 redeploy. Round 4 architectural pivot verified.
  API-key exposure advice (no code, just guidance):
  - Flagged that public Streamlit Cloud URLs spend the ANTHROPIC_API_KEY stored in the app's Secrets - every visitor's briefing or Q&A click bills to Justus's Anthropic account. Estimated ~$0.10 per briefing on claude-sonnet-4-6.
  - Proposed four mitigations ranked by impact: (1) hard spend cap in console.anthropic.com, (2) password gate inside the Streamlit app, (3) pause when not demoing, (4) rotate the key after the presentation.
  - Justus chose option 1 only (planning €25 cap) and to take the website offline after the presentation. Declined the password gate.
  Documentation closure (commits on docs/tick-deploy-done):
  (1) cad4b41 docs(project-plan): ticked Deploy to live URL with the May 11 verification date and the note that ONNX migration unlocked it.
  (2) 0730a0e docs: added a "Live demo" section to README with the streamlit.app URL and brief instructions, plus appended the URL to the project-plan presentation-day checklist row.
  (3) 0a8bab9 docs: fixed two stale paths in README left over from the May 11 deliverables reorg - docs/business_plan/ -> docs/deliverables/business_plan/ for Alex's row and docs/genai_transparency_log.md -> docs/deliverables/business_plan/genai_transparency_log.md for the log link. Spotted while editing README, flagged as a follow-up rather than rolled into the URL commit silently.
  (4) this commit - the consolidated log entry covering this closure session.
  Local cleanup:
  - Stopped the local Streamlit process via pkill.
  - Discarded runtime HNSW binary mods (data_level0.bin + length.bin) that ChromaDB stamps even on read-only queries, so they wouldn't show as bogus diff on main.
  - Refreshed local main to origin/main before branching docs/tick-deploy-done.
Human Review: Verified the local UI personally (clicked through all features, both stores, before reporting "all works"). Confirmed the cloud render personally before authorising any documentation tick. Chose option 1 only for API-key protection - declined the password gate as overkill for a class-demo timeframe and accepting "take offline after" as the residual mitigation. Authorised the stale-path fix as a separate commit only after Claude flagged it (rejected the implicit "while-I'm-here" pattern). Requested this closing log entry rather than letting the round-4 entry stand at "awaiting verification".

---

Date: 2026-05-11
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7), with the superpowers:systematic-debugging skill
Task: Round 4 of the cloud-deploy debugging arc - after the model_kwargs={"low_cpu_mem_usage": False} fix (PR #7) was merged and redeployed, the briefing pipeline crashed with the IDENTICAL "Cannot copy out of meta tensor" error again. Two failed fixes against the same symptom; per the systematic-debugging skill, "if 3+ fixes fail, question the architecture - do not stack another guess". Pivoted: stopped trying to make sentence-transformers + torch work on cloud, and switched the embedding layer to ChromaDB's built-in ONNX-based DefaultEmbeddingFunction instead. Bypasses the entire torch + transformers + sentence-transformers stack.
AI Contribution: One commit on branch fix/switch-to-onnx-embeddings (864caee).
  Trigger for the architectural pivot:
  - Round 1 (de317a0, merged in PR #6): bump sentence-transformers 3.0.1 -> 3.2.1. Failed. Same error on redeploy.
  - Round 2 (ecac035, merged in PR #7): pass model_kwargs={"low_cpu_mem_usage": False} through chromadb to disable HF meta-init. Failed. Same error on redeploy.
  - Per the skill: after two failed fixes against the same symptom, the next step is NOT a third dep / kwarg guess. User intuited this independently and asked "how about just using the different command?" which was the architecturally right move.
  Round 4 change (commit 864caee):
  - src/rag/retriever.py: replaced SentenceTransformerEmbeddingFunction with chromadb.utils.embedding_functions.DefaultEmbeddingFunction (ONNX Runtime + all-MiniLM-L6-v2). Same model family, different inference runtime that does not touch torch.
  - src/rag/ingest.py: same swap, so the build-time and serve-time embedding functions stay in sync. Mismatched functions would produce vectors that retrieve garbage at query time.
  - requirements.txt: dropped sentence-transformers==3.2.1. With no remaining import of sentence_transformers in the codebase (verified by grep), the package and its ~1.5GB of transitive torch + transformers + accelerate weight is no longer needed. Smaller cloud container, faster cold-start.
  - Cleanup inside retriever.py: removed the now-defunct os.environ.setdefault("TOKENIZERS_PARALLELISM"/"OMP_NUM_THREADS") calls. They guarded a macOS spawn-method deadlock specific to sentence-transformers + loky multiprocessing; ONNX Runtime does not spawn multiprocess workers.
  - data/vector_store/: wiped and rebuilt locally via scripts/build_rag_corpus.py running against the new ingest.py. Old SentenceTransformer-embedded vectors are NOT interchangeable with the new ONNX-embedded vectors, so the store had to be reseeded. Same 382 M5-derived blurbs (124 + 131 + 127 across CA_1, CA_2, TX_1). New collection UUID bdec07c9-... replaces the old 6a0819b2-...
  Local verification before pushing:
  - Headless smoke test: from src.recommendations.engine import run_pipeline; ran on CA_1; received 9 well-formed recs (3 PROMOTE / 3 RESTOCK / 3 MARKDOWN), none flagged. End-to-end pipeline works with the new embeddings.
  - The user explicitly asked to NOT claim success until the live cloud URL renders a briefing, so this is "verified locally, pending cloud verification" only.
Human Review: After round 2 failed identically, asked the assistant to STOP proposing more fixes. Proposed the architectural pivot ("how about just using the different command?") rather than waiting for the assistant to escalate it. Authorised the full migration (code + dep removal + vector store rebuild) as one atomic change rather than splitting across multiple commits. Reviewed all four changed files plus the rebuilt store binary before approving the commit. Requested the log entry be written as a continuation of the existing round 1 + round 2 entry rather than as a separate new debugging series. Awaiting cloud redeploy verification before declaring fixed.

---

Date: 2026-05-11
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7), with the superpowers:systematic-debugging skill
Task: Third cloud-deploy crash session - after the sentence-transformers 3.0.1 -> 3.2.1 bump (PR #6) was merged and Streamlit Cloud redeployed, the briefing pipeline crashed with the IDENTICAL "Cannot copy out of meta tensor; no data!" error. First hypothesis was wrong. Reset to Phase 1 of systematic-debugging with new evidence, researched the actual cause, identified a code-level fix, branched it. Logged as one consolidated entry covering both rounds per the rule against fragmenting a single debugging arc.
AI Contribution: One commit on branch fix/disable-meta-init.
  Round 1 (failed hypothesis, already on main as de317a0):
  - Claim: "sentence-transformers 3.2.0 added explicit meta-tensor handling in .to(device)". This was unverified - I extrapolated from sbert's reputation for tracking torch breaking changes, not from release notes. Bumped 3.0.1 -> 3.2.1, merged, redeployed. Same error.
  Round 2 (this session, verified evidence):
  - Phase 1 reset: read the error verbatim again. "Use torch.nn.Module.to_empty() instead of .to() when moving from meta to different device". The directive is at PyTorch's API level - any caller of .to() on a meta tensor will fail under torch >=2.6. The bug is upstream of sentence-transformers' version - it's in HOW the model gets loaded onto meta in the first place.
  - Research (skill says "if you don't know, research more"): fetched chromadb 0.5.0 source via GitHub (embedding_functions.py). Confirmed SentenceTransformerEmbeddingFunction(__init__) accepts **kwargs and forwards them verbatim to SentenceTransformer(model_name, device=device, **kwargs). Fetched sentence-transformers v3.0.1 source. Confirmed SentenceTransformer(__init__) accepts a named parameter model_kwargs (dict) that is passed to AutoModel.from_pretrained(**model_kwargs) inside _load_auto_model. HuggingFace transformers uses meta-device init when low_cpu_mem_usage=True, which became default in many code paths around 4.40 (mid-2024). Setting low_cpu_mem_usage=False forces direct-to-device loading and avoids meta tensors entirely.
  - Verified evidence chain: chromadb forwards **kwargs to SentenceTransformer; SentenceTransformer 3.0.1 accepts model_kwargs and forwards to from_pretrained; from_pretrained respects low_cpu_mem_usage=False; no meta-init = no .to() copy error.
  - Phase 3 hypothesis (with citations this time): add model_kwargs={"low_cpu_mem_usage": False} to the SentenceTransformerEmbeddingFunction(...) call in src/rag/retriever.py. Single argument addition. Bypasses the bug class entirely without changing any dep versions.
  - Phase 4 fix: edited src/rag/retriever.py:23-32 to pass model_kwargs through, with a 5-line comment explaining the why. Did NOT revert the 3.2.1 bump from round 1 - it's now on main and reverting would be "while-I'm-here" cleanup against the one-change-at-a-time rule. Net deps: still sentence-transformers 3.2.1.
  - Fallback if round 2 also fails: pin transformers<4.40 to prevent meta-init at the dep level. Not betting on this - the verified evidence chain above is strong enough that I'd want to talk before stacking yet another guess.
Human Review: Switched the assistant into superpower-skill mode during round 1 after the second cloud failure to enforce systematic discipline. After round 1's hypothesis also failed, explicitly asked the assistant to NOT propose another fix without verified evidence (the skill says "if you don't know, say so - don't pretend"). Reviewed all source-code citations (chromadb 0.5.0, sentence-transformers 3.0.1) before authorising the model_kwargs change. Authorised consolidating both round 1 and round 2 in a single log entry rather than fragmenting across separate entries. Awaiting cloud redeploy result before declaring the fix verified - explicitly not claiming success until the live URL renders a briefing for the first time.

---

Date: 2026-05-11
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7)
Task: Second cloud-deploy crash session - after the HF offline fix landed and Streamlit Cloud redeployed, the briefing pipeline crashed again on first generation with a different error: "Cannot copy out of meta tensor; no data!". Diagnosed using the systematic-debugging superpowers skill, branched a one-line dependency fix, ready to merge.
AI Contribution: One commit on branch fix/sentence-transformers-meta-tensor.
  Diagnostic process (systematic-debugging skill applied):
  - Phase 1 root cause: Read the full PyTorch error verbatim. The "Cannot copy out of meta tensor" message is raised by torch >=2.6 when .to(device) is called on a tensor that lives on the meta device with no underlying data. Inferred load path: chromadb -> SentenceTransformerEmbeddingFunction -> sentence-transformers SentenceTransformer.__init__ -> .to(device). Inferred cause: newer transformers (>=4.40) uses meta-init for memory efficiency; sentence-transformers 3.0.1 (June 2024) does not materialize meta tensors before .to(); the combination fails on torch >=2.6.
  - Phase 2 pattern: locally on Justus's machine the embedding loads fine because the model is already cached from the May 9 rebuild; sentence-transformers takes the cached-load fast-path which does not trigger meta-init. Cloud has no cache, hits the broken path.
  - Phase 3 hypothesis (one): bumping sentence-transformers from 3.0.1 to 3.2.1 fixes the crash because 3.2.0 (Oct 2024) added explicit meta-tensor handling before .to(). Conservative version choice within 3.x to preserve chromadb 0.5.0 compatibility. Alternative considered and rejected: pinning transformers<4.40 - that is symptom suppression, leaves the buggy library in place, fragile against future resolutions.
  - Phase 4 fix: one-line edit in requirements.txt, 3.0.1 -> 3.2.1.
  Limitation noted in the process: no easy local repro - local cache hides the bug. Cloud is the test environment; verification cost is one redeploy cycle.
  Fallback hypothesis if 3.2.1 also fails: chromadb 0.5.0 may not be forward-compat with sentence-transformers 3.2.x. Next step would be bumping chromadb. Not betting on this - chromadb uses the stable SentenceTransformer(model_name, device=device) constructor surface.
Human Review: Switched the assistant into superpower-skill mode after the second cloud failure to enforce systematic discipline. Reviewed the full Phase 1-3 reasoning before authorising the requirements.txt edit. Authorised the branch + commit + push plan. Awaiting the cloud redeploy result before declaring the fix verified - explicitly NOT claiming success until the live URL renders a briefing.

---

Date: 2026-05-11
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7)
Task: Streamlit Cloud deploy session - took main from "deploy-ready" to "live and serving briefings". First deploy build succeeded but the briefing pipeline failed on first generation due to a hardcoded offline flag in retriever.py blocking the embedding model download on cold-start. Diagnosed, branched the fix, ready to merge.
AI Contribution: One commit on branch fix/hf-offline-cloud-deploy (b5fc6e3).
  Deploy walk-through:
  - share.streamlit.io: new app from nason31/Advanced_ML_Group_F, branch main, main file app/main.py, Python 3.12, ANTHROPIC_API_KEY pasted into the Secrets UI in TOML format.
  - First build green (~3-5 min installing LightGBM, ChromaDB, sentence-transformers, anthropic 0.97.0).
  - App booted successfully; UI rendered correctly with the sidebar (store dropdown, Generate button, Ask Your Data).
  Crash on first briefing:
  - Clicked Generate Today's Briefing on CA_1; "Analysing products..." spinner ran briefly then errored: "Pipeline failed: We couldn't connect to https://huggingface.co to load the files, and couldn't find them in the cached files."
  - Root cause: src/rag/retriever.py lines 10-11 hardcode HF_HUB_OFFLINE=1 + TRANSFORMERS_OFFLINE=1 via os.environ.setdefault. This was the right call on Apr 26 (macOS local, model cached, CDN load-balancer hang) and Leticia explicitly preserved it on May 11. But the Streamlit Cloud container has no pre-cached model, so the offline flag forces an "OSError: couldn't find files locally" the first time SentenceTransformerEmbeddingFunction tries to load all-MiniLM-L6-v2.
  Fix (b5fc6e3 on branch fix/hf-offline-cloud-deploy):
  - Removed both os.environ.setdefault lines for HF_HUB_OFFLINE and TRANSFORMERS_OFFLINE.
  - Kept TOKENIZERS_PARALLELISM=false and OMP_NUM_THREADS=1 (they guard a separate macOS spawn-method deadlock and are harmless on Linux).
  - Net cost: ~30-60s first-briefing cold start while the model downloads, then cached on the container. Subsequent briefings stay fast (~5-10s thanks to the May 11 ThreadPoolExecutor parallelization).
  - lru_cache on _get_collection still ensures the model loads once per process, so the network call only happens on the very first retrieve() call after a container restart.
  Repoint vs merge decision:
  - Original plan was to repoint Streamlit Cloud at the fix branch to test before merging. Streamlit Cloud UI does not expose branch-switch cleanly (treats it as effectively immutable post-deploy); the alternative would be delete + redeploy the app.
  - Decided to merge to main instead given the change is 8 deleted lines with a clear hypothesis and a 30-second revert path. PR open at github.com/nason31/Advanced_ML_Group_F/pull/new/fix/hf-offline-cloud-deploy.
Human Review: Rejected Claude's first attempt to commit and push the fix directly to main; required a feature branch first. Authorised the push to origin/fix/hf-offline-cloud-deploy after reviewing the diff. Initially asked to repoint Streamlit Cloud at the branch to test in isolation; after confirming Streamlit Cloud does not support clean mid-deploy branch changes, agreed to merge to main as the lower-friction path with adequate safety (revert is trivial). Verified the secret format in the Streamlit Cloud UI (TOML "KEY = value", no export prefix). Read the cloud error message in the UI screenshot before authorising the diagnosis path.

---

Date: 2026-05-11
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Pre-presentation review session - applied four professor grading prompts (Technical Architecture, Unit Economics, Defensibility, Final Simulation) to the full project, fixed identified issues in the codebase, and reorganised the deliverables structure.
AI Contribution: Claude performed a full cross-file codebase and pitch deck review, then implemented 5 commits across 4 files:
  Analysis:
  - Technical Architecture Review: identified 4 issues - slow pipeline (9 sequential Claude API calls), frozen spinner UX, audit trail lost on refresh, and NaN sell_price producing broken Impact column values (€nan / €0).
  - Unit Economics Review: read all 18 slides via python-pptx extraction; confirmed 92% gross margin, LTV/CAC ratios, and three-scenario P&L are correct; flagged Appendix A1 discrepancy (JSON schema and "re-prompt" claim don't match actual code), RAG count inconsistency (282 vs 382 on slides 4 vs 5), and missing temperature=0.2 in code.
  - Defensibility Review: confirmed not a wrapper (LightGBM + RAG + guard = 3 separate engineering problems); identified feedback loop as aspirational not real (CSV only, no retraining); recommended adding hallucination guard as Moat 04 (compliance-ready, deterministic, auditable).
  - Final Presentation Simulation: scored 7.5/10 overall (Commercial 7.5, Technical 7.0, Defensibility 7.5, Presentation 8.0); identified top 5 improvements before demo day.
  Code fixes (3 commits):
  (1) 119cb03 perf: parallelize briefing generation with ThreadPoolExecutor
      - src/llm/reasoner.py: added threading.Lock (double-checked locking) to _get_client() for thread-safe singleton init under concurrent calls.
      - src/recommendations/engine.py: extracted per-seed logic into _process_seed(), parallelized with ThreadPoolExecutor(max_workers=len(rec_seeds)). Reduces generation time from ~45-90s to ~5-10s.
      - app/main.py: replaced st.spinner with st.status() showing "Analysing products..." during run and collapsing to "Briefing ready - N recommendations" on complete.
  (2) 2ca0409 fix: persist audit trail to CSV and guard against NaN sell_price
      - src/recommendations/summarize.py: added math.isnan guard on sell_price in _build_seed() - NaN values sanitized to 0.0 before reaching engine.
      - src/recommendations/engine.py: _compute_action() now checks sell_price > 0 before computing revenue; falls back to units (PROMOTE) or percentage-only (MARKDOWN) when price is unavailable, so Impact column never shows €nan or €0.
      - app/main.py: added _load_audit() and _append_audit() helpers; audit_trail.csv written on every accept/reject, loaded on app startup. Audit trail now survives page refresh.
  Doc/repo changes (2 commits):
  (3) b02fc17: moved docs/business_plan/ to docs/deliverables/business_plan/, committed pitch deck (Advanced_ML_Pitch_work.pptx).
  (4) 9ae744b: deleted outdated docs/deliverables/business_plan/outline.md (superseded by pitch deck).
  Also updated docs/project_plan.md (removed Deploy to live URL and Demo script tasks) and docs/feature_overview.md (RAG count 57→382, added ACTION and Impact column rows).
Human Review: Confirmed parallelization is safe - each seed is fully independent, Anthropic client is thread-safe, ChromaDB PersistentClient supports concurrent reads. Rejected a proposed fix to remove HF_HUB_OFFLINE=1 from retriever.py after confirming the app runs locally only (model is cached; the original Apr 26 fix remains appropriate). Rejected adding temperature=0.2 to reasoner.py - not needed for local demo. Decided to delete outline.md rather than update it, since the pitch deck is now the authoritative business plan document. Reviewed all diffs before each commit. Verified imports pass after each change.

---

Date: 2026-05-11
Team Member: Alex
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Updating the business plan from v1.2 to v1.3 to reflect all code changes since May 1 and fixing internal consistency issues identified in a pre-submission review.
AI Contribution: Claude read all current source files and the codebase genai transparency log, identified divergences between the v1.2 business plan and the current codebase, and implemented targeted edits to build_business_plan.py:
  (1) RAG corpus count updated from 57 to 382 documents throughout.
  (2) PROMOTE threshold corrected from +15% to +50% to match summarize.py; RESTOCK documented as the 15-50% range.
  (3) Token economics revised from 5 recs at €0.026/briefing to up to 9 recs at €0.043/briefing; prompt caching opportunity (90% input cost reduction) added as a planned optimisation.
  (4) ACTION column feature (quantifiable impact badges: +€X rev / +X units / ↓ €X.XX) added to Sections 2.2, 4.2, and 6.3.
  (5) Ask Your Data updated to reflect k=6 RAG retrieval, product name matching, and 2-sentence plain-language format.
  (6) Note added to Section 6.5 clarifying that the system prompt's ">+15%" is directional guidance for Claude's copy generation, while the actual classification threshold is PROMOTE_THRESHOLD = 50.0 in summarize.py. The LLM receives the pre-classified seed with an explicit "PROMOTE THIS candidate" tag, not the threshold number.
  (7) Break-even updated from 78 to 79 stores, gross margin from 92% to 91%, fully loaded per-store cost from €25 to €27/month to reflect higher per-briefing LLM cost.
  (8) GenAI transparency log appendix removed from the business plan document; missing sessions added to this file instead.
Human Review: Alex verified all updated numbers against current source files. Confirmed PROMOTE threshold change against summarize.py line 18. Confirmed token cost recalculation against Claude Sonnet 4.6 published pricing ($3/MTok input, $15/MTok output). Confirmed gross margin and break-even recalculation manually. Approved all section additions. Regenerated .docx via build_business_plan.py.

---

Date: 2026-05-10
Team Member: Justus
Tool Used: Claude Code (claude-opus-4-7)
Task: Local end-to-end smoke test of main after Leticia's May 1/6/7 work, diagnosing a crash that surfaced, then bundling the fix and a project-plan trim into a cleanup branch ahead of the Streamlit Cloud deploy. Multi-day arc: smoke test + rebuild on May 9, branch + commits on May 10.
AI Contribution: Two commits on branch chore/cleanup-and-deploy-prep (dd868e8, 0467a3c).
  Diagnosis (May 9):
  - Streamlit launched cleanly but "Generate Today's Briefing" failed with "Pipeline failed: object of type 'int' has no len()". Engine.py swallows tracebacks behind try/except, so reproduced headlessly via `python -c "from src.recommendations.engine import run_pipeline; ..."` to surface the real stack.
  - Stack pointed at chromadb's _decode_seq_id calling len() on an int. Root cause: the committed data/vector_store/ SQLite was written by a different chromadb build than the 0.5.0 pinned in requirements.txt, so the on-disk seq_id storage format (BLOB vs INTEGER) was incompatible with the running version.
  - Fix path: deleted data/vector_store/ and re-ran scripts/build_rag_corpus.py (the May 7 version Leticia wrote). Regenerated the same 382 M5-derived blurbs (124 CA_1 + 131 CA_2 + 127 TX_1) under chromadb 0.5.0. New collection UUID 6a0819b2-... replaces the old a1795dd4-...
  - Verified end-to-end: 9 well-formed recs (3 PROMOTE / 3 RESTOCK / 3 MARKDOWN) returned in ~50s, none flagged. Same shape as Justus's Apr 26 smoke test.
  Cleanup branch (May 10), per Leticia's request to tighten the plan and clean residue:
  (1) dd868e8 fix(rag): rebuild vector store under chromadb 0.5.0 to fix len() crash. Stages the rebuilt SQLite + new HNSW collection dir, drops the old collection, restores .gitkeep. Same fix applied locally on May 9, just committed today so origin/main and Streamlit Cloud get the working artefact too.
  (2) 0467a3c docs(project-plan): close completed tech items, narrow tech scope to deploy + model. Per Leticia's read on May 10, only "Deploy to live URL" and the optional "Model improvement" remain on the tech track. Ticked UI polish (May 1 + May 7 work shipped it: ACTION column, Impact column, Department names, confidence badges, delta arrows, Generate Today's Briefing button). Folded "Lock demo scenario" into Marie's existing Demo script row to remove duplication. Promoted Deploy to bold "biggest remaining tech blocker". Added two ticks to the presentation-day checklist (UI polish, vector store rebuild).
  Also surveyed the repo for residue per Leticia's "stuff lying around" note: nothing tracked is dead. __pycache__ everywhere, .pytest_cache, .vscode, .ipynb_checkpoints all already in .gitignore. Deleted local __pycache__ dirs and .pytest_cache as one-off hygiene with no git change. Notebook 01_baseline.ipynb kept on purpose - documented context for the Apr 23 baseline result, no clear reason to delete.
Human Review: Drove the diagnostic process - confirmed the crash reproduced from a plain python -c invocation independent of Streamlit, ruling out the UI layer. Authorised the destructive `rm -rf data/vector_store/` only after confirming the rebuild script could regenerate from data/raw/ (no Kaggle round-trip needed). Sourced .env into the test shell after Claude flagged the headless test missed dotenv loading. Approved the branch name and commit-by-commit plan before staging. Reviewed both diffs before commit. Rejected one Claude suggestion to add .pytest_cache/ to .gitignore defensively - it has never been tracked, so a "just in case" change is unnecessary churn. Declined the open question on deleting notebooks/01_baseline.ipynb. Branch is local only - not pushed yet pending the deploy session.

---

Date: 2026-05-09
Team Member: Alex + Marie
Tool Used: Claude Code (claude-sonnet-4-6) for prompt generation; Claude Design (Anthropic) for deck creation
Task: Generating a structured prompt for Claude Design to produce the first draft of the MerchAI pitch deck for the course presentation.
AI Contribution: Claude Code generated a 12-slide structured prompt for Claude Design, covering: title slide with tagline ("The AI Merchandiser Every Walmart Has, But the 500-Store Chain Can't Afford"); problem (3-column layout: late markdowns / replenishment gaps / promo blind spots, with the €2.5M margin improvement hook); solution with a briefing table mockup including example rows with action badges; pipeline flow diagram (LightGBM -> RAG -> Claude -> Guard -> Manager decision); three recommendation types with example action badges (+€X rev / +X units / ↓ €X.XX); hallucination guard with flagged card mockup (2-column: intent check / numeric check); moat (three compounding structural advantages + "Why not OpenAI?" callout); market opportunity (€1.1B TAM, positioning map vs Relex / Blue Yonder / generic BI); unit economics (91% gross margin, break-even at 79 stores, LTV/CAC 188:1); product roadmap (4-phase timeline); team (2x2 grid with track colour-coding); Ask Your Data demo call to action with example Q&A. The prompt specified a dark navy/teal colour palette, clean modern SaaS aesthetic, exact KPIs per slide, and quote placements. Claude Design produced the first-draft deck (12 slides).
Human Review: Significant edits applied after the first draft. Slides reordered to lead with the market gap before the solution. Unit economics slide restructured to emphasise customer ROI over internal cost. Briefing table mockup replaced with an actual screenshot from the live Streamlit app. Team slide redesigned with track colour-coding. Visual styling, metric placements, and narrative flow substantially revised. Approximately 40-50% of content retained from the first draft. The structured prompt approach saved an estimated 3-4 hours of initial slide structure and content organisation work.

---

Date: 2026-05-07
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Q&A chatbot overhaul and RAG expansion - fixing a broken Q&A feature, expanding the context corpus from 57 to 382 docs, and improving answer quality and UI for store managers.
AI Contribution: Claude implemented changes across 4 commits (b483574, cbf4a1a, b40c226, a76b265):
  (1) fix(qa) b483574 - corrected summarize_forecast() call in qa.py: wrong keyword argument top_k -> bucket_size.
  (2) feat(rag) cbf4a1a - expanded RAG corpus from 57 to 382 docs across 3 stores:
      - scripts/build_rag_corpus.py: rewrote event_lift_blurbs() to compute lift per category x event (not store-wide average), covering all events with >5% lift and picking up the event_name_2 calendar column. Added new per_sku_blurbs() function generating one doc per top-50 SKU per store, covering seasonal peak/trough months, best sales weekday, and price sensitivity.
      - src/llm/qa.py: RAG retrieval k=4 -> k=6; added SKU-matching logic to use category/dept for targeted RAG query.
      - src/llm/prompts.py: rewrote QA system prompt to lead with best explanation, no headers/bullets, strict 2-3 sentence limit.
  (3) fix(qa) b40c226 - rewrote QA system prompt again for fully plain language: "selling fast" not "elevated delta", no em dashes, strict 2-sentence format, translate percentages to plain English ("about 5 times normal").
  (4) feat(qa+ui) a76b265 - product name and dept name wiring:
      - src/data/product_names.py: added DEPT_NAMES mapping (FOODS_3 -> "Snacks & Beverages" etc.) and get_dept_name() function.
      - app/components/briefing_card.py: added Department column between Product and Confidence in the briefing table.
      - src/llm/qa.py: refactored to accept active_products {name: sku} from caller instead of scanning all 3000 forecast SKUs - fixes product name collision issue where multiple SKUs shared the same name.
      - app/main.py: builds active_products from the 9 current recs only; passes dept name in context so Claude says "Snacks & Beverages" not "FOODS_3"; updated Ask Your Data caption to plain manager language.
      - src/llm/prompts.py: build_qa_prompt() now accepts and renders a Product Name to SKU Mapping section so Claude can match "Maple Syrup" to the right SKU.
Human Review: Diagnosed the top_k bug from the error message. Set per-category event lift threshold at >5% lift (below that is noise). Decided to pass active_products from the caller (9 recs) rather than building from all forecast SKUs after observing that multiple SKUs share the same product name and the wrong one was being picked. Reviewed all dept name labels for retail accuracy before committing. Verified the Department column renders correctly in the table. Confirmed max_tokens reduced from 512 to 256 to enforce shorter answers.

---

Date: 2026-05-06
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Team role label cleanup across all project docs - renaming Marie's track from "Float" to "Product" and fixing inconsistencies in CLAUDE.md, docs/project_plan.md, and docs/genai_transparency_log.md.
AI Contribution: Claude identified all files where the team role table or badge labels appeared (CLAUDE.md, project_plan.md, genai_transparency_log.md, README.md), flagged the three inconsistencies (Float vs Presentation vs no label), and executed the fixes across 1 commit (44b7267):
  (1) CLAUDE.md - changed Marie's track from "Float" to "Product".
  (2) docs/project_plan.md - updated the legend badge and all 4 task-table rows from "🟠 Presentation" to "🟠 Product".
  (3) docs/genai_transparency_log.md - replaced the "Who needs to log" table with a bullet list; named [Teammate 3] as Alex and [Teammate 4] as Marie; corrected Marie's track to "Product".
Human Review: Confirmed "Product" is the correct track label per team alignment. Verified the vector store binary changes were excluded from the commit (runtime artefacts from the running app, not source changes). Reviewed all three diffs before approving the commit.

---

Date: 2026-05-01
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: UI overhaul session - rebuilt the recommendations view as a sortable table, added a sidebar chat panel, wired dotenv support, improved data presentation (product names, store labels, date variation), replaced the date picker with a "Generate Today's Briefing" button, and tightened the 3-bucket selection logic.
AI Contribution: Claude implemented changes across 5 commits on main (+changes across app/main.py, src/recommendations/engine.py, src/recommendations/summarize.py, and supporting files):
  (1) 852824b feat(ui): table view for recommendations, sidebar chat, dotenv support - replaced the card stack with a sortable st.dataframe table for all recommendations; added a sidebar chat panel stub for the Ask Your Data flow; added python-dotenv loading so the app picks up .env locally without manual export.
  (2) 535be68 feat(ui+data): product names column, date variation, friendlier store labels - added a human-readable product name column to the recommendations table by joining the M5 item lookup; introduced date variation in the generated data so each run does not show identical dates; renamed raw store IDs (CA_1, TX_1) to friendlier labels (California Store 1, Texas Store 1) throughout the UI.
  (3) 6d9718b feat(ui): replace date picker with Generate Today's Briefing button - removed the st.date_input widget and replaced it with a single prominent button that always runs for today's date, simplifying the UX for a demo context where date navigation is a distraction.
  (4) c08e7df feat(recommendations): 3-bucket selection logic (PROMOTE / RESTOCK / MARKDOWN) - tightened the bucket assignment in engine.py so PROMOTE, RESTOCK, and MARKDOWN are selected based on explicit delta_pct thresholds rather than a single catch-all else branch; ensures the three buckets are always represented in the briefing output.
  (5) 97378af docs(genai-log): expand header with per-member logging table and rule - added the per-member logging responsibility table and the mandatory logging rule to the genai_transparency_log.md header so all teammates know what to log.
Human Review: Confirmed the table view is cleaner for the demo than individual cards - easier for a non-technical audience to scan. Verified the friendlier store labels map correctly to the underlying M5 store IDs. Set the 3-bucket thresholds based on the same delta_pct logic established in the Apr 29 session (>+15% = PROMOTE, negative = MARKDOWN, else RESTOCK). Confirmed the "Generate Today's Briefing" button simplification is appropriate for a demo context and does not remove any underlying forecast capability.

---

Date: 2026-04-29
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Building Confidence display and Conversational "Ask Your Data" features, plus fixing 5 code and doc inconsistencies identified in a full codebase review.
AI Contribution: Claude implemented across 9 commits on main:
  Confidence display (2 commits):
  (1) src/recommendations/engine.py - added _compute_confidence() helper (High >100%, Medium 30-100%, Low <30% delta_pct) and confidence + delta_pct fields to Rec dataclass.
  (2) app/components/briefing_card.py - green/amber/red badge top-right of each card with exact delta_pct below it.
  Ask Your Data (3 commits):
  (3) src/llm/prompts.py - added QA_SYSTEM_PROMPT (conversational, citation-required, plain language) and build_qa_prompt() alongside existing recommendation prompts.
  (4) src/llm/qa.py - new answer_question() function reusing forecast_with_names, summarize_forecast, retrieve, and _get_client(). top_k=5 SKUs and k=4 RAG docs for broader Q&A grounding vs top_k=3 / k=3 for recs.
  (5) app/main.py - Ask Your Data section below audit trail: text input with example placeholder, Ask button, answer displayed inline with spinner.
  Codebase fixes (4 commits):
  (6) docs/architecture.md - full rewrite splitting training vs serve pipeline. Previous diagram was missing serve.py and summarize.py entirely.
  (7) docs/feature_overview.md - fixed hallucination guard description (said suppressed, actually surfaced), split built vs planned features with effort/gain/priority ratings.
  (8) src/llm/guard.py - replaced generic 'feature' phrase in PROMOTE_PHRASES with 'feature placement' and 'feature in flyer' to avoid false positive matches.
  (9) src/llm/reasoner.py - Anthropic client now created once as module-level singleton via _get_client() instead of on every reason() call.
Human Review: Defined confidence thresholds based on retail signal strength intuition (>100% is an unambiguous act signal, <30% warrants human verification). Reviewed all fixes before committing - confirmed architecture diagram accurately reflects current code flow. Approved splitting feature_overview.md into built vs planned so the business track has an honest picture of what exists. Verified qa.py reuses existing layers correctly with no new dependencies introduced.

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

Date: 2026-04-30
Team Member: Alex
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Writing and structuring the complete business plan (v1.0 to v1.2) as a Python docx generator (build_business_plan.py), covering all 9 sections.
AI Contribution: Claude drafted the full document structure and all section content, using team-provided data points, architecture details, and financial inputs:
  - Executive summary framing and market sizing narrative.
  - Target customer profile table and competitive landscape table.
  - Four-argument "why not OpenAI?" moat structure.
  - Full pipeline description (Steps 1-6) mapping the LightGBM to RAG to Claude to guard flow.
  - Token economics derivation from Claude Sonnet 4.6 API pricing with per-briefing cost breakdown.
  - All financial scenario tables: gross margin model, operating cost model, break-even analysis, LTV/CAC table.
  - Hallucination guard architecture description (2-layer: intent check + numeric check).
  - Prompt engineering exhibit (Section 6.5) including verbatim system prompt and user prompt structure.
  - Risks and mitigations section (4 risks with mitigation paths).
  - Python docx-generation framework (python-docx) so the plan regenerates from source after every code change.
Human Review: Alex provided all key facts (market size estimates, pricing strategy, tech stack details, team roles and contributions), verified all financial calculations against team-derived numbers, confirmed all technical claims against the working codebase, and rejected framing that overstated prototype capabilities. The ROI story (0.5% margin improvement = €2.5M/year = 4.6x ROI), the pricing model (€200-500/store/month), competitive positioning, and break-even target were human decisions made in team discussion. Expression and document structure were AI-assisted; the reasoning and underlying data are the team's own.

---

Date: 2026-04-30
Team Member: Alex
Tool Used: Claude (claude.ai)
Task: Grammar and logic correction on team-authored business plan drafts. The team is composed entirely of non-native English speakers; Claude was used to improve expression while preserving the team's own reasoning.
AI Contribution: For each business plan section, Claude reviewed team-drafted paragraphs and corrected grammar, syntax, and logical flow. Prompt used: "Please read carefully through the following paragraph and correct it based on grammar and logic. Take the position of a native English speaker who is very familiar with machine learning and knows the jargon." Claude suggested corrections improving clarity and professional register without adding or changing the underlying arguments.
Human Review: Alex reviewed every suggested change and accepted only those that preserved the intended meaning. All arguments, data points, financial projections, and strategic reasoning were authored by the team; AI corrected expression only. Suggestions that changed meaning or introduced claims not supported by the team's own analysis were rejected.

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
Team Member: Leticia
Tool Used: Claude (claude.ai)
Task: Startup idea generation and product selection - generating candidate business ideas from the assignment brief and selecting MerchAI from a shortlist.
AI Contribution: Claude was provided with the full assignment brief, the four evaluation criteria (commercial innovation, technical execution, defensibility, presentation), and the team's skill profile. It generated a set of startup ideas that were commercially viable and technically feasible within a 3-week build window. The team shortlisted three candidates and asked Claude to evaluate which best fit the team profile and rubric. The final shortlist came down to two ideas: (1) a Merchandising Copilot for mid-size retailers and (2) an AI-Powered Due Diligence Assistant for SME acquisitions. Claude outlined the tradeoffs and mapped each idea to the four evaluation criteria.
Human Review: The team discussed both shortlisted ideas in a team meeting. Selected the Merchandising Copilot because some team members had limited interest in the finance domain, and the retail use case offered more tangible prototyping opportunities on publicly available data (M5 Forecasting dataset). The final product decision, the team name (MerchAI), and the target customer segment (mid-market retailers, 50-500 stores) were human decisions made in team discussion, not AI outputs.

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

Date: 2026-05-07
Team Member: Leticia
Tool Used: Claude Code (claude-sonnet-4-6)
Task: Adding quantifiable ACTION column to briefing table and improving recommendation clarity
AI Contribution: Claude implemented a full ACTION column pipeline across 4 files. In src/forecast/serve.py: added sell_price to forecast output so it flows downstream. In src/recommendations/summarize.py: added baseline and sell_price to each seed dict. In src/recommendations/engine.py: replaced the Rec.impact field with impact + action_detail fields, implemented _compute_action() which produces a short badge ("+€78 rev" / "+ 42 units" / "↓ €1.91") and a full explanatory sentence per recommendation type. PROMOTE shows expected revenue uplift at current price; RESTOCK shows units to order; MARKDOWN shows target price with discount scaled to delta severity (clamped 15-30%). In app/components/briefing_card.py: renamed column header to ACTION, added a deterministic st.info() callout at the top of each Details expander explaining the suggested action with matching numbers, restored Accept/Reject buttons to the main table row, and iteratively tuned 9-column proportions to prevent header wrapping. Claude also clarified the distinction between PROMOTE (visibility action, no price change) and MARKDOWN (price reduction) after the user questioned why a PROMOTE showed the same price.
Human Review: Reviewed each iteration in the live UI. Corrected the PROMOTE badge from "Feature @ €2.24/unit" (misleading - implied a price recommendation) to "+€78 rev" (revenue opportunity). Chose Version 3 arrow format for badges (↑/+/↓). Confirmed column proportions after several visual checks. Approved final layout before committing.
