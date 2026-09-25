# AGENTS.md — miuix

## What this skill is for

It teaches coding agents to build apps with [Miuix](https://github.com/compose-miuix-ui/miuix)
(`top.yukonga.miuix.kmp`), the Compose Multiplatform UI library that recreates Xiaomi's HyperOS
look. An agent that has installed it can:

- scaffold a compiling Android / desktop / web project in an empty directory;
- write Miuix UI code that compiles on the first try;
- avoid the traps that make Miuix code fail to compile or look wrong.

Only `skills/miuix/` is installed: `SKILL.md`, the generated `references/`, the project template
in `assets/template/`, and `scripts/new_app.py`. Everything else in this directory is maintainer
tooling. The skill's text is written in Chinese, for Miuix's main community.

It targets the Miuix **release** it was synced to: `source_ref` in `data/miuix-api.json`, currently
v0.9.4. Never target `main`.

## How it stays correct

Signatures are extracted from the Miuix source (`tools/sync.py`). `references/` is rendered from
that data plus the hand-written `data/gotchas/*.yaml` and `data/recipes/*.md` (`tools/render.py`).
Every trap cites the `path:line` in the Miuix source that proves it. Gates check each layer against
the source, and CI (`.github/workflows/miuix.yml` at the repository root) runs them and builds the
template.

[CONTRIBUTING.md](CONTRIBUTING.md) has the full layout, the gates, the upgrade procedure and how to
write a trap. Read it before changing anything here. Run commands from `miuix/`.

## Rules that are easiest to break

- Never hand-edit `skills/miuix/references/` or `data/miuix-api.json`. Edit `data/gotchas/*.yaml`,
  `data/recipes/*.md` or `tools/`, then run `python3 tools/render.py`.
- Nothing under `skills/miuix/` may link outside that directory.
- Every trap cites the `path:line` in the Miuix source that proves it. Don't write what you have
  not verified.
- Run every gate in CONTRIBUTING.md before you commit; all must exit 0.
