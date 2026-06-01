---
description: 'Implement the next unchecked task from NNN-PLAN.md'
triggers: '"build step", "build next", "implement next"'

---

Implement the smallest safe change for the first unchecked task in milestone order in `NNN-PLAN.md`.

Layer stack for this task:
- Area: `@set-web` · `@set-api` · `@set-service` (pick one)
- Add: `@microservices` (service boundaries) · `@stack-ai` (LLM SDK)
- Shortcut: `@set-microservice` = `@set-service` + `@microservices`

**After coding**
- Mark only that task `- [x]` when acceptance criteria are satisfied.

Output: Read `schemas/PLAN.md` for context.

**When done — print this as your final message:**

### Next recommended step
Inspect project state and pick **one**:
- **unchecked tasks remain in NNN-PLAN.md or NNN-REFACTOR.md** → `/build-step` with @set-web, @set-api, or @set-service (Stack skills are NOT auto-attached — pick one for the task area)
- **all plan or refactor tasks checked** → `/review-code`

_Also:_ if diff touches auth, user input, secrets, or third-party/AI integrations, run `/review-security`.