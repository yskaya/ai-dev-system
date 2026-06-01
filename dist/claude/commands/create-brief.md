---
description: 'Create product brief for new products/greenfield. For existing system changes, use /plan-work'
triggers: '"create brief", "product brief", "new product"'
model: opus
---

Capture just enough to start design or planning. 
Focus on product intent (what and why), not implementation details.

Output: Read `schemas/BRIEF.md` for context. Create or update `NNN-BRIEF.md`.

**When done — print this as your final message:**

### Next recommended step
1. **Review** `NNN-BRIEF.md` — Confirm MVP scope, non-goals, and success criteria.
2. **Run** `/design-web` to document architecture before build.

_Alternatively:_
- **small change to an existing system (skip design)** → `/plan-work`

_Skills for `/design-web` (auto-attached):_ `@architecture-docs`, `@backend-architecture`, `@frontend-architecture`, `@auth`, `@stack-react`, `@stack-nextjs`, `@stack-node`, `@stack-nestjs`
_Layer manually if scope requires:_ `@ai-architecture` (LLM/RAG/chat in scope), `@realtime` (live updates in scope), `@set-microservice` (service decomposition), `@monorepo` (monorepo layout)