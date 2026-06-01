# 001 — Personal bookmarks — Plan

## Scope

In-scope: bookmarks CRUD API + minimal dashboard list UI hook-up.  
Deferred: pagination, dedupe, tags.

## Milestones

Complete tasks in milestone order; mark done with `- [x]`.

### M1 — Data layer

- [x] Add `Bookmark` entity and migration — `src/bookmarks/bookmark.entity.ts`, migration file — migration runs; table exists with index on `(userId, createdAt)`
- [ ] Register `BookmarksModule` in app — `src/app.module.ts` — app boots; module wired

### M2 — API

- [ ] POST `/bookmarks` — `bookmarks.controller.ts`, `bookmarks.service.ts`, DTOs — valid URL returns 201; invalid URL 400; unauthenticated 401
- [ ] GET `/bookmarks` — same files — returns only caller's rows, newest first
- [ ] DELETE `/bookmarks/:id` — same files — owner deletes 204; other user's id 404

### M3 — Client (minimal)

- [ ] Bookmark form + list on dashboard — `app/dashboard/page.tsx` — user can add and see entries after refresh

## Execution sequence

M1 → M2 → M3. Do not start UI until API acceptance criteria pass.

## External dependencies

None — uses existing auth and database setup.

## Risks

- Migration on shared dev DB — coordinate with team before running locally
