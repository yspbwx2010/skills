# metamodule

[简体中文](README.md) | English

Teach your Coding Agent to write a **metamodule**: the pluggable module mount / install backend in [KernelSU](https://github.com/tiann/KernelSU) (and [APatch](https://github.com/bmax121/APatch), which adopted the design). A metamodule (`module.prop` with `metamodule=1`) decides, via `metamount.sh` / `metainstall.sh` / `metauninstall.sh`, how regular modules mount onto `/system` and how they install. Without one, KernelSU mounts nothing

Checked against KernelSU's `ksud` source and the official [metamodule guide](https://kernelsu.org/guide/metamodule.html), cross-checked against APatch's `apd`

## What it does

- **The contract**: `metamodule=1`, the `meta-` id convention, the single-instance rule, the `/data/adb/metamodule` symlink
- **The three hooks**: `metamount.sh` (the mount backend; env `MODULE_DIR`; every mount must use source `"KSU"`), `metainstall.sh` (sourced during a regular install, has `install_module`), `metauninstall.sh` (cleanup; the module id is the `MODULE_ID` env var, not `$1`, a doc-vs-source trap)
- **Boot order**: exactly when `metamount.sh` runs (after all post-fs-data), and that it is blocking
- **The install block**: why regular-module installs get refused (a metamodule with `metainstall.sh` in an unstable state) and how to clear it
- **Reference impl**: how `meta-overlayfs` works (dual-directory + ext4 image), plus a minimal bind-mount metamodule
- **KernelSU vs APatch**: the env-var and busybox-path differences
- **Scaffold**: `scripts/new_metamodule.py` generates a valid metamodule (and an optional zip)

## Install

```bash
npx skills add yspbwx2010/skills --skill metamodule
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install metamodule@yspbwx2010-skills
```

or copy `metamodule/skills/metamodule/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## License

[MIT](../LICENSE)
