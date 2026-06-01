---
description: 'Design and document full-stack architecture as NNN-DESIGN.md'
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