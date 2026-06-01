# ai-dev-system

Portable prompt system for **Cursor** and **Claude Code**: skills, slash commands, always-on rules, and output-document schemas. Edit YAML/Markdown in `recipes/`; build emits installable artifacts in `dist/`.

**Using the system in your projects?** Start with [GUIDE.md](GUIDE.md) (philosophy, workflows, commands/skills reference). This README is the technical reference for building and extending the package.

## Package

| Piece | Role |
|---|---|
| `recipes/` | **Source** — skills, commands, rules, schemas, skillsets |
| `scripts/build.py` | **Compiler** — recipes → platform-specific Markdown |
| `dist/cursor/`, `dist/claude/` | **Build output** — ready to copy into a project |
| `scripts/install.py` | **Installer** — `dist/*` → `.cursor/` and `.claude/` |
| `templates/` | **Templates** — `.tmpl` files loaded by `build.py` for emitted shapes |
| `tests/` | Recipe validation + build output assertions |

**Dependencies:** Python 3 + PyYAML (`requirements.txt`).

## Source → output

You define platform-neutral recipes; the build produces two parallel trees.

| You define (recipes/) | You get (dist/) |
|---|---|
| `skills/<id>.yaml` — `name`, `description`, `body`, optional `paths`, `source`/`output`/`sections` | `skills/<id>/SKILL.md` with YAML frontmatter + body + optional `Output:` line |
| `commands/<id>.yaml` — `name`, `description`, `body`, optional `skills`, `source`/`output`/`sections`, `targets` | `commands/<id>.md` — Cursor: description only; Claude: + `triggers`, optional `model` |
| `rules/rules.yaml` + `rules/*.md` bodies | Cursor: `rules/<id>.mdc` (`alwaysApply`, optional `globs`); Claude: `rules/<id>.md` (`paths` when scoped) |
| `schemas/*.md` | Copied verbatim to `schemas/` |
| `skillsets.yaml` — named skill bundles | Expanded inline in command `Skills: @…` lines (tech-only sets only) |
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

## Install into a project

### Remote install (recommended)

From any project directory — no clone, no Python:

```bash
curl -fsSL https://raw.githubusercontent.com/ykanapatskaya/ai-dev-system/main/scripts/install-remote.sh | bash
```

With options:

```bash
# target directory (default: cwd)
curl -fsSL https://raw.githubusercontent.com/ykanapatskaya/ai-dev-system/main/scripts/install-remote.sh | bash -s -- /path/to/your-project

# Cursor only
curl -fsSL ... | bash -s -- --cursor-only .

# pin a release
AI_DEV_SYSTEM_VERSION=v1.0.0 curl -fsSL ... | bash
```

Downloads the latest [GitHub release](https://github.com/ykanapatskaya/ai-dev-system/releases) asset (`ai-dev-system-dist.tar.gz`). If no release exists yet, falls back to the `main` branch source archive (uses committed `dist/`).

Environment overrides: `AI_DEV_SYSTEM_REPO`, `AI_DEV_SYSTEM_VERSION`, `AI_DEV_SYSTEM_REF`.

### Local install (from a clone)

For recipe development or offline use:

```bash
python3 scripts/build.py
python3 scripts/install.py /path/to/your-project              # cursor + claude
python3 scripts/install.py --cursor-only /path/to/your-project
python3 scripts/install.py --claude-only /path/to/your-project
```

Copies `dist/cursor/*` → `.cursor/` and `dist/claude/*` → `.claude/` (rules, commands, skills, schemas).

## Publish a release

Tag a version to build, test, package, and attach `ai-dev-system-dist.tar.gz` to a GitHub release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The [Release workflow](.github/workflows/release.yml) runs tests, rebuilds `dist/`, and publishes the tarball.

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

## Quickstart

```bash
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
└── outputs.yaml      schema metadata index (validation only)
```

## Tests

```bash
python3 -m unittest discover -s tests
```

Tests validate recipes, rebuild `dist/`, and assert rules, skillset expansion, schemas, triggers, and output formatting.

See [templates/README.md](templates/README.md) for emitted file shapes.
