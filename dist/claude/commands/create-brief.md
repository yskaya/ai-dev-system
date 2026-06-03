---
description: 'Create product brief for new products/greenfield. For existing system changes, use /plan-work'
triggers: '"create brief", "product brief", "new product"'
model: opus
---

Capture just enough to start design or planning. 
Focus on product intent (what and why), not implementation details.

**Artifact (required)**
- Read `schemas/BRIEF.md` before writing.
- Write `docs/ai/NNN-BRIEF.md` on disk — not chat-only. Create `docs/ai/` if missing.
- Use schema headings exactly; substitute real work id (`001`) when known.

### Next Step
Review `NNN-BRIEF.md` and run `/design-web`