---
name: auth
description: 'Apply authentication and authorization expertise. Use whenever a task touches login, tokens, sessions, or any security-sensitive boundary'
triggers: '"auth", "login"'

---

Do:
- enforce authorization at the API/service layer — never UI-only
- revocation strategy alongside expiry

Avoid:
- custom token schemes when JWTs or sessions suffice
- mixing authentication and authorization in the same layer
- tokens in localStorage or non-HttpOnly cookies

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Update sections `Auth & trust model` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only.
- Leave other sections unchanged.