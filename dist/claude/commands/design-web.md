---
description: 'Design and document full-stack architecture as NNN-DESIGN.md'
triggers: '"design web", "design architecture", "system design", "full-stack design"'
model: opus
---

Skills: @architecture-docs @backend-architecture @frontend-architecture @auth @stack-react @stack-nextjs @stack-node @stack-nestjs

Read NNN-BRIEF.md when present.

Treat frontend and backend equally; center the document on their contract (API shape, auth boundaries, data flow).

Layer when scope requires it:
- LLM/RAG/chat/generation → @ai-architecture
- Live updates → @realtime
- Service decomposition → @microservices or @set-microservice
- Monorepo layout → @monorepo

Output: Read `schemas/DESIGN.md` for context. Create or update `NNN-DESIGN.md`.

**When done — print this as your final message:**

### Next recommended step
1. **Review** `NNN-DESIGN.md` — Verify API contract, auth boundaries, and data flow.
2. **Run** `/plan-work`.

_Layer manually if scope requires:_ `@ai-architecture` (LLM/RAG/chat in scope), `@realtime` (live updates in scope), `@set-microservice` (service decomposition), `@monorepo` (monorepo layout)