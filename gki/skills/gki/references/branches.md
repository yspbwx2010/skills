# Per-branch facts: android14-6.1, android15-6.6, android16-6.12, android17-6.18

Every other file in this skill was measured on **one** tree: OGKI `android15-6.6` (OnePlus's common
kernel for ACK `android15-6.6`, Linux 6.6.118) built with plain Kbuild from `gki_defconfig`. Its numbers
are examples for that tree. This file says, per ACK branch, which of those facts hold, which differ, and
which nobody has checked yet. **When this file and another reference disagree for your branch, this
file wins.** When a fact is marked `verify`, run the command before relying on it.

## Evidence markers

| Marker | Meaning |
|---|---|
| `src` | Read from the ACK source at the tag in the header row (`git checkout tags/<tag>`) |
| `ship` | Read from the `/proc/config.gz` of one Google-built `android17-6.18` kernel shipped on a device |
| `ogki-6.6` | Measured by the original skill on the OGKI 6.6.118 build; not re-measured on ACK |
| `verify` | Not checked for this branch. Needs the tree, a full build of it, or the target device |

An OEM common kernel (OGKI) is **not** ACK: OEMs add options, symbol lists and struct users. Re-check
every row on the tree you actually build, and on the device's running kernel when stock modules matter.

## 1. Identity and toolchain

| Fact | 6.1 | 6.6 | 6.12 | 6.18 | Check |
|---|---|---|---|---|---|
| Tag read | `android14-6.1-2025-06_r17` | `android15-6.6-2025-06_r39` | `android16-6.12-2026-03_r73` | `android17-6.18-2026-06_r66` | — |
| Linux version at that tag (`src`) | 6.1.138 | 6.6.89 | 6.12.69 | 6.18.21 | `head -4 Makefile` |
| `KMI_GENERATION` (`src`) | 11 | 8 | 6 | 5 | `build.config.common`; 6.18: `bazel/constants.scl` |
| Clang (`src`) | r487747c | r510928 | r536225 | r584948c | `grep CLANG_VERSION build.config.constants` |
| LLVM version | 17.0.2 | 18.0.0 | 19.0.1 | `verify` | `clang --version` of that prebuilt |
| Rust prebuilt (`src`) | none | none | 1.82.0.p2 | 1.91.1.p3 | `grep RUSTC_VERSION build.config.constants` |
| Constants file | `build.config.constants` | same | same | `build.config.constants` and `bazel/constants.scl` | — |

## 2. Rust

| Fact | 6.1 | 6.6 | 6.12 | 6.18 |
|---|---|---|---|---|
| `CONFIG_RUST` in `gki_defconfig` (`src`) | absent, **cannot** be enabled | absent, **cannot** be enabled | `=y` | `=y` |
| Why (`src`, `init/Kconfig` `config RUST`) | `depends on !CFI_CLANG`, `!MODVERSIONS`, `!SHADOW_CALL_STACK` (all three are `y`) | `depends on !MODVERSIONS`, `!SHADOW_CALL_STACK`; the top-level `Makefile` also stops with `Enabling Rust and CFI silently changes the KMI.` | `depends on !MODVERSIONS \|\| GENDWARFKSYMS` and `!CFI_CLANG \|\| HAVE_CFI_ICALL_NORMALIZE_INTEGERS_RUSTC`; selects `CFI_ICALL_NORMALIZE_INTEGERS` | same as 6.12, with `CFI` in place of `CFI_CLANG` |
| `CONFIG_RUST_INLINE_HELPERS` (`src`) | — | — | `=y` | `=y` |

Rust modules are therefore a 6.12+ option on ACK `gki_defconfig`. A Rust module still sits on the same
KMI as a C one: no Rust ABI is promised, so build it with the branch's pinned `rustc` and treat a
`rustc` change like a compiler change.

## 3. Symbol versioning, KMI lists and the protected-symbol gate

