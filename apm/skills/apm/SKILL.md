---
name: apm
description: Build Magisk modules — standard Magisk-style systemless modules, as used by APatch on Android. Use when creating a module.prop, laying out a module zip, writing customize.sh / service.sh / post-fs-data.sh / boot-completed.sh / action.sh, doing systemless system changes via overlayfs (REPLACE / REMOVE), sepolicy.rule, system.prop, WebUI (webroot), or porting a Magisk/KernelSU module to APatch. Triggers on "Magisk module", "Magisk 模块", "APatch 模块", "APM", "module.prop", "customize.sh", "systemless", "把 Magisk 模块移植到 APatch".
license: MIT
compatibility: APM modules run on Android arm64 devices rooted with APatch. Scripts run in APatch's BusyBox ash "standalone mode". Building a module needs only a zip tool; no compiler.
metadata:
  apatch-version: "11224"
---

# Magisk module

This skill builds **Magisk modules** — standard Magisk-style systemless modules, as used by
[APatch](https://github.com/bmax121/APatch): they modify `/system` without touching the real
partition, run boot scripts, and install from a zip through the APatch manager. APatch's module
engine is derived from KernelSU's, so if you know Magisk/KernelSU modules this is familiar — the
differences are the ones that bite, and they are called out below.

This skill is written against **APatch manager 11224** (its `apd` daemon and installer). APM is
**not** KPM: a KPM is kernel-space C (see the `kpm` skill); an APM is files + shell.

## The two things that make an APM

1. A directory installed at `/data/adb/modules/<id>/` containing at least a **`module.prop`**.
2. Optionally a **`system/`** tree (mounted over `/system`), boot **scripts**, and metadata files.

Distributed as a **zip** flashed in the APatch manager. Minimum viable module:

```
mymodule.zip
├── module.prop            # required — without it, it is not a module
├── customize.sh           # optional install-time script
├── system/...             # optional, overlaid on /system
└── service.sh             # optional, runs late in boot
```

Use `scripts/new_module.py <dir> --id my_module --name "My Module"` to scaffold a valid zip layout.

## module.prop (required)

```
id=my_module
name=My Module
version=v1.0
versionCode=1
author=you
description=What it does
```

- **`id`** must match `^[a-zA-Z][a-zA-Z0-9._-]+$` (verified in `apd`). It is the directory name and
  is interpolated into shell commands, so a bad id is rejected at install. Do not change it after
  release. ✓ `a_module`, `a.module`, `module-101` ✗ `1_module`, `-mod`, `a module`.
- **`versionCode`** must be an integer; it is what version comparison uses.
- Use **LF** line endings, not CRLF.
- `apd` rejects a zip whose `module.prop` has no `id` (`module id not found in module.prop!`).

`references/module.md` has the full installed-directory layout and every marker file.

## Systemless `/system` changes are overlayfs, not magic mount

This is the biggest difference from Magisk. APatch overlays your `system/` on top of `/system`
using the kernel's **overlayfs**. Consequences:

- Files in your `system/` **override** same-path system files; directories **merge**.
- To **delete** a system file, don't omit it — create a whiteout: `mknod <path> c 0 0` in your
  module tree, or list it in a `REMOVE="..."` variable in `customize.sh` and APatch runs the
  `mknod` for you.
- To **replace** (not merge) a system directory, set `setfattr -n trusted.overlay.opaque -v y
  <dir>`, or list it in a `REPLACE="..."` variable in `customize.sh`.

`references/systemless.md` covers REMOVE/REPLACE, `system.prop` and `sepolicy.rule`.

## Scripts and when they run

Put `MODDIR=${0%/*}` at the top of every script to find your module dir — never hardcode the path.
All scripts run in APatch's BusyBox `ash` **standalone mode**.

| Script | Stage | Blocking? |
| --- | --- | --- |
| `post-fs-data.sh` | early, before modules mount, before zygote | yes (≤10s budget) |
| `post-mount.sh` | after modules are mounted | yes |
| `service.sh` | late_start service — **use this by default** | no (parallel) |
| `boot-completed.sh` | after Android finishes booting | no |
| `uninstall.sh` | when the module is removed | — |
| `action.sh` | when "Action" is tapped in the manager | — |

- In `post-fs-data.sh` never use `setprop` (deadlock) — use `resetprop -n <k> <v>`.
- Detect APatch at runtime with the env var **`APATCH=true`** (also `APATCH_VER`, `APATCH_VER_CODE`,
  `AP_MODULE`). `references/scripts.md` has the full boot flow and the env for each stage.

## Install-time: customize.sh

The installer extracts your zip to `$MODPATH` and, if present, **sources** `customize.sh`. Declare
`SKIPUNZIP=1` to take over the whole install yourself. Available helpers: `ui_print`, `abort`,
`set_perm`, `set_perm_recursive`, and variables `MODPATH`, `TMPDIR`, `ZIPFILE`, `ARCH` (always
`arm64`), `API`, `IS64BIT`, `BOOTMODE`, plus APatch/KernelPatch ones (`APATCH`, `APATCH_VER_CODE`,
`KERNELPATCH_VERSION`, `SUPERKEY`, …). `references/installer.md` lists them all and the exact
install order.

## Differences from Magisk / KernelSU (read before porting)

- **No Zygisk.** APatch has no built-in Zygisk; Zygisk modules don't work as-is.
- **Paths:** APatch uses `/data/adb/ap/…` (KernelSU: `/data/adb/ksu/…`); busybox at
  `/data/adb/ap/bin/busybox`.
- **overlayfs**, not Magisk's magic mount (see above).
- **Compatibility shims:** `customize.sh` sees `MAGISK_VER`/`MAGISK_VER_CODE` set to values that
  change between releases (30.0 / 30000 in 11224) — **read them, don't hardcode**.
- **APatch-only:** WebUI (`webroot/`), per-stage Lua scripts (`<id>.lua`), and **metamodules**
  (`metamodule=1` modules that own mounting/installation). A metamodule with a custom installer can
  **block** installing ordinary modules until reboot. See `references/module.md` and
  `references/webui.md`.

## References

Read on demand.

- `references/module.md` — installed layout, module.prop, markers, metamodules.
- `references/scripts.md` — boot stages, the full boot flow, per-stage env, general `.d` scripts.
- `references/installer.md` — zip format, customize.sh variables and functions, install order.
- `references/systemless.md` — overlayfs REMOVE/REPLACE, system.prop, sepolicy.rule.
- `references/webui.md` — WebUI (`webroot/`), the Action button, Lua stage scripts.
