# AGENTS.md — mcpp-style-ref

## What this skill is for

It teaches coding agents the Modern/Module C++ (C++23) style used across mcpp projects: identifier
naming, module and `.cppm`/`.cpp` organisation, `import std`, and everyday idioms. Only
`skills/mcpp-style-ref/` is installed: `SKILL.md`, `reference.md` and `LICENSE`.

## Where it comes from

This is the upstream skill from the mcpp community's
[mcpp-style-ref](https://github.com/mcpp-community/mcpp-style-ref), taken at commit `c9ddaf7`
(2026-03-10). It is licensed **CC BY-NC-SA 4.0**, not MIT like the rest of this repository; the
licence text ships as `skills/mcpp-style-ref/LICENSE`.

Changes from upstream, kept to what this repository's layout requires:

- two relative links into the upstream repository (`README.md`, `src/`) are now absolute URLs;
- `license: CC-BY-NC-SA-4.0` was added to the frontmatter.

## Rules

- Don't rewrite the style here. Style changes go upstream; this copy follows upstream.
- Keep `skills/mcpp-style-ref/LICENSE`, and keep the list of changes above complete.
- Nothing under `skills/mcpp-style-ref/` may link outside that directory.
- Run `tools/validate_skill.py` and `../tools/check_repo.py` before committing; both must exit 0.
