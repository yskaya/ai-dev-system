---
description: 'Reproduce a bug, isolate root cause, and propose a minimal fix with regression risk'
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