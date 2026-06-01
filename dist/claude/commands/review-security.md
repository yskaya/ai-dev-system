---
description: 'Adversarial audit of attack surface; rank risks P0–P3 with mitigations'
triggers: '"review security", "security review"'
model: opus
---

Skills: @auth

Report only — do not edit application source.

Audit auth boundaries, input validation, secrets, third-party and AI integrations, and data exposure. Anchor every finding to file:line; rank P0–P3 by exploitability and impact. P0 blocks release.

Summarize findings in the **Security** section of `NNN-REVIEW.md`. For findings that need tracking or a minimal fix plan, add entries to `NNN-ISSUES.md` (or `ISSUES.md` for unnumbered work) following `schemas/ISSUES.md`.

Do:
- check bypasses, privilege escalation, and data leaks
- verify token expiry and revocation on auth flows

Avoid:
- flattening severities into one priority
- rewriting unrelated `NNN-REVIEW.md` sections
- skipping third-party and AI integration surfaces

Output: Read `schemas/REVIEW.md` for context. Update sections `Security` in `NNN-REVIEW.md` (create the file if missing).

**When done — print this as your final message:**

### Next recommended step
1. **Review** `NNN-REVIEW.md` (Security section) — Check security findings and P0–P3 rankings.

Inspect project state and pick **one**:
- **P0 security findings need tracking or investigation** → `/debug` — Findings may also be appended to NNN-ISSUES.md or ISSUES.md
- **no P0 blockers** → `/doc-pr`