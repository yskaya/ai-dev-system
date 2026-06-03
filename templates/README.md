# Templates

Emitted file shapes for `scripts/build.py`. The build **loads these `.tmpl` files** and fills placeholders — keep templates and build logic in sync.

## Layout

| Path | Used by |
|---|---|
| `cursor/command.tmpl`, `claude/command.tmpl` | Slash commands |
| `cursor/skill.tmpl`, `claude/skill.tmpl` | Skills |
| `cursor/rule.tmpl`, `claude/rule.tmpl` | Rules |
| `_shared/artifact-header.tmpl` | HTML comment prepended to generated docs — edit banner here |
| `_shared/artifact-write.tmpl` | Full write — `source` + `output`, no `sections` |
| `_shared/artifact-edit.tmpl` | Section update — `source` + `output` + `sections` |
| `_shared/artifact-read.tmpl` | `source` only (e.g. `/build-step`) |
| `_shared/next-step.tmpl` | `next:` only — no review line |
| `_shared/next-step-review.tmpl` | `source` + `output` + `review` + `next` |

**Shared partials** hold the markdown structure. `scripts/build.py` loads `recipes/project.yaml` for `{artifact_dir}`, normalizes recipe fields into placeholder dicts, then renders partials via `_render_partial()`.

## Project config (`recipes/project.yaml`)

| Field | Default | Used in |
|---|---|---|
| `artifact_dir` | `docs/ai` | artifact partials, next-step review path, rules |

Override at build: `--artifact-dir` or env `AI_DEV_ARTIFACT_DIR`.  
Override per app at install: `.ai-dev-system.yaml` in project root or `install.py --artifact-dir`.

## Command / skill placeholders

| Placeholder | Command | Skill | Rule (cursor) | Rule (claude) |
|---|---|---|---|---|
| `{description}` | yes | yes | yes | — |
| `{triggers_line}` | claude only | claude only | — | — |
| `{model_line}` | claude only | — | — | — |
| `{skills_block}` | if `skills:` set | — | — | — |
| `{name}` | — | yes | — | — |
| `{paths_block}` | — | stack-* only | — | scoped only |
| `{globs_block}` | — | — | scoped only | — |
| `{alwaysApply}` | — | — | yes | — |
| `{paths_block}` | — | — | — | scoped only |
| `{body}` | yes | yes | yes | yes |
| `{output_statement}` | from `_shared/artifact-*.tmpl` | same | — | — |
| `{next_step_block}` | from `_shared/next-step*.tmpl` | — | — | — |

## Artifact partials

Template picked in `_artifact_template_and_values()` from recipe fields:

| Template | When |
|---|---|
| `artifact-write.tmpl` | `output:` set, no `sections:` |
| `artifact-edit.tmpl` | `output:` and `sections:` set |
| `artifact-read.tmpl` | `source:` only (no `output:`) |

Placeholders (normalized from recipe YAML):

| Placeholder | From |
|---|---|
| `{source}` | `source:` |
| `{artifact_dir}` | `project.yaml` → `artifact_dir` |
| `{output_path}` | `output:` via `_artifact_path()` |
| `{sections}` | `sections:` as `` `A`, `B` `` |
| `{artifact_header}` | rendered from `artifact-header.tmpl` (write/edit only) |

## Next-step partials

Template picked in `_next_step_template_and_values()` from command recipe + `workflows.yaml`:

| Template | When |
|---|---|
| `next-step-review.tmpl` | command has `source` + `output` and workflow has `next` |
| `next-step.tmpl` | workflow has `next`, no review doc (no `source`/`output`) |

Placeholders:

| Placeholder | From |
|---|---|
| `{output_path}` | command `output:` via `_artifact_path()` |
| `{review_section}` | workflow `review_section:` (optional, e.g. ` (Security)`) |
| `{next}` | workflow `next:` |

Workflow entry shape in `recipes/workflows.yaml`:

```yaml
create-brief:
  next: design-web
```

Empty placeholders drop their line from the output (`_apply_template`).

When changing output format, update the relevant `_shared/*.tmpl` and/or value builders in `scripts/build.py`, then:

```bash
python3 scripts/build.py all
python3 tests/generate_expected.py
python3 -m unittest discover -s tests
```

See `tests/README.md` for fixture layout.
