# AGENTS.md — kpm

## What this skill is for

It teaches coding agents to write, build and load **KernelPatch Modules (KPM)** — arm64 ELF
objects that [KernelPatch](https://github.com/bmax121/KernelPatch) (and [APatch](https://github.com/bmax121/APatch),
which is built on it) load and run inside the Linux kernel. A KPM inline-hooks kernel functions,
hooks syscalls, or calls arbitrary kernel functions by name, without the kernel's source. An agent
with this skill can author the `KPM_INIT`/`KPM_CTL0`/`KPM_EXIT` callbacks, use the hook and syscall
APIs correctly, set up the `aarch64-none-elf` build, and load a `.kpm` via SuperCall or APatch.

Only `skills/kpm/` is installed: `SKILL.md`, the `references/`, the `assets/template/`
(a buildable KPM skeleton), and `scripts/new_kpm.py`. Everything else here is maintainer tooling.

It is written against the **KernelPatch release** it was verified on — currently 0.13.9. Never
document `main`: a KPM must compile against the headers users actually have.

## How it stays correct

Every API signature, macro, exported-symbol name, error code and loader behaviour in the skill was
read out of the KernelPatch source (`kernel/include/`, `kernel/patch/`, the demo modules under
`kpms/`) and out of APatch's `apd`, not from the upstream docs — the docs already drifted (e.g.
they list `commit_su`/`task_su` as exported KPM symbols; they are not, and a KPM calling them fails
to load). `tools/check_kpm.py` builds the template with clang for arm64 and asserts the resulting
ELF is a relocatable object carrying the required `.kpm.*` sections; CI (`.github/workflows/kpm.yml`)
runs it.

## Rules

- Verify against a KernelPatch **release tag** checkout; put facts in the skill only after reading
  the source line. Prefer the extracted export list in `references/api.md` over the upstream prose.
- Nothing under `skills/kpm/` may link outside that directory.
- Keep `SKILL.md` under 500 lines; put detail in `references/`, read on demand.
- Run `tools/check_kpm.py` and `../tools/check_repo.py` before committing; both must exit 0.
- When bumping the KernelPatch version: re-read every changed header, update the export list, the
  signatures, `metadata.kernelpatch-version` in SKILL.md, and `plugin.json`'s version.
