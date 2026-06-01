Documentation is part of implementation — keep it lightweight and selective.

Update or create docs only when changes affect:
- architecture or service boundaries
- API contracts
- database schema
- auth or security flows
- infrastructure
- major workflows or reusable patterns
- important engineering decisions

When producing command output (NNN-DESIGN.md, NNN-PLAN.md, etc.), follow the command's schema — do not invent structure.

Avoid:
- documenting trivial changes or what the code already makes obvious
- marketing language and vague explanations
