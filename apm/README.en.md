# apm

[简体中文](README.md) | English

Teach your Coding Agent to write **Magisk modules**: [APatch](https://github.com/bmax121/APatch) uses standard Magisk systemless modules: `module.prop`, the zip + `customize.sh` install flow, changing `/system` via overlayfs, boot scripts, `sepolicy.rule`, WebUI

Targets **APatch manager 11224**. The rules come from APatch's `apd` daemon and installer, not just the docs (which lag; e.g. the `MAGISK_VER_CODE` shim is 30000 in the installer, 27000 in the doc)

## What it does

- **Module layout**: the installed `/data/adb/modules/<id>/` tree, the marker files (`skip_mount` / `disable` / `remove`), and `module.prop` with the id regex `apd` enforces
- **Systemless the APatch way**: overlayfs, not Magisk's magic mount; how to add, delete (whiteout / `REMOVE`) and replace (`REPLACE` / opaque attr) system paths
- **Scripts**: the boot stages, which one blocks boot, the real `apd` ordering, per-stage env (`APATCH=true`, etc.), common `.d` scripts, Lua stage scripts
- **Install**: the zip format, `customize.sh` variables and functions, `SKIPUNZIP`, the exact install order
- **Extras**: WebUI (`webroot/`), the Action button, metamodules (including how a custom-installer metamodule blocks regular-module installs)
- **Porting**: the differences from Magisk / KernelSU (no Zygisk, `/data/adb/ap/` paths, overlayfs, arm64 only, the `APATCH` env var)
- **Scaffold**: `scripts/new_module.py` generates a valid module skeleton (and an optional flashable zip)

## Install

```bash
npx skills add yspbwx2010/skills --skill apm
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install apm@yspbwx2010-skills
```

or copy `apm/skills/apm/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## License

[MIT](../LICENSE)
