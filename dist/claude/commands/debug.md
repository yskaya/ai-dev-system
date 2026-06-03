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

**Artifact (required)**
- Read `schemas/ISSUES.md` before writing.
- Write `docs/ai/ISSUES.md` on disk — not chat-only. Create `docs/ai/` if missing.
- Use schema headings exactly; substitute real work id (`001`) when known.

### Next Step
Review `docs/ai/ISSUES.md` and run `/build-step`