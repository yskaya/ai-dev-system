Goal: build web apps quickly, safely, and repeatedly under human control — smallest useful change that runs end-to-end.

Always:
- match existing codebase patterns; extend before parallel systems
- prefer direct implementations over clever abstractions
- stay in scope — no unrelated refactors, speculative features, new deps, or public API changes unless required
- do not rewrite working code without a clear reason

Default (most tasks):
- answer or edit directly
- no over-planning, unrelated file reads, new abstractions, or docs (see documentation rule)
- prefer implementation over excessive planning once uncertainty is low

Complex or risky tasks:
- briefly explain approach before editing
- incremental changes only
- document assumptions and tradeoffs when they matter

Stop vs proceed:
- stop if missing info risks wrong architecture, broken data flow, security issues, or wasted work
- stop if requirements conflict with the codebase — explain the mismatch
- otherwise state assumptions explicitly and proceed — never fill gaps silently

Design defaults (architecture or stack choices only):
- proven, boring technology over trendy unless there is a clear measurable advantage
- monoliths, simple modules, and synchronous flows unless operational pressure requires otherwise
- low operational and AI cost

Recipes/commands:
- `@<skill-name>` or `@<command-name>` in a body: load and apply in order before continuing; if unavailable, note and proceed
- command outputs (NNN-DESIGN.md, NNN-PLAN.md, etc.): follow the command schema — do not invent structure
- review commands: no Approve / go while P0 or blocking issues remain unresolved
- no relevant context attached: ask before proceeding

Workflow handoff:
- when a slash command session completes, your **last message** must include a `### Next recommended step` block
- follow the compiled **When done** section from the active command — do not invent a different workflow
- substitute the actual work id (`001`, not `NNN`) when known
- for branches, inspect project files (plan checkboxes, review P0s, diff scope) before recommending
- distinguish auto-attached skills (command `Skills:` line) from manual `@` skills
- keep the block concise — 2–4 lines plus optional skill notes
