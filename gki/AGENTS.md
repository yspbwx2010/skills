# AGENTS.md — gki

## What this skill is for

It teaches coding agents to build out-of-tree modules for, and make changes to, an **Android GKI**
(Generic Kernel Image) arm64 kernel without breaking the **KMI** (Kernel Module Interface) that the
device's stock vendor modules depend on. An agent with this skill knows what the KMI is made of
(symbol lists, type layouts in the `.stg`, layout-affecting Kconfig), how symbol trimming and the
`MODULE_SIG_PROTECT` gate behave, how to write KCFI-safe callbacks, how to use vendor hooks
(`android_vh_*` / `android_rvh_*`) and kprobes correctly, which path to take for a change, and what a
self-built kernel must keep so the stock modules still load.

Only `skills/gki/` is installed: `SKILL.md`, the `references/`, and two buildable module templates
under `assets/` (`kprobe-notifier/`, `vendor-hook/`). Everything else here is maintainer tooling.

It is written against **OGKI `android15-6.6`** (OnePlus's common kernel tree for ACK
`android15-6.6`): Linux 6.6.118, `KMI_GENERATION=8`, `gki_defconfig`, arm64, clang-r510928. Never
document another branch or generation from memory: KMI facts are per branch and per config.

## How it stays correct

Every count, config value, code path and hook signature in the skill was read from the kernel source
and from a real `gki_defconfig` build of it (`.config`, `Module.symvers`, generated headers,
`pahole`), not from Android documentation or memory. The research it was condensed from had errors;
eight errata were applied (for example: the KMI-list union does not depend on which symvers file you
compare with; equal CRCs prove nothing about semantics; restricted hooks cannot be unregistered and
have 2 slots; `android_rvh_place_entity` is observe-only; vendor/OEM data slots are shared, not free).
Anything not verified is marked `(inferred)` or listed under "Could not confirm" in its reference.

`tools/check_gki.py` compiles every template under `skills/gki/assets/` against a prepared kernel
build (source tree plus a full build's output) with the Kbuild command the skill documents, and fails
on any error, warning or missing `.ko`. It needs a full kernel build, so it runs **locally only**;
CI (`.github/workflows/gki.yml`) runs `tools/validate_skill.py`.

## Rules

- Verify against a kernel tree **and** a full build of it before adding or changing a fact. State
  config-dependent facts as facts about that build, with the command that re-checks them.
- Nothing under `skills/gki/` may link outside that directory, and nothing there may cite a local
  path, a project-specific tool or a device of the maintainer.
- Keep `SKILL.md` under 500 lines; put detail in `references/`, read on demand.
- Run `tools/validate_skill.py` and `../tools/check_repo.py` before committing; both must exit 0.
  After touching `assets/`, run
  `tools/check_gki.py --ksrc KERNEL_SRC --kout KERNEL_OUT --clang-bin CLANG_BIN`; it must exit 0.
- When retargeting a new ACK branch or KMI generation: re-verify every config-dependent fact, count
  and hook signature against that tree and its build, re-run `tools/check_gki.py`, and bump
  `metadata` in `SKILL.md` and the version in `.claude-plugin/plugin.json`.
