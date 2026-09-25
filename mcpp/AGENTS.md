# AGENTS.md — mcpp

## What this skill is for

It teaches coding agents to use [mcpp](https://github.com/mcpp-community/mcpp), the C++23 modules
build tool: build, test and gate, write `mcpp.toml`, run workspaces, choose toolchains and cross
targets, keep the caches honest, wire machine-readable output into CI, file issues and PRs against
mcpp itself, and package a library into [mcpp-index](https://github.com/mcpplibs/mcpp-index).
Only `skills/mcpp/` is installed: `SKILL.md` and `references/`.

It is written against **mcpp 2026.9.24.1** (`metadata.mcpp-version`).

## How it stays correct

Claims cite where they came from: a source line (`[file:line]`), a doc, or an issue/PR number.
Where the docs and the source disagree, the skill follows the source and says so. `SKILL.md` §0
records, for each version stamp, what was read, what was run and what was only read from source.

## Rules

- Put a fact in the skill only after reading the mcpp source or running the command; cite it.
- Nothing under `skills/mcpp/` may link outside that directory.
- The `SKILL.md` body is at the 500-line limit; new detail goes in `references/`.
- Run `tools/validate_skill.py` and `../tools/check_repo.py` before committing; both must exit 0.
- When bumping the mcpp version: add the release to `references/version-notes.md`, refresh
  `references/whats-new.md` and the §0 stamp, update `metadata.mcpp-version` in `SKILL.md`, and bump
  `version` in `.claude-plugin/plugin.json`.
