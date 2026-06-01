---
name: microservices
description: 'Apply microservices decomposition expertise. Layer via @set-microservice or @microservices when service splits or cross-service boundaries are in scope.'

---

Do:
- justify each split with operational need — not domain size alone
- assign each service its own data store; no shared mutable DB
- choose sync vs async at service boundaries deliberately

Avoid:
- splitting before domain ownership is clear
- async where sync is simpler and sufficient
- service meshes before scale demands them

Output: Read `schemas/DESIGN.md` for context. Update sections `System structure`, `Data flow`, `Key decisions`, `Risks` in `NNN-DESIGN.md` (create the file if missing).