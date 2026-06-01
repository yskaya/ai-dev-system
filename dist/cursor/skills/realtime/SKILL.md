---
name: realtime
description: 'Apply real-time transport expertise. Use for WebSocket, SSE, or subscription design when layered via @realtime'

---

Do:
- choose WebSocket vs SSE by directionality; define subscription lifecycle
- batch high-frequency updates; handle disconnect, retry, and re-auth on reconnect

Avoid:
- WebSockets when unidirectional SSE suffices
- query-string auth tokens on long-lived connections
- stateful connections without a pub/sub scaling path

Output: Read `schemas/DESIGN.md` for context. Update sections `Data flow`, `Key decisions` in `NNN-DESIGN.md` (create the file if missing).