---
name: frontend-architecture
description: 'Apply frontend architecture expertise. Use when deciding the client/server boundary and how each route renders and fetches'
triggers: '"frontend architecture", "rendering strategy", "client server boundary"'

---

Default to server components and one fetching pattern per feature.

Per route: client/server boundary, rendering mode (SSR / SSG / client), data source (RSC fetch vs client query).

Avoid:
- state management libraries for trivial data flows
- mixed fetching patterns in the same feature

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Ensure the file starts with this header; prepend if missing (verbatim):
<!--
******************************************************
*****                AI GENERATED                *****
******************************************************
-->
- Update sections `System structure`, `Data flow`, `Key decisions` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only.
- Leave other sections unchanged.