Apply only if the project uses TypeScript, React, Next.js, Node.js, or NestJS. Skip otherwise.

Use TypeScript with clear types. Avoid `any`.

Follow existing naming, folder structure, and style — do not introduce new patterns without a reason.

Frontend:
- functional React components
- client components only when needed
- handle loading, error, empty, and disabled states
- keep UI accessible

Backend:
- NestJS and Node.js conventions
- validate inputs at boundaries
- return consistent response shapes

Database:
- query only needed fields
- avoid unnecessary calls
- avoid schema changes unless required
