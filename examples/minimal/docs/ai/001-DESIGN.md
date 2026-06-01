# 001 — Personal bookmarks — Design

## Technical complexity

**Low.** CRUD on one table, scoped by `userId`. Reuses existing NestJS auth guard and Postgres.

## System structure

| Module | Responsibility |
|--------|----------------|
| `bookmarks` | Controller, service, DTOs, entity |
| `auth` (existing) | JWT validation; provides `userId` on request |
| `database` (existing) | TypeORM / Postgres connection |

Monolith — no new service boundary.

## API contracts

Internal REST (NestJS), JSON:

| Method | Path | Input | Output |
|--------|------|-------|--------|
| POST | `/bookmarks` | `{ url: string, title?: string }` | `{ id, url, title, createdAt }` |
| GET | `/bookmarks` | — | `{ items: Bookmark[] }` |
| DELETE | `/bookmarks/:id` | — | `204` |

All routes require `Authorization: Bearer <token>`.

## Data model

**Bookmark**

- `id` UUID PK
- `userId` UUID FK → User
- `url` string (max 2048)
- `title` string nullable (max 256)
- `createdAt` timestamp

Index: `(userId, createdAt DESC)` for list query.

## Auth & trust model

- **Trusted:** authenticated user from JWT
- **Untrusted:** request body URLs — validate with URL parser; reject non-http(s)
- Delete/update scoped: service loads by `id` **and** `userId`; 404 if not owner

## Data flow

1. Client POST → Auth guard → DTO validation → service insert with `userId` from token
2. Client GET → Auth guard → service `findByUserId` ordered by `createdAt`
3. Client DELETE → Auth guard → service delete where `id` + `userId`

## AI system

N/A

## Key decisions

| Decision | Chosen | Rejected | Why |
|----------|--------|----------|-----|
| Storage | Postgres row per bookmark | JSON blob on user | Queryable list, simple migrations |
| URL validation | Parse only; no HEAD fetch | Server-side title fetch | Avoid SSRF and latency in MVP |
| Ordering | `createdAt` desc | Manual sort order | No reorder UI in MVP |

## Risks

- Open redirect if URLs rendered as links without `rel="noopener"` — frontend concern; note in plan
- Large lists — paginate in v2; MVP cap at 100 with warning in API docs
