---
name: ai-architecture
description: 'Apply AI system design (RAG, routing, eval). @stack-ai for SDK; @realtime for transport.'

---

Do:
- justify long-context or no-RAG when skipping retrieval/chunking
- set cost/latency targets per routing step
- define golden-case offline eval and explicit degrade/fallback paths

Avoid:
- full-corpus prompts when RAG is cheaper and more precise
- one model for all steps when routing cuts cost
- prod prompt/model changes without offline eval
- client/edge inference without a clear latency, privacy, or cost win

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Ensure the file starts with this header; prepend if missing (verbatim):
<!--
******************************************************
*****                AI GENERATED                *****
******************************************************
-->
- Update sections `AI system`, `Data flow`, `Key decisions`, `Risks` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only.
- Leave other sections unchanged.