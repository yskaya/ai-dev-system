---
description: 'Command exercising full handoff block shape'
triggers: '"rich handoff", "fixture next"'
model: sonnet
---

Skills: @skill-plain

Rich handoff command body.

Output: Read `schemas/SAMPLE.md` for context. Update sections `Alpha`, `Beta` in `NNN-OUT.md` (create the file if missing).

**When done — print this as your final message:**

### Next recommended step
1. **Review** `NNN-OUT.md` (Alpha section) — Verify alpha section content.
2. **Run** `/cmd-minimal` @skill-scoped, or @skill-plain to proceed after rich handoff.
   _Branch skills are illustrative only_

_Alternatively:_
- **condition A applies** → `/cmd-skills-direct` with @skill-plain (use plain skill here)
- **condition B applies** — note-only branch without command

_Also:_ if optional follow-up needed, run `/cmd-skills-skillset`.

_Layer manually if scope requires:_ `@skill-output` (layer when output sections matter)