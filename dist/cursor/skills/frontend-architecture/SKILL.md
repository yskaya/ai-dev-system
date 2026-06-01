---
name: frontend-architecture
description: 'Apply frontend architecture expertise. Use when deciding the client/server boundary and how each route renders and fetches'

---

Default to server components and one fetching pattern per feature.

Per route: client/server boundary, rendering mode (SSR / SSG / client), data source (RSC fetch vs client query).

Avoid:
- state management libraries for trivial data flows
- mixed fetching patterns in the same feature

Output: Read `schemas/DESIGN.md` for context. Update sections `System structure`, `Data flow`, `Key decisions` in `NNN-DESIGN.md` (create the file if missing).