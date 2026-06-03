---
name: backend-architecture
description: 'Apply backend architecture expertise. Use when deciding how responsibilities and contracts are split across the backend'
triggers: '"backend architecture", "API design", "service design"'

---

Domain ownership over technical layers; match structure to current scale.

Do:
- versioning policy with API contracts
- operational cost as a gate before any service or module split

Avoid:
- service splits before domain boundaries are clear (@microservices when decomposing)

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Update sections `System structure`, `API contracts`, `Data model` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only. Create `docs/ai/` if missing.
- Leave other sections unchanged.
- Use schema headings exactly; substitute real work id (`001`) when known.