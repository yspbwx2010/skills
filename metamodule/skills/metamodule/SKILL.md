---
name: metamodule
description: Develop a metamodule — the pluggable module-mounting/installation backend for KernelSU (and APatch). A metamodule is a special root module (module.prop with metamodule=1) that controls HOW regular modules are mounted and installed, via the metamount.sh / metainstall.sh / metauninstall.sh hooks. Use when writing a metamodule, a custom mount backend (overlayfs, magic mount, FUSE), the metamount/metainstall/metauninstall scripts, or debugging why modules aren't mounted / why module installs are blocked. Triggers on "metamodule", "meta module", "metamount.sh", "metainstall.sh", "meta-overlayfs", "KernelSU 挂载", "自定义挂载模块".
license: MIT
compatibility: Metamodules run on Android arm64 devices rooted with KernelSU (with metamodule support) or APatch. Scripts run in the manager's BusyBox ash. Building one needs only a zip tool; no compiler (unless your mount backend is a native binary).
metadata:
  kernelsu-ref: "08a3b08 (metamodule support)"
---

# Metamodule

A metamodule is a **special root module that provides the module system's mounting and installation
backend**. Regular modules ship `system/` files and scripts; a metamodule decides *how* those files
get mounted over `/system` and *how* modules install. KernelSU moved this out of its core so the
mount strategy is pluggable (overlayfs, magic mount, FUSE, or none) and KernelSU itself performs no
mounts — a smaller detection surface. **Without a metamodule installed, KernelSU mounts nothing.**

This is a **KernelSU** concept (the official reference impl is `meta-overlayfs`); **APatch** adopted
the same design, so a metamodule is largely portable between them. This skill is verified against
KernelSU's `ksud` source and the official metamodule guide, with APatch's `apd` differences called
out. It is **not** the guide for ordinary modules (those ship `system/` + scripts and need no
`metamodule=1`) — this is only for building the mount/install backend itself.

## What makes a module a metamodule

One line in `module.prop`:

```txt
id=meta-example
name=My Metamodule
version=1.0
versionCode=1
author=you
description=Custom mount backend
metamodule=1
```

- **`metamodule=1`** (or `metamodule=true`, case-insensitive) is the only thing that distinguishes a
  metamodule from a regular module. Without it, it's treated as a regular module.
- **Name the id `meta-*`** by strong convention (`meta-overlayfs`, `meta-magicmount`, …) so users and
  the manager recognize it and it won't collide with regular modules.
- Everything else is an ordinary module: same `id` regex (`^[a-zA-Z][a-zA-Z0-9._-]+$`), same zip
  install flow, same optional lifecycle scripts (`post-fs-data.sh`, `service.sh`, …).

`scripts/new_metamodule.py <dir> --id meta-example` scaffolds a valid metamodule (module.prop +
the three hook stubs), optionally as a flashable zip.

## Single instance, and the symlink

Only **one** metamodule can be installed at a time; the manager blocks a second. When installed,
KernelSU/APatch creates a stable symlink:

```
/data/adb/metamodule -> /data/adb/modules/<metamodule_id>
```

Use that path to find the active metamodule regardless of its id. Switching metamodules means:
uninstall all regular modules → uninstall the current metamodule → reboot → install the new one →
reinstall modules → reboot.

## The three hooks

All optional; each lives in the metamodule's directory and runs in the manager's BusyBox `ash`.
Start each with `MODDIR="${0%/*}"`.

### metamount.sh — the mount backend

Runs at boot to mount every enabled module systemlessly. This is the core of a metamodule.

- Env: **`MODULE_DIR`** (the modules root, `/data/adb/modules`) plus the standard KSU env
  (`KSU=true`, `KSU_VER`, …). `MODDIR` is the metamodule's own dir.
