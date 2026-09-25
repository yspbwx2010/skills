# gki

[简体中文](README.md) | English

Teach your Coding Agent to write out-of-tree kernel modules for **Android GKI** (Generic Kernel Image) and to change the kernel without breaking the **KMI** (Kernel Module Interface): the stock vendor modules on the device bind to the KMI, fail to load when a symbol, CRC or struct layout does not match, and are not proven compatible when they do

Targets **OGKI android15-6.6** (OnePlus's common kernel tree for ACK `android15-6.6`), Linux 6.6.118, KMI generation 8, `gki_defconfig`, arm64. Every count, config value and hook signature is read from the kernel source and a real `gki_defconfig` build, and every config-dependent finding comes with the command that re-checks it on your own tree

## What it does

- **The surprising facts first**: in a local build `CONFIG_MODULE_SIG_PROTECT=y` but the protected-symbol gate is empty, `CONFIG_FUNCTION_TRACER` is off (no ftrace, fprobe or livepatch) while kprobes work, `CONFIG_TRIM_UNUSED_KSYMS` is off, and `M=` modules are unsigned
- **What the KMI is made of**: the `abi_gki_aarch64*` symbol lists, the type layouts in the `.stg` (including "private" types such as `struct rq`), layout-affecting Kconfig, and what CRCs cannot see (inline bodies, constants such as `HZ`, `__GENKSYMS__`, `CONFIG_SLIM_SCHED`)
- **KCFI**: callback prototypes must match exactly, no function-pointer casts, `__nocfi` cannot rescue a mismatched callback, shadow call stack and x18
- **Vendor hooks**: declared, exported, actually called and registrable at runtime are four separate facts; plain vs restricted hooks (the latter cannot be unregistered, have 2 slots per hook, and pin the module forever); a hook catalog by subsystem with the useful signatures
- **Choosing a path**: out-of-tree module, vendor hook, kprobe, defconfig change, source patch, in that order
- **What a self-built kernel must keep**: the must-keep configs and layouts, what may be relaxed, why vendor/OEM data slots are not free, and a pre-change checklist
- **Templates**: two buildable modules under `assets/` (a kprobe with a reboot notifier, two plain vendor hooks), compiled warning-free against a 6.6.118 build

## Install

```bash
npx skills add yspbwx2010/skills --skill gki
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install gki@yspbwx2010-skills
```

or copy `gki/skills/gki/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## What the code it produces needs

- The kernel source tree and the output directory of a full build of it (`.config` and a complete `Module.symvers`; `make Image` alone is not enough)
- The clang the ACK branch pins (clang-r510928 / LLVM 18.0.0 for android15-6.6)
- An arm64 device running a kernel built from that source; a stock OEM kernel usually trims symbols and enforces the symbol gate, so the local-build freedoms do not hold there

## License

[MIT](../LICENSE)
