---
description: 'Review files, an area, or branch/PR diff for correctness and maintainability; rank findings P0–P3'
triggers: '"review code", "code review", "review diff", "review PR"'
model: opus
---

Anchor every finding to file:line. For diffs, check acceptance criteria in `NNN-PLAN.md` when available.

Do:
- flag bugs, unnecessary complexity, drift, weak error handling

Avoid:
- treating style preferences as blocking issues
- reviewing without understanding intended behavior first
- suggesting rewrites when focused fixes suffice

Auth, input handling, or external integrations → run `/review-security`, then fold results into this review.

Output: Read `schemas/REVIEW.md` for context. Create or update `NNN-REVIEW.md`.

**When done — print this as your final message:**

### Next recommended step
1. **Review** `NNN-REVIEW.md` — Check decision and P0–P3 findings.

Inspect project state and pick **one**:
- **diff touches auth, user input, secrets, or third-party/AI integrations** → `/review-security`
- **P0 or blocking issues remain** → `/debug`
- **approved or no blockers** → `/doc-pr`