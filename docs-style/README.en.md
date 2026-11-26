# docs-style

[简体中文](README.md) | English

Teach your Coding Agent to write English developer docs in a style adapted from the [Google developer documentation style guide](https://developers.google.com/style). It covers READMEs, procedures, concept and troubleshooting pages, release notes, and API reference comments. The rules are rewritten in my own words and kept to the mistakes that models still make without a guide

It also has a supplement for Chinese technical docs. Its default punctuation profile is my own half-width style (the one the Chinese README uses); a mainstream full-width profile is there for projects that ask for it

## What comes first

- **Facts outrank style**: facts from the source (error messages, UI locations, platform lists, hedges such as "might") are never deleted or weakened to satisfy a rule, and claims the source doesn't make aren't written
- **Project rules and the author's voice outrank the skill**: a project's style file, `AGENTS.md`, `CONTRIBUTING.md`, and the author's own punctuation and voice win; the skill only fills the gaps they leave

## What's included

- **Main file**: precedence, writing only the facts you were given, naming the actor, one term per concept, lead-ins for lists and code blocks, numbered procedures, placeholders, sentences and headings, and a final pass before handing the document back
- **Word list**: words to replace and what to use instead, kept as a table you can `grep`
- **Topic references**: API comments, code samples, formatting (dates, numbers, tables, images), links and UI, example data and inclusive language, read on demand
- **Chinese supplement**: two punctuation profiles, spacing between Chinese and Latin text, terminology, numbers and units, translationese and AI-sounding phrases
- **Checker**: `scripts/check_style.py`, standard-library Python, reports line numbers and rule names and never rewrites a file. It reads English Markdown prose only; Chinese docs use the self-check list in the supplement

## Results

I ran two rounds of blind paired judging with an LLM as the judge, 70 pairs in total, each pair being two documents written from the same brief with and without the skill, plus a 4-pair retest of Haiku in Chinese. Documents written with the skill were preferred in most pairs (round 3, English: 31 of 32) and had far fewer invented facts (35 against 171). They also had far fewer firm style problems (42 against 303), but that count uses the same rules the skill is built from, so it favors the skill; the invented-facts count says more. Weaker models such as Haiku still need a human check of facts and length, especially in Chinese

## Install

```bash
npx skills add yspbwx2010/skills --skill docs-style
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install docs-style@yspbwx2010-skills
```

or copy `docs-style/skills/docs-style/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## License

Adapted from the [Google developer documentation style guide](https://developers.google.com/style), which is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This adaptation is CC BY 4.0 too; what changed and what is original are listed in [LICENSE-NOTICE.md](skills/docs-style/LICENSE-NOTICE.md)

This skill is not affiliated with or endorsed by Google
