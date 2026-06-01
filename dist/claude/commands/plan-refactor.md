---
description: 'Plan test-gated phased refactoring → NNN-REFACTOR.md (no new features or bug fixes per phase)'
triggers: '"plan refactor", "phased refactor", "refactor plan"'
model: opus
---

Read relevant code plus `NNN-DESIGN.md` and `NNN-ISSUES.md` when present.

Analyze the problem area and produce a phased refactor plan.

**Constraints**
- Each milestone must compile and pass all existing tests before the next starts.
- Do not mix refactor work with new features or bug fixes in the same milestone.

Output: Read `schemas/REFACTOR.md` for context. Create or update `NNN-REFACTOR.md`.

**When done — print this as your final message:**

### Next recommended step
1. **Review** `NNN-REFACTOR.md` — Confirm phases are test-gated with no feature or bug-fix mix-in.
2. **Run** `/build-step` @set-web, @set-api, or @set-service.
   _Stack skills are NOT auto-attached — pick one for the task area_