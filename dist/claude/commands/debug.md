---
description: 'Reproduce a bug, isolate root cause, and propose a minimal fix with regression risk'
triggers: '"debug", "bug report", "fix bug", "reproduce bug"'
model: opus
---

Work in order: reproduce → isolate root cause → propose minimal fix. Fill the Investigation section in `ISSUES.md` before editing code.

Do:
- reproduce and document steps before forming a theory
- name the root cause (with file:line) before proposing a fix
- state regression risk and verification steps with the fix

Avoid:
- speculative edits before the cause is identified
- refactoring, cleanup, or unrelated changes in the same diff

Output: Read `schemas/ISSUES.md` for context. Create or update `ISSUES.md`.

**When done — print this as your final message:**

### Next recommended step
1. **Review** `ISSUES.md` — Confirm root cause, fix, and verification steps are documented.

Inspect project state and pick **one**:
- **fix applied and a unit test is practical** → `/write-unit-tests`
- **fix applied and more plan tasks remain** → `/build-step` with @set-web, @set-api, or @set-service
- **investigation complete but fix not yet applied** — Apply the minimal fix, then re-run /debug or proceed to /write-unit-tests