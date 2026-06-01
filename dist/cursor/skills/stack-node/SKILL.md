---
name: stack-node
description: 'Apply Node.js runtime expertise. Use for event-loop safety, streams, and process lifecycle — not service layout (@backend-architecture).'

---

Do:
- wire `unhandledRejection`, `uncaughtException`, and SIGTERM/SIGINT graceful shutdown
- streams with backpressure for large I/O; worker_threads or a queue for CPU-bound work

Avoid:
- sync fs/net/crypto in request handlers or event callbacks
- buffering entire large payloads when a stream fits