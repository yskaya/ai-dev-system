---
description: 'Command exercising full handoff block shape'
triggers: '"rich handoff", "fixture next"'
model: sonnet
---

Skills: @skill-plain

Rich handoff command body.

**Artifact (required)**
- Read `schemas/SAMPLE.md` before writing.
- Update sections `Alpha`, `Beta` in `docs/ai/NNN-OUT.md` on disk — not chat-only. Create `docs/ai/` if missing.
- Leave other sections unchanged.
- Use schema headings exactly; substitute real work id (`001`) when known.

### Next Step
Review `NNN-OUT.md` (Alpha) and run `/cmd-minimal`