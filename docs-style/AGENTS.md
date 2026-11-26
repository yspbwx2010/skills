# AGENTS.md — docs-style

## What this skill is for

It helps coding agents write, edit and review English developer documentation: READMEs,
procedures, concept and troubleshooting pages, release notes, and API reference comments. The style
is adapted from the [Google developer documentation style guide](https://developers.google.com/style)
and condensed to the mistakes that capable models still make without a guide. A Chinese supplement
covers Chinese technical docs; its default punctuation profile is the maintainer's own half-width
style, and a mainstream full-width profile is available when a project asks for it.

Two rankings sit above every style rule. Facts from the source come first: a rule never deletes or
weakens an error message, a UI location, a platform list or a hedge. Then a project's own rules and
the author's voice outrank this skill, which fills only the gaps they leave.

It is used by agents working in any repository that writes developer docs, and by people who want an
agent's drafts to read like edited documentation.

## What gets installed

Only `skills/docs-style/` is installed:

- `SKILL.md`: precedence, the facts rules, and the rules that a baseline test showed models miss.
- `LICENSE-NOTICE.md`: the CC BY 4.0 attribution, the list of changes, and what is original.
- `reference/`: topic references read on demand (API comments, code samples, formatting, links and
  UI, examples and inclusive language), the word list, and the Chinese supplement `zh.md`.
- `scripts/check_style.py` and its data file `scripts/word_list.tsv`: a standard-library checker
  that reports findings with line numbers and rule names and never rewrites a file. It reads English
  Markdown prose only.

## Layout

```
docs-style/
  skills/docs-style/          the installable skill (above)
  tools/validate_skill.py     Agent Skills spec: frontmatter, SKILL.md size, links stay inside the skill
  .claude-plugin/plugin.json  plugin manifest (name, version, license)
  README.md, README.en.md     for users (Chinese is the default)
  AGENTS.md, CLAUDE.md        this file; CLAUDE.md is `@AGENTS.md`
```

CI (`.github/workflows/docs-style.yml`) runs `tools/validate_skill.py` and the checker's
`--self-test`.

## Rules

- **Licence.** The skill is an adaptation under CC BY 4.0, and the adaptation is CC BY 4.0 too. Keep
  `skills/docs-style/LICENSE-NOTICE.md`, the `license: CC-BY-4.0` frontmatter, and the attribution
  section of `SKILL.md`. When a change adds, drops or reworks material, update the list of changes in
  `LICENSE-NOTICE.md` in the same commit.
- **Own words.** Write every rule and example in your own words. Never copy sentences, examples or
  tables from the Google guide, and never include its code samples (they are Apache 2.0).
- **Facts first.** Facts from the source outrank style rules. A rule must never ask the agent to
  delete or weaken a source fact; the agent rewords around the fact instead.
- **Google's rules match Google.** A rule presented as Google's must match what the guide says. Check
  the guide before adding or changing one, and don't attribute a guess to it.
- **Own rules are marked.** A rule that is the skill's own, or that departs from the guide, says so
  where it appears ("this skill's own", "a skill row"), and `LICENSE-NOTICE.md` lists it.
- **Test before release.** Before releasing a change to the rules, test it with and without the
  skill on the same briefs, and compare the outputs.
- **Checker.** `scripts/check_style.py` only reports and never edits. When you change a rule it
  checks, update `word_list.tsv` or the script and its built-in cases, and keep
  `python3 skills/docs-style/scripts/check_style.py --self-test` passing.
- Nothing under `skills/docs-style/` may link outside that directory, and nothing there may cite a
  local path or a private project of the maintainer.
- Keep the `SKILL.md` body under 500 lines; put detail in `reference/`.
- Run `tools/validate_skill.py` and `../tools/check_repo.py` before committing; both must exit 0.
- When releasing, bump `version` in `.claude-plugin/plugin.json`.
