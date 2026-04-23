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
