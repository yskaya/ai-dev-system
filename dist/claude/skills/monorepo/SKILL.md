---
name: monorepo
description: 'Apply monorepo expertise for package boundaries and workspace layout. Layer via @monorepo when workspace structure or cross-package dependencies are in scope.'
triggers: '"monorepo", "workspace", "package boundaries"'

---

Do:
- one named domain per package; one shared package for cross-cutting code — not a grab-bag

Avoid:
- circular imports between packages

Output: Read `schemas/DESIGN.md` for context. Update sections `System structure`, `Key decisions` in `NNN-DESIGN.md` (create the file if missing).