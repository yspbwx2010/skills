# AGENTS.md — metamodule

## What this skill is for

It teaches coding agents to build a **metamodule** — the pluggable module mount/install backend for
[KernelSU](https://github.com/tiann/KernelSU) (and [APatch](https://github.com/bmax121/APatch),
which adopted the same design). A metamodule is a root module whose `module.prop` has
`metamodule=1`; it controls *how* regular modules are mounted (`metamount.sh`) and installed
(`metainstall.sh` / `metauninstall.sh`). An agent with this skill can write those hooks correctly,
respect the boot order, tag mounts with source `"KSU"`, and diagnose why modules aren't mounted or
why installs are blocked.

This is **not** the guide for ordinary modules (a systemless `system/` module) — that is a different
skill (`apm` covers the APatch flavor). Only `skills/metamodule/` is installed: `SKILL.md`, the
`references/`, `assets/template/` (a metamodule skeleton with the three hooks), and
`scripts/new_metamodule.py`.

## How it stays correct

The metamodule contract — `is_metamodule` detection, the `/data/adb/metamodule` symlink, the three
hooks and their env (`MODULE_DIR`, the sourced `metainstall.sh` with `install_module`, the
`MODULE_ID` **env var** for `metauninstall.sh`), the boot execution order, and the
install-block state machine — was read from KernelSU's `ksud` source (`src/metamodule.rs`,
`init_event.rs`, `module.rs`) and the official metamodule guide, cross-checked against APatch's
`apd`. A documented doc-vs-source trap: the official `metauninstall.sh` example reads `$1`, but the
id arrives only as `$MODULE_ID`. `tools/check_metamodule.py` scaffolds the template and asserts
`metamodule=1`, a valid id, the three hooks, `source=KSU` in the mount, and that `metauninstall.sh`
does not read `$1`; CI (`.github/workflows/metamodule.yml`) runs it and the Agent Skills spec check.

## Rules

- Verify against the KernelSU source (and APatch `apd`); put a fact in the skill only after reading
  the code. Prefer source over the docs where they disagree.
- Nothing under `skills/metamodule/` may link outside that directory.
- Keep `SKILL.md` under 500 lines; detail goes in `references/`, read on demand.
- Run `tools/check_metamodule.py`, `tools/validate_skill.py` and `../tools/check_repo.py` before
  committing; all must exit 0.
