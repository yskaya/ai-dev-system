# ai-dev-system

Portable prompt system for **Cursor** and **Claude Code**: skills, slash commands, always-on rules, and output-document schemas. Edit YAML/Markdown in `recipes/`; build emits installable artifacts in `dist/`.

**Repo:** [github.com/yskaya/ai-dev-system](https://github.com/yskaya/ai-dev-system) · **Latest release:** [v1.0.0](https://github.com/yskaya/ai-dev-system/releases) · **License:** [MIT](LICENSE)

**Using the system in your projects?** Start with [GUIDE.md](GUIDE.md) (philosophy, workflows, commands/skills reference). This README is the technical reference for installing, building, and extending the package. See [examples/minimal](examples/minimal/) for sample `docs/ai/` artifacts.

## Quickstart (use in a project)

Install predefined rules, commands, skills, and schemas into your app — no clone, no Python:

```bash
curl -fsSL https://raw.githubusercontent.com/yskaya/ai-dev-system/main/scripts/install-remote.sh | bash
```

This writes into your project:

| Path | Contents |
|---|---|
| `.cursor/rules/` | Always-on and path-scoped rules |
| `.cursor/commands/` | Slash commands (`/create-brief`, `/build-step`, …) |
| `.cursor/skills/` | Agent skills (stack, architecture, auth, …) |
| `.cursor/schemas/` | Output document shapes (`BRIEF.md`, `DESIGN.md`, …) |
| `.claude/…` | Same layout for Claude Code (omit with `--cursor-only`) |

Then open the project in Cursor and run a command, e.g. `/create-brief` → `docs/ai/001-BRIEF.md`. See [GUIDE.md](GUIDE.md) for the full workflow.

**Pin a version** (recommended for teams):

```bash
AI_DEV_SYSTEM_VERSION=v1.0.0 curl -fsSL \
  https://raw.githubusercontent.com/yskaya/ai-dev-system/main/scripts/install-remote.sh | bash
```

**Reinstall / upgrade:** run the same command again. Each install replaces the previous `.cursor/` (and `.claude/`) artifact trees.

## Two ways to install

| | **Remote install** | **Local install** |
|---|---|---|
| **For** | App developers using the package as-is | Maintainers editing `recipes/` |
| **Requires** | `curl`, `tar`, `bash` | Python 3, clone of this repo |
| **Command** | `install-remote.sh` (see below) | `build.py` + `install.py` |
| **Gets updates from** | GitHub releases (or `main` fallback) | Your local `recipes/` after rebuild |

## Install into a project

### Remote install (recommended)

From any project directory:

```bash
curl -fsSL https://raw.githubusercontent.com/yskaya/ai-dev-system/main/scripts/install-remote.sh | bash
```

Options (pass after `bash -s --`):

```bash
# target directory (default: current directory)
curl -fsSL https://raw.githubusercontent.com/yskaya/ai-dev-system/main/scripts/install-remote.sh \
  | bash -s -- /path/to/your-project

# Cursor only (skip .claude/)
curl -fsSL https://raw.githubusercontent.com/yskaya/ai-dev-system/main/scripts/install-remote.sh \
  | bash -s -- --cursor-only .

# Claude only
curl -fsSL https://raw.githubusercontent.com/yskaya/ai-dev-system/main/scripts/install-remote.sh \
  | bash -s -- --claude-only .
```

**How it works**

1. Fetches `ai-dev-system-dist.tar.gz` from the [latest GitHub release](https://github.com/yskaya/ai-dev-system/releases).
2. If no release exists, falls back to the `main` branch source archive (uses committed `dist/`).
3. Extracts and copies `cursor/` → `.cursor/` and `claude/` → `.claude/` (rules, commands, skills, schemas).

**Environment variables**

| Variable | Default | Purpose |
|---|---|---|
| `AI_DEV_SYSTEM_REPO` | `yskaya/ai-dev-system` | GitHub `owner/repo` |
| `AI_DEV_SYSTEM_VERSION` | *(latest release)* | Pin to a tag, e.g. `v1.0.0` |
| `AI_DEV_SYSTEM_REF` | `main` | Branch for source-archive fallback |

### Local install (from a clone)

For recipe development, forks, or offline use:

```bash
git clone https://github.com/yskaya/ai-dev-system.git
cd ai-dev-system
pip install -r requirements.txt   # only needed for build/tests
python3 scripts/build.py
python3 scripts/install.py /path/to/your-project              # cursor + claude
python3 scripts/install.py --cursor-only /path/to/your-project
python3 scripts/install.py --claude-only /path/to/your-project
```

After editing `recipes/`, rebuild and reinstall:

```bash
python3 scripts/build.py
python3 scripts/install.py /path/to/your-project
```

## Publish a release (maintainers)

When you change `recipes/` and want remote users to get the update:

```bash
# 1. Build and test locally
pip install -r requirements.txt
python3 scripts/build.py
python3 -m unittest discover -s tests

# 2. Commit dist/ changes (if any) and push to main
git add -A && git commit -m "..." && git push origin main

# 3. Tag and push — CI publishes the release tarball
git tag v1.0.1
git push origin v1.0.1
```

The [Release workflow](.github/workflows/release.yml) on tag push (`v*`):

1. Runs tests
2. Rebuilds `dist/`
3. Packages `ai-dev-system-dist.tar.gz` via `scripts/package-release.sh`
4. Creates a [GitHub release](https://github.com/yskaya/ai-dev-system/releases) with the tarball attached

Remote install picks up the new version automatically (or users pin with `AI_DEV_SYSTEM_VERSION=v1.0.1`).

**First-time repo setup** (one-time):

```bash
gh auth login
gh repo create yskaya/ai-dev-system --public --source=. --remote=origin --push
git tag v1.0.0 && git push origin v1.0.0
```

Use your actual GitHub username in place of `yskaya` if forking.

## Package

| Piece | Role |
|---|---|
| `recipes/` | **Source** — skills, commands, rules, schemas, skillsets, workflows |
| `scripts/build.py` | **Compiler** — recipes → platform-specific Markdown |
| `dist/cursor/`, `dist/claude/` | **Build output** — ready to copy into a project |
| `scripts/install.py` | **Local installer** — `dist/*` → `.cursor/` and `.claude/` |
| `scripts/install-remote.sh` | **Remote installer** — GitHub release → project (curl-able) |
| `scripts/package-release.sh` | **Release packager** — `dist/` → `ai-dev-system-dist.tar.gz` |
| `templates/` | **Templates** — `.tmpl` files loaded by `build.py` for emitted shapes |
| `tests/` | Fixture golden files (`fixtures/` → `expected/`) + recipe validation + production dist smoke |

**Dependencies:** Python 3 + PyYAML (`requirements.txt`).

## Source → output

You define platform-neutral recipes; the build produces two parallel trees.

| You define (recipes/) | You get (dist/) |
|---|---|
| `skills/<id>.yaml` — `name`, `description`, `body`, optional `paths`, `source`/`output`/`sections` | `skills/<id>/SKILL.md` with YAML frontmatter + body + optional `Output:` line |
| `commands/<id>.yaml` — `name`, `description`, `body`, optional `skills`, `source`/`output`/`sections`, `targets` | `commands/<id>.md` — Cursor: description only; Claude: + `triggers`, optional `model`; + compiled **Next recommended step** handoff block |
| `rules/rules.yaml` + `rules/*.md` bodies | Cursor: `rules/<id>.mdc` (`alwaysApply`, optional `globs`); Claude: `rules/<id>.md` (`paths` when scoped) |
| `schemas/*.md` | Copied verbatim to `schemas/` |
| `skillsets.yaml` — named skill bundles | Expanded inline in command `Skills: @…` lines (tech-only sets only) |
| `workflows.yaml` — command transition graph | Compiled into each command as a **When done** / **Next recommended step** block |
| `outputs.yaml` — schema index | Drives which schemas are copied to `dist/` |

**Field quick reference**

| Field | Used in | Purpose |
|---|---|---|
| `name` | skills, commands | Id (must match filename stem) |
| `description` | skills, commands, rules | One-line purpose |
| `triggers` | skills, commands | Optional phrases (Claude frontmatter) |
| `body` | skills, commands | Instruction text |
| `paths` | stack-* skills | Comma-separated globs for auto-attach |
| `source` | commands, design skills | Schema path, e.g. `schemas/DESIGN.md` |
| `output` | commands, design skills | Target doc, e.g. `NNN-DESIGN.md` |
| `sections` | design skills, some commands | Schema section headings to update |
| `skills` | commands | YAML list of skills/skillsets (expanded at build) |
| `targets` | commands, rules | Per-platform options — see below |

**Claude models:** use `targets.claude.model: opus` or `sonnet` (canonical short ids; build normalizes legacy `claude-opus` / `routing` if present).

**`targets` on commands:** required on every command. Sets Claude frontmatter (`model`). All commands emit to **both** `dist/cursor/` and `dist/claude/`; empty `cursor: {}` marks Cursor-oriented commands (e.g. `/build-step`).

**Skill kinds**

- **stack-*** — implementation expertise; may declare `paths:` for auto-attach
- **bare name** — reasoning/design mode; wire via command `skills:` or manual `@` layering

Mixed skillsets (e.g. `set-microservice`) must **not** appear in a command's `skills:` list — layer with `@set-microservice` instead. Enforced in `tests/test_recipes.py`.

## Build

```bash
pip install -r requirements.txt
python3 scripts/build.py                   # all targets (cursor + claude)
python3 scripts/build.py cursor            # cursor only
python3 scripts/build.py claude            # claude only
python3 scripts/build.py all design-web    # filter by command/skill/rule/schema id or schema token
python3 scripts/build.py claude auth       # example: auth skill + related commands
python3 scripts/build.py cursor build-step # filter examples
python3 scripts/build.py claude design
```

Each target writes `dist/<target>/manifest.json` listing generated paths. Filtered builds update matching files and **remove stale artifacts** from that target.

## Standards (formats this build targets)

Emitted files follow current platform conventions as of **2025–2026**:

| Platform | Artifact | Standard |
|---|---|---|
| **Cursor** | Rules | [Project Rules](https://cursor.com/docs/context/rules) — `.mdc` with `description`, `alwaysApply`, optional `globs` |
| **Cursor** | Skills | [Agent Skills](https://cursor.com/docs/context/skills) — `<name>/SKILL.md`, frontmatter `name`, `description`, optional `paths` |
| **Cursor** | Commands | `.cursor/commands/*.md` with YAML frontmatter (`description`) |
| **Claude Code** | Rules | `.claude/rules/*.md` with optional `paths` frontmatter for file-scoped rules |
| **Claude Code** | Skills / commands | Frontmatter includes `triggers`; commands may set `model` |

When platform formats change, update `scripts/build.py` and `templates/`, then run tests.

## Quickstart (contributors)

```bash
git clone https://github.com/yskaya/ai-dev-system.git
cd ai-dev-system
pip install -r requirements.txt
python3 scripts/build.py
python3 -m unittest discover -s tests
```

## Document convention (`NNN`)

`NNN` is a zero-padded work id (e.g. `001`, `002`). Default path prefix: `docs/ai/`. Mapping of schemas → commands → filenames is in [GUIDE.md — Work id](GUIDE.md#work-id-nnn) and [GUIDE.md — Commands reference](GUIDE.md#commands-reference).

## Layout

```
recipes/
├── skills/           one YAML per skill
├── commands/         one YAML per slash command
├── schemas/          output doc shapes (also copied to dist/)
├── rules/            always-on / path-scoped rules
│   └── rules.yaml    rule index + cursor targeting
├── skillsets.yaml    named bundles (set-web, set-api, …)
├── workflows.yaml    command transition graph → next-step handoff blocks
└── outputs.yaml      schema metadata index (validation only)
```

## Tests

```bash
python3 -m unittest discover -s tests
```

Tests validate recipes, rebuild `dist/`, and assert rules, skillset expansion, schemas, triggers, and output formatting.

See [templates/README.md](templates/README.md) for emitted file shapes.

## Contributing

Fork-friendly: edit `recipes/`, run tests, open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for skills, commands, workflows, and release notes.
