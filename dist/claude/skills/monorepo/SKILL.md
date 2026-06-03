---
name: monorepo
description: 'Apply monorepo expertise for package boundaries and workspace layout. Layer via @monorepo when workspace structure or cross-package dependencies are in scope.'
triggers: '"monorepo", "workspace", "package boundaries"'

---

Do:
- one named domain per package; one shared package for cross-cutting code — not a grab-bag

Avoid:
- circular imports between packages

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Ensure the file starts with this header; prepend if missing (verbatim):
<!--
******************************************************
*****                AI GENERATED                *****
******************************************************
-->
- Update sections `System structure`, `Key decisions` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only.
- Leave other sections unchanged.