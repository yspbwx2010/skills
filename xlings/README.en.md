# xlings

[简体中文](README.md) | English

Teach your Coding Agent to use the **[xlings](https://github.com/openxlings/xlings)** package manager: install and remove packages, switch versions with `use`, create and sandbox SubOS environments, project-mode `.xlings.json`, custom index repos, mirrors and CN networking, machine-readable output for CI and agents, and its integration with mcpp

Targets **xlings 2026.9.20.1**. CLI spellings were checked against `--help` on 2026.9.14.1; the two later releases were read from source and merged PRs

## What it does

- **Commands**: every flag of the 16 top-level commands and 5 command groups, aliases, exit codes
- **Configuration and layout**: global and project `.xlings.json` field by field, the home layout, where payloads land, environment variables and the `XLINGS_HOME` resolution chain
- **SubOS**: create, use, sandbox, and keep homes from leaking into each other
- **Machine output**: the four output layers, all 20 capabilities, NDJSON events, CI wiring
- **Troubleshooting**: indexed by symptom (self update deadlocks, a mirror that changes nothing, a SubOS that does not describe itself ...)
- **Packaging**: the full recipe for an xim-pkgindex package (`spec = "2"`, hooks, `xvm.add`, mirrors), and whether a package belongs in xim-pkgindex or mcpp-index
- **mcpp integration**: `MCPP_VENDORED_XLINGS`, `[xlings] deps`, two homes that never read each other
- **Upstream doc gaps**: where the upstream docs disagree with the implementation

## Install

```bash
npx skills add yspbwx2010/skills --skill xlings
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install xlings@yspbwx2010-skills
```

or copy `xlings/skills/xlings/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## License

[MIT](../LICENSE)
