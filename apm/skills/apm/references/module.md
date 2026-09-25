# Module layout and metadata

Verified against APatch 11224 (`apd` daemon, `docs/cn/ap_module.md`).

## Installed directory

A module lives at `/data/adb/modules/<id>/`:

```
/data/adb/modules/<id>/
├── module.prop          # required config (id, name, version, versionCode, author, description)
├── system/              # overlaid onto /system (systemless)
├── skip_mount           # marker: if present, system/ is NOT mounted
├── disable              # marker: module is disabled
├── remove               # marker: module is removed on next boot
├── post-fs-data.sh      # script, post-fs-data stage
├── post-mount.sh        # script, post-mount stage
├── service.sh           # script, late_start service stage
├── boot-completed.sh    # script, after boot
├── uninstall.sh         # script, on removal
├── action.sh            # script, on "Action" in the manager
├── <id>.lua             # optional Lua run per stage / for Action (APatch addition)
├── system.prop          # props applied at boot via resetprop
├── sepolicy.rule        # extra SELinux rules loaded at boot
├── webroot/             # optional WebUI (APatch addition)
└── vendor|product|system_ext   # auto-generated symlinks into system/ — do not hand-create
```

`/data/adb/modules_update/` is the staging dir for A/B-style updates; `apd` promotes it to
`modules/` on boot. Don't write there directly.

## module.prop

```
id=<string>          # ^[a-zA-Z][a-zA-Z0-9._-]+$  — dir name, immutable after release
name=<string>
version=<string>
versionCode=<int>    # integer, used for version comparison
author=<string>
description=<string>
```

- The id regex is enforced by `apd` (`module.rs`) because the id becomes a directory name and is
  interpolated into shell — a traversal-y id is a security reject, not a style nit.
- Single-line values; **LF** newlines.
- No `id` in module.prop ⇒ install fails with `module id not found in module.prop!`.
- `apd` adds runtime fields the manager reads back: `enabled`, `update`, `remove`, `web` (has
  `webroot/`), `action` (has `action.sh` or `<id>.lua`).

## Marker files

| File (in the module dir) | Effect |
| --- | --- |
| `skip_mount` | module's `system/` is not mounted |
| `disable` | module disabled (kept installed) |
| `remove` | module deleted on next boot |

`apd` toggles `disable`/`remove` when you enable/disable/uninstall from the manager; a module can
ship `skip_mount` if it only wants scripts, no overlay.

## Metamodules (APatch-specific)

A module with `metamodule=1` (or `true`) in `module.prop` is a **metamodule**: it owns how ordinary
modules are mounted and installed, via scripts named `metamount.sh`, `metainstall.sh`,
`metauninstall.sh`. Only one is active, symlinked at `/data/adb/metamodule`.

Consequence for ordinary modules: if an active metamodule provides a **custom installer**
(`metainstall.sh`), installing a normal module that needs mounting (has `system/`, no `skip_mount`)
is **blocked** until you reboot to apply the metamodule, or is blocked while the metamodule is
disabled/pending. `apd` prints "Installation Blocked / A metamodule with custom installer is
active". Don't fight it — reboot or re-enable the metamodule as the message says. Most modules are
not metamodules and never touch this.
