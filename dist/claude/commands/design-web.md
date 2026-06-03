---
description: 'Design and document full-stack web architecture as NNN-DESIGN.md'
triggers: '"design web", "full-stack design", "web architecture"'
model: opus
---

Skills: @architecture-docs @backend-architecture @frontend-architecture @auth @stack-react @stack-nextjs @stack-node @stack-nestjs

Read NNN-BRIEF.md when present.

Document constraints, module boundaries, contracts, data flow, trust model, and key decisions — stay platform-agnostic unless a specialized design command applies.

Full-stack web app — treat frontend and backend equally; center the document on their contract (API shape, auth boundaries, data flow).

Layer when scope requires it:
- LLM/RAG/chat/generation → @ai-architecture
- Live updates → @realtime
- Service decomposition → @microservices or @set-microservice
- Monorepo layout → @monorepo

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Write `docs/ai/NNN-DESIGN.md` on disk — not chat-only. Create `docs/ai/` if missing. Use schema headings exactly.

### Next Step
Review `docs/ai/NNN-DESIGN.md` and run `/plan-work`