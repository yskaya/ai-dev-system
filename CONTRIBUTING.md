# Contributing

Thanks for helping improve ai-dev-system. This repo is a **recipe compiler** — you edit YAML/Markdown in `recipes/`, run tests, and cut releases. Users install the built artifacts; they do not need Python in their app repos.

For day-to-day usage (not contributing), see [GUIDE.md](GUIDE.md).

## Prerequisites

- Python 3.10+
- PyYAML: `pip install -r requirements.txt`

## Quick loop

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests
```

After changing `templates/` or `scripts/build.py`, regenerate golden files:

```bash
python3 tests/generate_expected.py
python3 -m unittest discover -s tests
```

## What lives where

| Path | You edit when… |
|------|----------------|
| `recipes/skills/*.yaml` | Adding or tuning expertise (stack or design mode) |
| `recipes/commands/*.yaml` | Adding or tuning slash workflows |
| `recipes/rules/*.md` + `rules.yaml` | Always-on or path-scoped guardrails |
| `recipes/schemas/*.md` | Output document shapes |
| `recipes/skillsets.yaml` | Bundling skills (`@set-web`, …) |
| `recipes/workflows.yaml` | Command transition graph → **Next recommended step** blocks |
| `recipes/project.yaml` | Project paths (`artifact_dir`) compiled into commands, skills, rules |
| `recipes/outputs.yaml` | Schema index (validation only) |
| `templates/` | Platform-specific emitted shapes (Cursor `.mdc`, Claude frontmatter) |
| `scripts/build.py` | Compiler logic |

Do **not** hand-edit `dist/` — it is build output. Commit `dist/` changes when cutting releases so remote install works.

## Adding a skill

1. Create `recipes/skills/<id>.yaml`:

```yaml
name: my-skill          # must match filename stem
description: One-line purpose for the agent picker
triggers:               # optional; Claude frontmatter
  - my skill phrase
paths: '**/*.ts'        # optional; stack skills only — Cursor auto-attach globs
body: |
  Instruction text the agent follows when this skill is active.
```

2. **Stack skill** (`stack-*`): implementation expertise; may declare `paths`.
3. **Mode skill** (bare name): design/reasoning; wire via command `skills:` or manual `@mention`.
4. Rebuild and test. If the skill updates a design doc section, add `source`, `output`, and `sections`.

Optional: add to `recipes/skillsets.yaml` if it belongs in a bundle.

## Adding a command

1. Create `recipes/commands/<id>.yaml`:

```yaml
name: my-command        # must match filename stem
description: One-line purpose shown in the command picker
triggers:               # optional; Claude
  - my command
source: schemas/PLAN.md # optional; schema binding
output: NNN-PLAN.md     # optional; target doc pattern
skills:                 # optional; expanded at build (tech-only skillsets OK)
  - stack-react
body: |
  What the agent should do.
targets:                # required on every command
  claude:
    model: sonnet       # or opus
  cursor: {}            # Cursor-oriented commands use empty cursor target
```

2. Add an entry in `recipes/workflows.yaml` — **every command must have one**. Tests enforce coverage.
3. If the command references a schema, ensure the file exists and is listed in `recipes/outputs.yaml`.
4. Rebuild and test.

**Skillset rule:** mixed skillsets (e.g. `set-microservice` = stack + design mode) must **not** appear in a command's `skills:` list. Users layer those with `@set-microservice` at invoke time. Enforced in `tests/test_recipes.py`.

## Changing rules

1. Edit body Markdown in `recipes/rules/<id>.md`.
2. Update index in `recipes/rules/rules.yaml` (description, `alwaysApply`, globs for Cursor).
3. Rebuild and test.

## Pull requests

- Keep changes focused — one skill, one command, or one workflow fix per PR when possible.
- Run the full test suite before opening a PR.
- Update [GUIDE.md](GUIDE.md) if user-facing behavior or command reference changes.
- Update [examples/minimal/](examples/minimal/) if the canonical workflow or artifact shapes change materially.

## Releases (maintainers)

See [README — Publish a release](README.md#publish-a-release-maintainers). Tag `v*` pushes trigger CI to rebuild, package, and attach `ai-dev-system-dist.tar.gz`. Update [CHANGELOG.md](CHANGELOG.md) when cutting releases.

## Questions

Open a [GitHub issue](https://github.com/yskaya/ai-dev-system/issues) for bugs, skill requests, or workflow ideas.
