---
name: stack-nestjs
description: 'Apply NestJS implementation expertise. Use for modules, guards, DTOs, DI, and interceptors — not domain or API design (@backend-architecture).'
triggers: '"nestjs stack"'
paths:
  - "**/*.controller.ts"
  - "**/*.service.ts"
  - "**/*.module.ts"
  - "**/*.guard.ts"
  - "**/*.dto.ts"
  - "**/*.pipe.ts"
  - "**/*.interceptor.ts"
---

Do:
- controllers route and validate only; services own business rules
- DTOs with class-validator at the HTTP boundary
- scope guards and interceptors to module or controller as needed

Avoid:
- repositories or ORM clients injected into controllers
- circular module imports