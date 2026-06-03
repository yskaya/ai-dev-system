---
name: architecture-docs
description: 'Apply architecture documentation expertise. Use when capturing why a system is shaped the way it is, for future maintainers'
triggers: '"architecture docs"'

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
- Update sections `Technical complexity`, `Key decisions` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only.
- Leave other sections unchanged.