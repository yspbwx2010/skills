# AGENTS.md — apm

## What this skill is for

It teaches coding agents to build **Magisk modules** — standard Magisk-style systemless modules,
as used by [APatch](https://github.com/bmax121/APatch) on Android. An agent with this skill can write a valid
`module.prop`, lay out the module zip, write the install script (`customize.sh`) and the boot
scripts (`post-fs-data.sh`/`post-mount.sh`/`service.sh`/`boot-completed.sh`), do systemless
`/system` changes via overlayfs, add `system.prop`/`sepolicy.rule`/WebUI, and port a
Magisk/KernelSU module across.

APM is **not** KPM. A KPM is kernel-space C (the separate `kpm` skill); an APM is files
plus shell scripts. Only `skills/apm/` is installed: `SKILL.md`, `references/`,
`assets/template/` (a module skeleton) and `scripts/new_module.py`.

It is written against the **APatch manager release** it was verified on — currently 11224.

## How it stays correct

The module layout, `module.prop` rules (the id regex is enforced by `apd`), install order,
`customize.sh` variables/functions, boot-stage ordering and env, the overlayfs REMOVE/REPLACE
mechanism, WebUI and metamodules were all read from APatch's `apd` daemon (`src/module.rs`,
`event.rs`, `metamodule.rs`), `apd/assets/installer.sh`, and the manager UI — not only the docs,
which lag (e.g. the doc's `MAGISK_VER_CODE` is 27000; the installer sets 30000). `tools/check_apm.py`
scaffolds the template and checks the generated `module.prop`/zip against the exact rules `apd`
applies at install; CI (`.github/workflows/apm.yml`) runs it and the Agent Skills spec check.

## Rules

- Verify against an APatch **release** checkout; put a fact in the skill only after reading the
  `apd`/installer line. Prefer source values over the docs where they disagree.
- Nothing under `skills/apm/` may link outside that directory.
- Keep `SKILL.md` under 500 lines; detail goes in `references/`, read on demand.
- Run `tools/check_apm.py`, `tools/validate_skill.py` and `../tools/check_repo.py` before
  committing; all must exit 0.
- When bumping the APatch version: re-read `apd` and `installer.sh` for changed paths, variables
  and the `MAGISK_VER*` shim; update `metadata.apatch-version` in SKILL.md and `plugin.json`.
