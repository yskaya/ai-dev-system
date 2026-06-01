# 001 — Personal bookmarks — Review

> **Note:** Draft example — illustrates review output shape before a real `/review-code` run completes the initiative.

## Decision

**Request changes** — API and entity look sound; M2–M3 not implemented yet. Re-run review after plan tasks are checked.

## Blocking issues

None in current diff (entity + migration only).

## Warnings

- Add integration test for cross-user DELETE (404) when M2 ships
- Document 100-item soft cap or add pagination before prod

## Security

Not fully reviewed — run `/review-security` when POST handler accepts user URLs.

## Prod risks

Unbounded list query if user has many bookmarks — acceptable for MVP with monitoring; paginate in next initiative.

## Nice-to-haves

- Normalize URL (strip trailing slash) on insert
- Return 409 or merge policy for duplicate URLs per user
