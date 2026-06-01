---
name: auth
description: 'Apply authentication and authorization expertise. Use whenever a task touches login, tokens, sessions, or any security-sensitive boundary'

---

Do:
- enforce authorization at the API/service layer — never UI-only
- revocation strategy alongside expiry

Avoid:
- custom token schemes when JWTs or sessions suffice
- mixing authentication and authorization in the same layer
- tokens in localStorage or non-HttpOnly cookies

Output: Read `schemas/DESIGN.md` for context. Update sections `Auth & trust model` in `NNN-DESIGN.md` (create the file if missing).