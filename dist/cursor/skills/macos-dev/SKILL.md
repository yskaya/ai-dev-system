---
name: macos-dev
description: 'Apply native macOS app expertise. Use for SwiftUI structure, lifecycle, entitlements, and local integration boundaries — not generic web patterns.'
paths:
  - "**/*.swift"
  - "**/*.xcodeproj/**"
  - "**/*.entitlements"
  - "**/Info.plist"
---

Default: single-process SwiftUI app; `@MainActor` observable store for UI; domain logic off the main actor only when measured need exists.

Do:
- domain ownership table (module → responsibility → does NOT)
- explicit entitlements/privacy list — request none unless the feature requires it
- Keychain for secrets; Application Support for durable files; temp + rename for config edits
- `MenuBarExtra` / window style called out in system structure when menu bar or panel UI
- wire contracts as method + JSON/table when hooks, CLI, or loopback HTTP cross process boundaries

Avoid:
- web stack patterns (REST client layers, SSR, Nest modules) unless the macOS app is primarily a web shell
- Accessibility or Screen Recording entitlements for activity data — prefer tool hooks or explicit user action
- Core Data or SQLite before query/scale needs justify it
- per-view timers — one shared tick for live elapsed UI when needed

**Artifact (required)**
- Read `schemas/DESIGN.md` before writing.
- Update sections `System structure`, `API contracts`, `Data flow`, `Auth & trust model`, `Key decisions` in `docs/ai/NNN-DESIGN.md` on disk — not chat-only.
- Leave other sections unchanged.