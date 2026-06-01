# Tests

## Layout

| Path | Role |
|------|------|
| `fixtures/recipes/` | Minimal recipe tree exercising every build variation |
| `expected/{cursor,claude}/` | Golden output — full file match after build |
| `helpers.py` | Build fixture dist, frontmatter parsing, golden compare |
| `test_fixture_outputs.py` | Template/build golden files + semantic assertions |
| `test_build_outputs.py` | Smoke tests on production `recipes/` → `dist/` |
| `test_recipes.py` | Recipe index validation (workflows, skillsets, filenames) |
| `generate_expected.py` | Regenerate `expected/` after template or `build.py` changes |

## Run

```bash
python3 -m unittest discover -s tests
```

## Fixture coverage

**Rules**

- `rule-always` — `alwaysApply: true` (Cursor); empty frontmatter (Claude)
- `rule-scoped` — globs / paths for `**/*.ts`, `**/*.tsx`

**Skills**

- `skill-plain` — no `paths`; Claude `triggers`
- `skill-scoped` — `paths` for auto-attach
- `skill-output` — `source`, `output`, `sections` → output line

**Commands**

- `cmd-minimal` — output statement, simple default next step, Claude `model: opus`
- `cmd-skills-direct` — direct `skills:` list
- `cmd-skills-skillset` — skillset expands to members (not bundle id)
- `cmd-next-rich` — review, default with branch skills, branches, also, manual_skills
- `cmd-next-branches` — branch-only handoff with skill suffix and note

## Update golden files

After changing `templates/` or `scripts/build.py`:

```bash
python3 tests/generate_expected.py
python3 -m unittest discover -s tests
```
