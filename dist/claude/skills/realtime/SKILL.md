---
name: realtime
description: 'Apply real-time transport expertise. Use for WebSocket, SSE, or subscription design when layered via @realtime'
triggers: '"realtime", "WebSocket", "SSE", "streaming", "live updates"'

---

Do:
- choose WebSocket vs SSE by directionality; define subscription lifecycle
- batch high-frequency updates; handle disconnect, retry, and re-auth on reconnect

Avoid:
- WebSockets when unidirectional SSE suffices
- query-string auth tokens on long-lived connections
- stateful connections without a pub/sub scaling path

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Update sections `Data flow`, `Key decisions` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only. Create `docs/ai/` if missing.
- Leave other sections unchanged.
- Use schema headings exactly; substitute real work id (`001`) when known.