| Fact | 6.1 | 6.6 | 6.12 | 6.18 | Check |
|---|---|---|---|---|---|
| CRCs come from (`src`) | genksyms | genksyms | **gendwarfksyms** (`CONFIG_GENDWARFKSYMS=y`) | **gendwarfksyms** | `grep GENDWARFKSYMS arch/arm64/configs/gki_defconfig` |
| `__GENKSYMS__` hiding (`src`) | used by `include/linux/android_kabi.h` | same | `android_kabi.h` has **no** `__GENKSYMS__`; it uses gendwarfksyms KABI rules (`.discard.gendwarfksyms.kabi_rules`) | same | `grep -n 'GENKSYMS\|gendwarfksyms' include/linux/android_kabi.h` |
| KMI symbol lists (`src`) | `android/abi_gki_aarch64` + `android/abi_gki_aarch64_*` | same | `gki/aarch64/symbols/*` | `gki/aarch64/symbols/*` | `ls` |
| List files / union of names (`src`, line parse) | 34 / 8466 | 32 / 9000 | 41 / 10264 | 24 / 9422 | command in [architecture.md](architecture.md) section 4.3, with the branch's paths |
| ABI description (`src`) | `android/abi_gki_aarch64.stg` | same | `gki/aarch64/abi.stg` | `gki/aarch64/abi.stg` | — |
| `struct rq`, `struct cfs_rq` described in the `.stg` (`src`) | yes | yes | yes | yes | `grep -c '^  name: "rq"$' <stg>` |
| Protected-exports list in tree (`src`) | `android/abi_gki_protected_exports_aarch64` (354) | same file (506) | not in tree (`BUILD.bazel` derives it from the protected modules list) | not in tree (`BUILD.bazel` uses an unprotected-modules exclude list) | `ls android/*protected* gki/aarch64/*protected* 2>/dev/null` |
| `CONFIG_MODULE_SIG_PROTECT` in `gki_defconfig` (`src`) | `=y` | `=y` | **not set** (code still `#ifdef`s on it) | **not set**; `ship`: `=y` in the shipped config (added by the official build) | `grep MODULE_SIG_PROTECT $KERNEL_OUT/.config` — `verify` for a plain `make gki_defconfig` build on 6.12/6.18 |
| What limits an unsigned module's imports (`src`, `kernel/module/`) | `gki_is_module_unprotected_symbol()` table under `MODULE_SIG_PROTECT` (`gki_module.c`) | same (`ogki-6.6`: table empty on a plain build) | **different mechanism**: only under `CONFIG_TRIM_UNUSED_KSYMS`, an unsigned (`!sig_ok`) module may import only symbols exported by other unsigned modules or allowed by `is_permitted_symbol_import()` (`main.c`, "ANDROID GKI" block) | **different mechanism**: under `CONFIG_MODULE_SIG`, an unsigned module cannot use a symbol flagged protected (`fsa.is_protected`, `Cannot use protected symbol`) | 6.1/6.6: [symbols-and-signing.md](symbols-and-signing.md); 6.12/6.18: read `resolve_symbol()` in `kernel/module/main.c`; whether it bites on a plain build is `verify` |
| `CONFIG_TRIM_UNUSED_KSYMS` | not in `gki_defconfig` (`src`) | same | same | same; `ship`: `=y` | official builds trim from Kleaf: `trim_nonlisted_kmi = True` in `BUILD.bazel` (`src`, 6.6–6.18) |
| `CONFIG_MODULE_SIG_SHA1` explicit (`src`) | no | no | no | `=y` | — |
| Exported-symbol counts | `verify` | `ogki-6.6`: 16923 / 16405 | `verify` | `verify` | `wc -l $KERNEL_OUT/*.symvers` after a full build |

## 4. Vendor hooks

| Fact | 6.1 | 6.6 | 6.12 | 6.18 |
|---|---|---|---|---|
| `ANDROID_RVH_NR_PROBES_MAX` (`src`, `kernel/tracepoint.c`) | 2 | 2 | 2 | 2 |
| Restricted hooks have no unregister (`src`, `include/trace/hooks/vendor_hooks.h`) | yes | yes | yes | yes |
| `rvh_func_add()` returns a **positive** `ENOMEM` (`src`) | yes | yes | yes | yes |
| `DECLARE_HOOK` / `DECLARE_RESTRICTED_HOOK` lines in `include/trace/hooks/*.h` (`src`, line-start grep; not unique names) | 360 / 151 | 534 / 190 (`ogki-6.6`: 552 / 195) | 629 / 204 | 585 / 204 |
| Hook header files (`src`) | 62 | 71 | 74 | 64 |
| `android_rvh_place_entity`'s `*vruntime` (`src`, `kernel/sched/fair.c`) | **read back**: the call sits before the min_vruntime clamp that uses `vruntime`, so a probe can steer placement | observe only (last statement of `place_entity()`) | observe only | observe only |

The two hooks in `assets/vendor-hook/` (`android_vh_cpufreq_resolve_freq`, `android_vh_cpu_idle_enter`)
have the same `TP_PROTO` on all four branches (`src`); the templates were compiled only against the 6.6.118
build (`verify` on the others).

