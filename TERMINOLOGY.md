# Terminology rules

**For any agent or person editing this manuscript.**

`TERMINOLOGY.yaml` is the single source of truth for what things are called. This file is
the short version of how to use it.

## The rule

1. **Never settle a terminology question by writing prose.** Change `TERMINOLOGY.yaml`
   first, then run the linter, then change the source.
2. **Never introduce a synonym.** If a concept already has a canonical form, use it. If it
   does not, add it to the canon before using it.
3. **Run `python3 scripts/termlint.py` before every commit.** Nonzero exit means the source
   has drifted from the canon.

## Commands

```
python3 scripts/termlint.py              # lint; errors only
python3 scripts/termlint.py -w           # include warnings
python3 scripts/termlint.py --json       # machine-readable, for agents
python3 scripts/termlint.py --list       # the whole canon as a table
python3 scripts/termlint.py --term ID    # one term's full entry
python3 scripts/termlint.py --actions    # the items no linter can check
```

`--actions` is the important one. Most of the real work is not string substitution: it is
adding a footnote that distinguishes this Article's term from an established term in a
neighbouring field. Those items live in the canon under `anchor`, `collision`,
`consolidation` and similar keys, and `--actions` prints them ranked.

## The three statuses

| Status | Meaning | Your obligation |
|---|---|---|
| `anchored` | A standard scholarly or statutory term exists and is adopted | Use it exactly. Do not vary it. |
| `coined` | The Article's own term for a concept with no standard name | Define once with `\term{}`. Never vary the wording. |
| `borrowed` | Imported from an adjacent literature | Cite the source at first use. Do not rename what that literature already named. |

Coining is legitimate and this Article does a lot of it. The failure mode is not coining;
it is coining where a standard term already exists, or coining and then drifting.

## Suppressing a deliberate exception

Put a pragma on the line, or the line before it:

```latex
A sentence that deliberately uses a banned form.  % termlint: allow front_door
% termlint: allow-line
```

Use these sparingly and say why in the same comment. Every suppression is a place a future
reader will ask a question.

## Known structural hazards

- `ailaw/source/*.tex` is byte-identical to `article/*.tex` and **nothing includes it**.
  Only `article/` is compiled by `what-is-ai-for-courts.tex`. An edit made in
  `ailaw/source/` will silently not appear. Delete that tree or make it a symlink.
- The docx output is still named `before-the-merits.docx`, from an earlier title. Rename
  before anything goes to an editor.

## Adding a term

```yaml
  - id: snake_case_id
    canonical: "the exact string"
    status: coined            # anchored | coined | borrowed
    define_at: "03-front-door-rule.tex (\\term)"
    gloss: "One sentence."
    short_forms: ["licensed shorthand"]
    banned:
      - form: "the variant to kill"
        replace: "the exact string"
        why: "Why this is drift and not a useful distinction."
        severity: error       # error | warn
```

Add `case_sensitive: true` to a banned form when only the capitalisation is wrong.
