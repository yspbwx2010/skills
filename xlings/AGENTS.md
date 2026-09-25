# AGENTS.md — xlings

## What this skill is for

It teaches coding agents to use the [xlings](https://github.com/openxlings/xlings) package manager:
install, remove and switch versions with `use`, create and sandbox SubOS environments, run
project-mode `.xlings.json`, add index repos and mirrors, read its machine-readable output, write
[xim-pkgindex](https://github.com/openxlings/xim-pkgindex) packages, and work with the mcpp
integration (`MCPP_VENDORED_XLINGS`, `[xlings] deps`, which index a package belongs in).
Only `skills/xlings/` is installed: `SKILL.md` and `references/`.

It is written against **xlings 2026.9.20.1** (`metadata.xlings-version`).

## How it stays correct

Claims cite a source line (`file:line`), a doc or an issue/PR number. `SKILL.md` §0 records what
each version stamp rests on: CLI spellings were checked against `--help` on 2026.9.14.1; the
2026.9.16.1 and 2026.9.20.1 changes were read from source and merged PRs.
`references/upstream-doc-gaps.md` lists where upstream docs disagree with the implementation.

## Rules

- Put a fact in the skill only after reading the xlings source or running the command; cite it.
- Nothing under `skills/xlings/` may link outside that directory.
- Keep the `SKILL.md` body under 500 lines; detail goes in `references/`.
- Run `tools/validate_skill.py` and `../tools/check_repo.py` before committing; both must exit 0.
- When bumping the xlings version: add the release to `references/version-notes.md`, refresh the
  §0 stamp, update `metadata.xlings-version` in `SKILL.md`, and bump `version` in
  `.claude-plugin/plugin.json`.
