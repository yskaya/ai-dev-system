---
description: 'Review files, an area, or branch/PR diff for correctness and maintainability; rank findings P0–P3'
triggers: '"review code", "code review", "review diff", "review PR"'
model: opus
---

Anchor every finding to file:line. For diffs, check acceptance criteria in `NNN-PLAN.md` when available.

Do:
- flag bugs, unnecessary complexity, drift, weak error handling

Avoid:
- treating style preferences as blocking issues
- reviewing without understanding intended behavior first
- suggesting rewrites when focused fixes suffice

Auth, input handling, or external integrations → run `/review-security`, then fold results into this review.

**Artifact (required)**
- Read `schemas/REVIEW.md` before writing.
- Prepend this header at the very top of the file (verbatim):
<!--
******************************************************
*****                AI GENERATED                *****
******************************************************
-->
- Write `docs/ai/NNN-REVIEW.md` on disk — not chat-only. Create `docs/ai/` if missing. Use schema headings exactly.

### Next Step
Review `docs/ai/NNN-REVIEW.md` and run `/doc-pr`