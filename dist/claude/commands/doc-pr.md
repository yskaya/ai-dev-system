---
description: 'Draft a PR description from the diff — what changed, why, and how to verify'
triggers: '"doc pr", "PR description", "draft PR description", "PR summary"'

---

Read the diff plus `NNN-BRIEF.md` and `NNN-PLAN.md` if they exist. Keep the description short — reviewers skim.

```
## Summary
One or two sentences: what this PR does, in product terms.

## Why
The motivation — link to BRIEF/PLAN if available. Skip if obvious from Summary.

## Changes
Bullet list of meaningful changes, grouped by area. Skip trivial edits.

## Test plan
- [ ] How a reviewer can verify each acceptance criterion
- [ ] Any manual checks needed

## Notes
Anything reviewers should know — known gaps, follow-ups, risky bits. Omit if none.
```

Do:
- write in product terms; group meaningful changes by area
- tie test plan checkboxes to acceptance criteria from `NNN-PLAN.md` when available

Avoid:
- listing every file or pasting the diff
- more than 200 words outside the test plan checklist

**When done — print this as your final message:**

### Next recommended step
1. Open or update the PR with the drafted description.

Inspect project state:
- **initiative complete — all plan tasks checked and review approved** → `/create-brief` — Start the next initiative with a new NNN id, or run /plan-work for the next feature