# 001 — Personal bookmarks

## Goal

Let signed-in users save and list URLs on a personal dashboard so they can revisit links without browser bookmarks sync.

## MVP scope

Size: **S** — single resource, no tags, no sharing.

- Save a bookmark (URL + optional title)
- List the user's bookmarks (newest first)
- Delete a bookmark
- Auth required for all operations

Out of scope for MVP: folders, tags, import/export, public sharing.

## Non-goals

- Browser extension or bookmarklet
- Full-text search across saved pages
- Team or shared collections

## Success criteria

- Authenticated user can add a URL and see it in the list within one page load
- List returns only that user's bookmarks (no cross-user leakage)
- Delete removes the row; subsequent list omits it

## Assumptions

- Users already exist in the app (auth module present)
- URLs are stored as strings; no fetching or preview generation in MVP

## Risks

- Users paste malformed URLs — validate format, do not fetch arbitrary URLs server-side in MVP
- Duplicate URLs per user — allow duplicates in MVP; dedupe is a follow-up
