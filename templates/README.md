# Templates

Emitted file shapes for `scripts/build.py`. The build **loads these `.tmpl` files** and fills placeholders — keep templates and build logic in sync.

Placeholders:

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
| `{output_statement}` | when `source`/`output` | when `source`/`output` | — | — |

When changing output format, update **both** the template and any placeholder assembly in `scripts/build.py`, then run `python3 -m unittest discover -s tests`.