- Must honor `disable` and `skip_mount` markers on each module.
- 🔴 **Every mount you create MUST use the source/device name `"KSU"`** (e.g.
  `mount -t overlay -o … KSU /target`, or `fsconfig_set_string(fs, "source", "KSU")` for the new
  mount API). KernelSU's kernel-side umount and zygisk umount find KernelSU's mounts by that source;
  get it wrong and mounts leak / can't be unmounted.
- It is **blocking** at boot — an error or a hang here can bootloop the device. Handle errors, don't
  `exit 1` on a single module's failure.

### metainstall.sh — customize regular-module installation

**Sourced** (not executed) by the built-in installer during a *regular* module's install, after the
zip is extracted, like `customize.sh`. Not run when installing the metamodule itself, and skipped
while the metamodule is disabled.

- Inherits the installer's variables (`MODPATH`, `TMPDIR`, `ZIPFILE`, `ARCH`, `API`, `IS64BIT`,
  `KSU`, `KSU_VER`, `KSU_VER_CODE`, …) and functions (`ui_print`, `abort`, `set_perm`,
  `set_perm_recursive`), plus **`install_module`** — call it when you're ready to run the built-in
  install (e.g. after moving files into your own store).
- Use it to relocate module files (e.g. into an ext4 image), validate, or set up directories.

### metauninstall.sh — clean up when a regular module is removed

Runs when a *regular* module is uninstalled, before its directory is deleted.

- Env: **`MODULE_ID`** — the id of the module being removed. Read `$MODULE_ID`, **not `$1`**: `ksud`
  passes the id as the `MODULE_ID` environment variable and passes no positional argument, so
  `MODULE_ID="$1"` (as one version of the official example shows) sets it empty. (APatch's `apd`
  passes it the same way.)
- Use it to remove that module's files from your store, drop symlinks, free resources.

## Boot execution order (verified against ksud)

```
post-fs-data:
  common post-fs-data.d  →  prune / restorecon / sepolicy.rule
  →  metamodule post-fs-data.sh  →  regular modules' post-fs-data.sh
  →  load system.prop
  →  metamount.sh              ← your mount backend runs HERE, after all post-fs-data
  →  post-mount stage: common post-mount.d → metamodule post-mount.sh → regular post-mount.sh
service:         common service.d       → metamodule service.sh       → regular service.sh
boot-completed:  common boot-completed.d → metamodule boot-completed.sh → regular boot-completed.sh
```

The metamodule's own lifecycle scripts always run **before** regular modules' at each stage;
`metamount.sh` runs after every post-fs-data script.

## The block you'll hit: installs refused

If the active metamodule has a `metainstall.sh` **and** is in an unstable state (has an `update`,
`remove` or `disable` marker — i.e. pending changes or disabled), the manager **refuses to install
regular modules** until you reboot to settle it (or re-enable it). This is deliberate: installs must
go through the metamodule's installer, and that isn't safe mid-change. Reboot, then install.

## KernelSU vs APatch

The design and the three hook names are the same; a metamodule is largely portable. Differences:

| | KernelSU | APatch |
| --- | --- | --- |
| Env prefix | `KSU`, `KSU_VER`, `KSU_VER_CODE`, `KSU_MODULE`, … | `APATCH`, `APATCH_VER`, `APATCH_VER_CODE`, `AP_MODULE`, … |
| Mount source tag | must be `"KSU"` | follows KernelSU's mounting; keep `"KSU"` unless the target's docs say otherwise |
| Symlink | `/data/adb/metamodule` | `/data/adb/metamodule` |
| busybox | `/data/adb/ksu/bin/busybox` | `/data/adb/ap/bin/busybox` |

Detect the host at runtime with the `KSU` / `APATCH` env var and branch where needed.

## References

Read on demand.

- `references/hooks.md` — the three hooks in full: signatures, env, the `install_module` call, examples.
- `references/execution.md` — boot order, lifecycle scripts, env vars, install-block state machine.
- `references/reference-impl.md` — how `meta-overlayfs` works (dual-directory + ext4 image), and a
  minimal bind-mount `metamount.sh`.
