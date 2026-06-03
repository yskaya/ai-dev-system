# Changelog

All notable changes to this project are documented here. Version tags follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-02

First public release — portable prompt system for Cursor and Claude Code.

### Added

- **9 slash commands:** `create-brief`, `design-web`, `plan-work`, `build-step`, `debug`, `review-code`, `review-security`, `write-unit-tests`, `doc-pr`
- **13 skills:** stack (`stack-react`, `stack-nextjs`, `stack-node`, `stack-nestjs`, `stack-ai`) and mode (`frontend-architecture`, `backend-architecture`, `architecture-docs`, `auth`, `ai-architecture`, `realtime`, `microservices`, `monorepo`)
- **4 skillsets:** `set-web`, `set-api`, `set-service`, `set-microservice` (mixed set manual-only)
- **3 always-on / scoped rules:** operating principles, fullstack TypeScript, documentation discipline
- **6 output schemas:** `BRIEF`, `DESIGN`, `PLAN`, `REVIEW`, `ISSUES`, `SETUP`
- **Workflow graph** (`recipes/workflows.yaml`) compiled into **Next recommended step** handoff blocks on every command
- **Dual-target build:** `recipes/` → `dist/cursor/` and `dist/claude/` via `scripts/build.py`
- **Remote install:** `curl | bash` from GitHub releases (`scripts/install-remote.sh`)
- **Local install:** `scripts/install.py` for forks and offline use
- **Examples:** [examples/minimal/](examples/minimal/) — sample `001-BRIEF` through `001-REVIEW` artifact trail
- **Tests:** recipe validation, golden fixtures, production dist smoke (39 tests)

### Platform support

- **Cursor:** `.mdc` rules, path-scoped skills, slash commands with workflow handoffs
- **Claude Code:** rules with `paths`, command `triggers` and `model` routing (Opus for design/review, Sonnet for planning)

[0.1.0]: https://github.com/yskaya/ai-dev-system/releases/tag/v0.1.0
