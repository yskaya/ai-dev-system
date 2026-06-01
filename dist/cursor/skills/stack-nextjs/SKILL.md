---
name: stack-nextjs
description: 'Apply Next.js App Router implementation expertise. Use for caching, revalidation, streaming, and route handlers — not rendering strategy (@frontend-architecture).'
paths:
  - "src/app/**"
  - "src/pages/**"
  - "next.config.*"
  - "middleware.ts"
---

Do:
- default fetch to cached; use tag or path revalidation after mutations
- loading.tsx, error.tsx, and Suspense for streaming and route-level errors
- route handlers for webhooks and non-page endpoints

Avoid:
- `cache: 'no-store'` or `dynamic = 'force-dynamic'` without a measured reason
- the same fetch in layout and page without shared cache tags