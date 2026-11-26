# apm

[简体中文](README.md) | English

Teach your Coding Agent to write **Magisk-style systemless modules** for [APatch](https://github.com/bmax121/APatch) and [KernelSU](https://github.com/tiann/KernelSU): `module.prop`, the zip + `customize.sh` install flow, changing `/system`, boot scripts, `sepolicy.rule`, WebUI

Targets **APatch manager 11224** and **KernelSU v3.3.1**. Both managers now leave mounting to a metamodule: with no mounting metamodule installed, a module's `system/` is not mounted. The rules come from APatch's `apd`, KernelSU's `ksud` and their installers, not just the docs (which lag; e.g. the `MAGISK_VER_CODE` shim is 30000 in the installer, 27000 in the doc)

## What it does

- **Module layout**: the installed `/data/adb/modules/<id>/` tree, the marker files (`skip_mount` / `disable` / `remove`), and `module.prop` with the id regex `apd` enforces
- **Systemless**: the metamodule does the mounting (`meta-overlayfs` uses overlayfs, a magic-mount metamodule uses bind mounts); how to add, delete (whiteout / `REMOVE`) and replace (`REPLACE` / opaque attr; on KernelSU v3 the metamodule must define `mark_replace`) system paths
- **Scripts**: the boot stages, which one blocks boot (KernelSU: up to 35 s per stage; APatch: no timeout), the real ordering in each manager (`post-fs-data` and the mount run in opposite order), per-stage env (`APATCH=true` / `KSU=true`, etc.), common `.d` scripts, Lua stage scripts
- **Install**: the zip format, `customize.sh` variables and functions, `SKIPUNZIP`, the exact install order
- **Extras**: WebUI (`webroot/`), the Action button, metamodules (including how a custom-installer metamodule blocks regular-module installs)
- **Porting**: the differences from Magisk (no Zygisk, `/data/adb/ap/` and `/data/adb/ksu/` paths, mounting depends on the metamodule, APatch is arm64 only, the `APATCH` / `KSU` env vars)
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
