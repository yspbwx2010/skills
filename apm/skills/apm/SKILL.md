---
name: apm
description: Build Magisk-style systemless root modules for APatch and KernelSU on Android, including the metamodule era where the root manager no longer mounts modules itself. Use when creating a module.prop, laying out a module zip, writing customize.sh / service.sh / post-fs-data.sh / post-mount.sh / boot-completed.sh / action.sh, doing systemless /system changes (system/, REPLACE / REMOVE), sepolicy.rule, system.prop, WebUI (webroot), or porting a Magisk module to APatch or KernelSU. Triggers on "Magisk module", "Magisk 模块", "APatch 模块", "KernelSU 模块", "KSU 模块", "APM", "module.prop", "customize.sh", "systemless", "元模块", "把 Magisk 模块移植到 APatch/KernelSU".
license: MIT
compatibility: Modules run on Android arm64 devices rooted with APatch (manager 11224 or later) or KernelSU (v3.0.0 or later). Scripts run in the manager's BusyBox ash "standalone mode". Building a module needs only a zip tool; no compiler.
metadata:
  apatch-version: "11224"
  kernelsu-version: "v3.3.1"
---

# Magisk-style module for APatch and KernelSU

This skill builds **Magisk-style systemless modules** for [APatch](https://github.com/bmax121/APatch)
and [KernelSU](https://github.com/tiann/KernelSU): they change `/system` without touching the real
partition, run boot scripts, and install from a zip through the root manager. APatch's module engine
(`apd`) follows KernelSU's (`ksud`), so the two are close; the differences that bite are called out.

Written against **APatch manager 11224** (`apd` and its `installer.sh`) and **KernelSU v3.3.1**
(`ksud`). A module is **not** a KPM: a KPM is kernel-space C (see the `kpm` skill); a module is
files + shell.

## The manager does not mount your `system/` any more

Both managers moved mounting out of their core into a **metamodule** (KernelSU v3.0.0, PR #2929;
APatch PR #1356, included in 11224: "APatch will NOT process module mount"). At boot the manager runs
the active metamodule's `metamount.sh`, and that script decides how (or whether) module `system/` trees
appear over `/system`.

- **No metamodule installed → no module's `system/` is mounted.** Scripts, `system.prop` and
  `sepolicy.rule` still work; file overlays do not. Tell users the module needs a mounting metamodule
  (KernelSU's reference one is `meta-overlayfs`).
- **How files appear depends on the metamodule**: `meta-overlayfs` uses overlayfs (files override,
  directories merge, whiteouts and opaque dirs work); a magic-mount metamodule uses bind mounts with
  its own rules. Do not promise overlayfs semantics unconditionally.
- `skip_mount` still means "do not mount my `system/`"; the metamodule is the one that honors it.
- `meta-overlayfs` **copies** each module's partition dirs (`system/`, `vendor/`, …) into its own ext4
  image (`/data/adb/metamodule/modules.img`) at install. Editing `$MODDIR/system/...` at runtime does
  not change what is mounted.

Details, REPLACE/REMOVE and metamodule-specific traps: `references/systemless.md`,
`references/module.md`.

## The two things that make a module

1. A directory installed at `/data/adb/modules/<id>/` containing at least a **`module.prop`**.
2. Optionally a **`system/`** tree (mounted by the active metamodule), boot **scripts**, and metadata
   files.

Distributed as a **zip** flashed in the manager. Minimum viable module:

```
mymodule.zip
├── module.prop            # required — without it, it is not a module
├── customize.sh           # optional install-time script
├── system/...             # optional, mounted over /system by the metamodule
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

- **`id`** must match `^[a-zA-Z][a-zA-Z0-9._-]+$` (same regex in `apd` and `ksud`). It is the
  directory name and is interpolated into shell commands, so a bad id is rejected at install. Do not
  change it after release. ✓ `a_module`, `a.module`, `module-101` ✗ `1_module`, `-mod`, `a module`.
- **`versionCode`** must be an integer; it is what version comparison uses.
- Use **LF** line endings, not CRLF.
- A zip whose `module.prop` has no `id` is rejected (`module id not found in module.prop!` in `apd`).
- `metamodule=1` makes the module a metamodule. Do **not** set it on an ordinary module.

## Systemless `/system` changes

Under a mounting metamodule (overlayfs-style, such as `meta-overlayfs`):

- Files in your `system/` **override** same-path system files; directories **merge**.
- To **delete** a system file: `REMOVE="..."` in `customize.sh`. Both installers create a whiteout
  (`mknod <path> c 0 0`) for each entry.
- To **replace** (not merge) a directory: `REPLACE="..."`. APatch's installer sets the overlay
  opaque xattr itself. **KernelSU's installer calls `mark_replace` but no longer defines it** (removed
  in v3.0.0); the active metamodule's `metainstall.sh` must define it (`meta-overlayfs` does). Without
  such a metamodule, REPLACE does nothing useful on KernelSU.

`references/systemless.md` covers REMOVE/REPLACE, `system.prop` and `sepolicy.rule`.

## Scripts and when they run

Put `MODDIR=${0%/*}` at the top of every script to find your module dir — never hardcode the path.
All scripts run in the manager's BusyBox `ash` **standalone mode**.

| Script | Stage | Blocking? |
| --- | --- | --- |
| `post-fs-data.sh` | early, before zygote. **APatch:** after the metamodule mounts. **KernelSU:** before it mounts | yes (KernelSU: up to 35 s per stage; APatch: waits, no timeout) |
| `post-mount.sh` | after the metamodule's `metamount.sh` | yes |
| `service.sh` | late_start service — **use this by default** | no (parallel) |
| `boot-completed.sh` | after Android finishes booting | no |
| `uninstall.sh` | when the module is removed | — |
| `action.sh` | when "Action" is tapped in the manager | — |

- In `post-fs-data.sh` never use `setprop` (deadlock) — use `resetprop -n <k> <v>`.
- If a script needs the mounted files, use `post-mount.sh` or later; that works on both managers.
- Detect the manager at runtime: APatch sets **`APATCH=true`** (also `APATCH_VER`,
  `APATCH_VER_CODE`, `AP_MODULE`); KernelSU sets **`KSU=true`** (also `KSU_VER`, `KSU_VER_CODE`,
  `KSU_KERNEL_VER_CODE`, `KSU_MODULE`). `references/scripts.md` has both boot flows.

## Install-time: customize.sh

The installer extracts your zip to `$MODPATH` and, if present, **sources** `customize.sh`. Declare
`SKIPUNZIP=1` to take over the whole install yourself. Available helpers: `ui_print`, `abort`,
`set_perm`, `set_perm_recursive`, and variables `MODPATH`, `TMPDIR`, `ZIPFILE`, `ARCH`, `API`,
`IS64BIT`, `BOOTMODE`, plus manager-specific ones (APatch: `APATCH`, `APATCH_VER_CODE`,
`KERNELPATCH_VERSION`, `SUPERKEY`, …; KernelSU: `KSU`, `KSU_VER_CODE`, …). If a metamodule ships a
`metainstall.sh`, the installer sources it too and it decides when `install_module` runs.
`references/installer.md` lists the APatch variables and the exact install order.

## Differences from Magisk (read before porting)

- **No Zygisk** in either manager's core; Zygisk modules don't work as-is.
- **Paths:** APatch uses `/data/adb/ap/…`, busybox `/data/adb/ap/bin/busybox`; KernelSU uses
  `/data/adb/ksu/…`, busybox `/data/adb/ksu/bin/busybox`.
- **Mounting** is the metamodule's job, not the manager's (see above). Magisk mounts itself.
- **Compatibility shims:** `customize.sh` sees `MAGISK_VER`/`MAGISK_VER_CODE` set to fixed values that
  change between releases (APatch 11224: 30.0 / 30000; KernelSU v3.3.1: 25.2 / 25200) — **read them,
  don't hardcode**.
- **Manager-specific:** WebUI (`webroot/`, both), per-stage Lua scripts (`<id>.lua`, APatch only), and
  **metamodules** (both; KernelSU's design, adopted by APatch). A metamodule with a custom installer
  can **block** installing ordinary modules until reboot. See `references/module.md` and
  `references/webui.md`.

## References

Read on demand.

- `references/module.md` — installed layout, module.prop, markers, metamodules.
- `references/scripts.md` — boot stages, both boot flows, per-stage env, general `.d` scripts.
- `references/installer.md` — zip format, customize.sh variables and functions, install order.
- `references/systemless.md` — mounting under metamodules, REMOVE/REPLACE, system.prop, sepolicy.rule.
- `references/webui.md` — WebUI (`webroot/`), the Action button, Lua stage scripts.
