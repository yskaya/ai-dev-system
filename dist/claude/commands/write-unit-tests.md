---
description: 'Add unit tests for behaviour and regressions against plan acceptance criteria'
triggers: '"write unit tests", "add tests", "generate tests"'

---

Read acceptance criteria in `NNN-PLAN.md` or regression steps in `ISSUES.md` when present. Match existing test patterns in the repo.

Do:
- test observable behaviour and edge cases for the changed area
- add a regression test when covering a bug fix from `/debug`
- prioritise critical paths, business logic, and unstable areas

Avoid:
- snapshot-heavy or implementation-coupled tests
- low-signal tests that only exercise mocks or internal structure

**When done — print this as your final message:**

### Next recommended step
Inspect project state and pick **one**:
- **unchecked tasks remain in NNN-PLAN.md** → `/build-step` with @set-web, @set-api, or @set-service
- **all plan tasks done or no plan in scope** → `/doc-pr`