---
name: architecture-docs
description: 'Apply architecture documentation expertise. Use when capturing why a system is shaped the way it is, for future maintainers'

---

Do:
- decision tables, short diagrams with prose — not file trees or code blocks
- Technical complexity: what makes this hard + scaling path and when it would flip
- edit only affected sections; leave the rest verbatim

Avoid:
- diagrams without explanatory prose
- file trees here (SETUP.md or NNN-PLAN.md instead)

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Update sections `Technical complexity`, `Key decisions` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only. Create `docs/ai/` if missing.
- Leave other sections unchanged.
- Use schema headings exactly; substitute real work id (`001`) when known.