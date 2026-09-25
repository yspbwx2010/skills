# Contributing to the miuix skill

How to maintain the **miuix** skill: the layout, the gates, following a new Miuix release, and
writing traps. It applies to people and coding agents alike. Users of the skill never need this
file — everything they need is under `skills/miuix/`. For the repository as a whole (adding a
skill, the marketplace), see the [root CONTRIBUTING.md](../CONTRIBUTING.md).

Run every command below from this directory (`miuix/`).

Found something the skill gets wrong? Open an issue with the Miuix version, what the agent wrote,
and the compile error or the wrong behaviour. A trap is only accepted with the source line that
proves it (see [Writing a trap](#writing-a-trap-datagotchasyaml)).

## Layout

```
skills/miuix/            the skill itself — this directory is what gets installed
  SKILL.md               entry point, loaded whenever the skill activates (keep < 500 lines)
  references/            GENERATED topic files + index.md, read on demand
  assets/template/       a minimal, buildable Compose Multiplatform app on Miuix
  scripts/new_app.py     copies the template into an empty directory (stdlib only)
data/
  miuix-api.json         GENERATED from Miuix source by tools/sync.py
  gotchas/*.yaml         hand-written facts: traps, visual specs, state, vs-Material3
  recipes/*.md           hand-written combinations (rendered into references/recipes.md); compile each before adding
tools/                   maintainer tooling, never installed
.claude-plugin/          Claude Code plugin manifest (the marketplace is at the repository root)
.miuix-src/              your local Miuix checkout for the gates (git-ignored, see below)
```

CI is `.github/workflows/miuix.yml` at the repository root; it runs every gate below and builds
the template.

Anything under `skills/miuix/` is copied onto users' machines on its own, so nothing in it may
link outside that directory (`tools/validate_skill.py` enforces this).

## The rule that shapes everything

Miuix's own docs drifted from its source because the examples are hand-written and nothing
checks them. A skill that copies API into Markdown rots the same way. So:

| Layer | Source | Kept honest by |
| --- | --- | --- |
| Signatures, types, defaults, icons | `tools/sync.py` extracts them from Kotlin source | `sync.py --check` |
| `references/*.md` | `tools/render.py` renders data + gotchas | `render.py --check` |
| Traps / specs / state / vs M3 | `data/gotchas/*.yaml`, hand-written | every trap cites `path:line`; `check_evidence.py` |
| Every Miuix symbol in SKILL.md and references | — | `check_skill.py` |
| Skill format | — | `validate_skill.py` (Agent Skills spec + links) |
| The template | — | CI builds it for Android, desktop and web |

**Never hand-edit `references/` or `data/miuix-api.json`.** Edit the YAML or the tools, then re-render.

## Gates

```bash
git clone --branch v0.9.4 --depth 1 https://github.com/compose-miuix-ui/miuix.git .miuix-src   # once
export PYTHONDONTWRITEBYTECODE=1
python3 tools/test_sync.py                          # parser self-test
python3 tools/validate_skill.py                     # Agent Skills spec + links stay inside the skill
python3 tools/check_skill.py                        # every Miuix symbol named in the skill exists
python3 tools/render.py --check                     # references/ matches data/
python3 tools/sync.py --src .miuix-src --check      # data/ matches the Miuix source
python3 tools/check_evidence.py --src .miuix-src    # every path:line evidence exists
```

All must exit 0. When you add a gate, break it on purpose once and watch it fail.

## Updating to a new Miuix release

Target the **release tag**, not `main`. Users depend on what Maven Central serves; a breaking
change that only exists on `main` would make the skill produce code that does not compile
against the release (0.9.4 is the example: right after the tag, `main` renamed a
`BreadcrumbBar` parameter and changed every `pagerGestureOverride` overload).

1. `git -C .miuix-src fetch --tags && git -C .miuix-src checkout <new-tag>`
2. `python3 tools/check_evidence.py --src .miuix-src --rebase <old-tag> --write`
   Shifts evidence line numbers through the diff and lists citations whose line itself changed.
   A shifted number only proves that one line is unchanged — the trap may still be fixed.
3. `python3 tools/sync.py --src .miuix-src && python3 tools/render.py`
   If render reports a source file "is unclassified", add it to `UI_BASIC` / `UI_DIR`
   in `tools/render.py`.
4. Re-verify, against the new source, every YAML entry that cites a changed file
   (`git -C .miuix-src diff --stat <old-tag> <new-tag>`), and write entries for new public API.
5. Update `skills/miuix/SKILL.md`: the version paragraph (breaking changes since the previous
   release, plus what is already on `main` but unreleased), the template's versions in
   `assets/template/common/gradle/libs.versions.toml`, and `.claude-plugin/plugin.json`'s `version`.
6. Run all gates, then build the template (see the `template` job in CI).

## Writing a trap (`data/gotchas/*.yaml`)

The YAML is read by a restricted parser in `tools/render.py` (no PyYAML dependency), so copy
the shape of existing entries exactly: two-space indent, double-quoted strings,
`- text:` followed by `severity:` and `evidence:` at the same indent.

```yaml
NavigationRail:                     # top-level fun name; extension: "Modifier.foo"; type or val name
  summary: "..."
  gotchas:
    - text: "What goes wrong, why (the mechanism), and what to write instead."
      severity: high                # high = compile error, crash or clearly wrong behaviour
      evidence: miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:142-154
  visual: { key: "value" }          # optional
  state: "..."                      # optional: who owns the state
  m3: "..."                         # optional: difference from Material3
```

- Evidence must be the line that **proves** the sentence — read it with `sed -n` before citing.
- One entry per name across all files; overloads share it.
- No "fixed in x.y" tombstones: delete traps that no longer hold. If an old behaviour still bites
  people on older versions, write "since 0.9.4 …, before that …".
- Don't write what you have not verified.

## Checking that the skill works from scratch

The skill's real test is an agent in an **empty directory** that knows nothing about Miuix.
Before a release, give one or more fresh agents only `skills/miuix/` plus a realistic app request
(for example a settings app on Android + desktop, or a plain Android app with a pager) and have
them build it, logging every place the skill was missing, wrong or ambiguous. Fix those, repeat.
