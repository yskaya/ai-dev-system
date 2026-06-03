---
description: 'Adversarial audit of attack surface; rank risks P0–P3 with mitigations'
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

**Artifact (required)**
- Read `schemas/REVIEW.md` before writing.
- Update sections `Security` in `docs/ai/NNN-REVIEW.md` on disk — not chat-only. Create `docs/ai/` if missing.
- Leave other sections unchanged.
- Use schema headings exactly; substitute real work id (`001`) when known.

### Next Step
Review `docs/ai/NNN-REVIEW.md` (Security) and run `/doc-pr`