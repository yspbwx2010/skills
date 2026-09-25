# Skills

[简体中文](README.md) | English

Some [Agent Skills](https://agentskills.io/specification) I use myself, only guaranteed to fit my own needs, nothing more promised

Each skill installs on its own, take only the ones you want

## Skill list

| Skill | For |
| --- | --- |
| [miuix](miuix/README.en.md) | Build apps with [Miuix](https://github.com/compose-miuix-ui/miuix) |
| [kpm](kpm/README.en.md) | Write [KernelPatch](https://github.com/bmax121/KernelPatch) modules (KPM) |
| [apm](apm/README.en.md) | Write Magisk modules (APM) |
| [metamodule](metamodule/README.en.md) | Write a [metamodule](https://kernelsu.org/guide/metamodule.html) |

## Install

> Replace `<skill>` with a name from the table above

### 1. Skills CLI (Claude Code, Codex, Cursor, OpenCode and 40+ other agents)

```bash
npx skills add yspbwx2010/skills --skill <skill>
npx skills add yspbwx2010/skills --list      # list every skill in the repo
```

### 2. Claude Code plugin marketplace

```text
/plugin marketplace add yspbwx2010/skills
/plugin install <skill>@yspbwx2010-skills
```

### 3. Manual copy

Copy `<skill>/skills/<skill>/` into your agent's skills directory, e.g. `~/.claude/skills/` for Claude Code

See each skill's README for other agents' directories

## Layout

One directory per skill; the README, changelog, maintenance notes and tooling all live in it, and only `<skill>/skills/<skill>/` is installed

For the full layout and the steps to add a skill, see [AGENTS.md](AGENTS.md)

## License

[MIT](LICENSE)
