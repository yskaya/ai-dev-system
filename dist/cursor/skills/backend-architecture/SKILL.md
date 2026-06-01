---
name: backend-architecture
description: 'Apply backend architecture expertise. Use when deciding how responsibilities and contracts are split across the backend'

---

Domain ownership over technical layers; match structure to current scale.

Do:
- versioning policy with API contracts
- operational cost as a gate before any service or module split

Avoid:
- service splits before domain boundaries are clear (@microservices when decomposing)

Output: Read `schemas/DESIGN.md` for context. Update sections `System structure`, `API contracts`, `Data model` in `NNN-DESIGN.md` (create the file if missing).