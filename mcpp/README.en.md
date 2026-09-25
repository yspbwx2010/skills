# mcpp

[简体中文](README.md) | English

Teach your Coding Agent to use **[mcpp](https://github.com/mcpp-community/mcpp)**, the C++23 modules build tool: build, test and gate, `mcpp.toml`, workspaces, toolchains and cross-compilation, caches, machine-readable output for CI, issues and PRs against mcpp itself, and packaging a library into [mcpp-index](https://github.com/mcpplibs/mcpp-index)

Targets **mcpp 2026.9.24.1**. Claims cite their source (a `file:line` in the mcpp source, a doc, an issue number); where the docs and the source disagree, the source wins

## What it does

- **Corrections to read first**: `build` / `test` / `run` default to the dev profile, `mcpp.lock` only binds with `--locked`, false greens from the fast path replaying a build, false greens from mtime-only staleness after a `tar` / `cp -p` rollback, `MCPP_HOME` inferred from the binary and not relocatable
- **Everyday commands and gating**: command semantics and traps, machine-readable output (envelope, NDJSON events, every `reason` token), the test system, gate cost on a large workspace
- **Configuration**: `mcpp.toml` section by section, workspace inheritance, `cfg()` predicates, dependency selectors, `[hooks]` and `build.mcpp` / `mcpp::action`
- **Cross and heterogeneous**: target selection, toolchains, wasm / Android / iOS, freestanding bare metal, accelerators and build plugins
- **Caches**: what each cache keys on and how to clean it safely
- **Troubleshooting**: a failure manual indexed by symptom
- **Version history**: every user-visible change from 2026.9.1.1 to 2026.9.24.1, with the spelling to type
- **Contributing upstream**: issue and commit style, the self-hosted build, CI, the release flow, rules for talking to upstream
- **Packaging**: mcpp-index descriptor fields, features, GLOBAL + CN mirrors, lint, local verification in an isolated home

## Install

```bash
npx skills add yspbwx2010/skills --skill mcpp
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install mcpp@yspbwx2010-skills
```

or copy `mcpp/skills/mcpp/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## License

[MIT](../LICENSE)