Hook names, signatures and call sites change between branches. Never copy a `TP_PROTO` from another
branch or from [hook-catalog.md](hook-catalog.md) without re-reading `include/trace/hooks/<file>.h` in
your tree, and run all four checks in [vendor-hooks.md](vendor-hooks.md) section 1 on your tree.

## 5. Struct slots and layout-affecting config

| Fact | 6.1 | 6.6 | 6.12 | 6.18 | Check |
|---|---|---|---|---|---|
| `task_struct` vendor slots (`src`, `include/linux/sched.h`) | `android_vendor_data1[64]`, `android_oem_data1[6]` | same | **`android_vendor_data1[6]`**, `android_oem_data1[6]` | **`android_vendor_data1[6]`**, `android_oem_data1[6]` | `grep -n 'ANDROID_VENDOR_DATA_ARRAY\|ANDROID_OEM_DATA_ARRAY' include/linux/sched.h` |
| `CONFIG_SLIM_SCHED` (`src`) | does not exist in ACK | does not exist in ACK (`ogki-6.6`: OnePlus OGKI has it, `=y`) | does not exist in ACK | does not exist in ACK | `grep -c SLIM_SCHED include/linux/sched.h` |
| `struct module` fields gated by config (`src`, `include/linux/module.h`) | `LIVEPATCH`, `KPROBES`, ... | same | same | adds a `CONFIG_DYNAMIC_FTRACE` gate | `grep -n '#ifdef CONFIG_' include/linux/module.h` |
| `CONFIG_FUNCTION_TRACER` | not in `gki_defconfig`; `verify` | `ogki-6.6`: off | not in `gki_defconfig`; `verify` | `ship`: off | `grep FUNCTION_TRACER $KERNEL_OUT/.config` |
| `CONFIG_KPROBES=y` (`src`) | yes | yes | yes | yes | — |
| CFI option (`src`) | `CONFIG_CFI_CLANG=y` | `CONFIG_CFI_CLANG=y` | `CONFIG_CFI_CLANG=y` | **`CONFIG_CFI=y`** | `grep -E 'CONFIG_CFI(_CLANG)?=' gki_defconfig` |
| `__nocfi` = `__no_sanitize__("kcfi")` (`src`) | yes | yes | yes | yes (under `CONFIG_CFI`) | `include/linux/compiler-clang.h`; 6.18: `include/linux/compiler_types.h` |
| `SHADOW_CALL_STACK=y`, `UNWIND_PATCH_PAC_INTO_SCS=y` (`src`) | yes | yes | yes | yes | — |
| `NR_CPUS=32`, `PREEMPT=y`, `MODVERSIONS=y`, `MODULE_UNLOAD=y`, `ANDROID_VENDOR_HOOKS=y`, `PANIC_ON_OOPS=y`, `DEBUG_INFO_BTF=y` (`src`) | yes | yes | yes | yes | — |
| `ARM64_VA_BITS_39=y` explicit (`src`) | no (`verify` the default) | no (`ogki-6.6`: 39) | yes | yes | `grep VA_BITS $KERNEL_OUT/.config` |
| `HZ` | `verify` | `ogki-6.6`: 250 | `verify` | `ship`: 250 | `grep '^CONFIG_HZ=' $KERNEL_OUT/.config` |
| 4K pages, `WERROR=y`, `DYNAMIC_SCS=y` | `verify` | `ogki-6.6`: yes | `verify` | `ship`: yes | `.config` |
| Pahole | `verify` | `ogki-6.6`: 131 | `verify` | `ship`: 131 | `CONFIG_PAHOLE_VERSION` |

## 6. What this means in practice

- **Vendor-data slot code does not port from 6.1/6.6 to 6.12+.** An index that fits in `[64]` can be
  out of bounds in `[6]`. `static_assert` the array size and every offset you rely on, on each branch.
- **`__GENKSYMS__` tricks are a 6.1/6.6 tool.** On 6.12+ CRCs come from DWARF; read
  `include/linux/android_kabi.h` and the gendwarfksyms documentation in your tree before assuming any
  change is CRC-invisible.
- **On 6.12/6.18 a plain `make gki_defconfig` build may not enable `MODULE_SIG_PROTECT`** while the
  shipped kernel does. Test unsigned modules against the kernel the device actually runs.
- **The must-keep list in SKILL.md is per branch.** Take it from the device's running config
  (`/proc/config.gz`) and the tree's `gki_defconfig`, not from the 6.6 values.
