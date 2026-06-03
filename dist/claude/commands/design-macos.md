---
description: 'Design and document native macOS app architecture as NNN-DESIGN.md'
triggers: '"design macos", "macos architecture", "native mac app design", "swift app design"'
model: opus
---

Skills: @architecture-docs @macos-dev

Read NNN-BRIEF.md when present.

Document constraints, module boundaries, contracts, data flow, trust model, and key decisions — stay platform-agnostic unless a specialized design command applies.

Native Swift + SwiftUI macOS app — not a web stack. Omit web stack skills unless the app embeds a web view with a real contract.

Center the document on:
- process boundaries (app vs helpers, XPC, loopback HTTP, CLI hooks)
- UI shell (menu bar, window style, login item lifecycle)
- concurrency (`@MainActor` UI store vs background I/O)
- persistence and config mutation (Keychain, Application Support, atomic writes)
- entitlements and trust (sandbox, privacy permissions — justify each or omit)

Layer when scope requires it:
- Local HTTP/WebSocket ingress → document wire contract in API contracts
- AI/LLM inside the app → @ai-architecture

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Prepend this header at the very top of the file (verbatim):
<!--
******************************************************
*****                AI GENERATED                *****
******************************************************
-->
- Write `docs/ai/NNN-DESIGN.md` on disk — not chat-only. Create `docs/ai/` if missing. Use schema headings exactly.

### Next Step
Review `docs/ai/NNN-DESIGN.md` and run `/plan-work`