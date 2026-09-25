# kpm

[简体中文](README.md) | English

Teach your Coding Agent to write, build and load **KernelPatch Modules (KPM)**: arm64 ELF objects that [KernelPatch](https://github.com/bmax121/KernelPatch) and [APatch](https://github.com/bmax121/APatch) load into the Linux kernel to inline-hook kernel functions, hook syscalls, or call kernel functions by name without kernel source

Targets **KernelPatch 0.13.9**. Every macro, API signature, exported-symbol name and loader rule is read from the KernelPatch source and the APatch daemon, not the upstream docs (which have drifted from the source)

## What it does

- **Anatomy and lifecycle**: metadata macros, the exact signatures of the five callbacks (`KPM_INIT` / `KPM_CTL0` / `KPM_CTL1` / `KPM_EXIT` / `KPM_EVENT`), and the rule that panics the kernel if broken: unhook everything in `exit`
- **The real exported API**: ~113 `KP_EXPORT_SYMBOL` symbols grouped by header with signatures, plus the doc-vs-source traps (e.g. `commit_su` / `task_su` are not actually exported)
- **Hooks**: inline `hook_wrap` chains, function-pointer hooks, the `hook_err_t` codes, chain order and the 16-item limit; the syscall-hook family with `syscall_argn` and return override
- **Build**: the `aarch64-none-elf` toolchain, the `-r` partial-link Makefile, `-fno-common`, the `.lds`, and the loader's ELF checks
- **Loading**: SuperCall `sc_kpm_load` / `control` / `unload`, the `kptools` embed flags and boot events, and APatch's `/data/adb/ap/kpm/` auto-load path
- **Scaffold**: `scripts/new_kpm.py` generates a buildable KPM skeleton in an empty directory

## Install

```bash
npx skills add yspbwx2010/skills --skill kpm
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install kpm@yspbwx2010-skills
```

or copy `kpm/skills/kpm/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## What the code it produces needs

- The `aarch64-none-elf` GCC toolchain (or `clang --target=aarch64-none-elf`) to build a `.kpm`
- A checkout of the matching KernelPatch release for its headers
- An arm64 device patched by KernelPatch / APatch (Linux 3.18-6.6, `CONFIG_KALLSYMS=y`)

## License

[MIT](../LICENSE)
