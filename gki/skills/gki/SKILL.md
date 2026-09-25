---
name: gki
description: Build out-of-tree modules for and make changes to an Android GKI (Generic Kernel Image) arm64 kernel without breaking the KMI, pinned to the android15-6.6 common kernel (Linux 6.6.118, KMI generation 8, gki_defconfig). Covers what the KMI is made of, symbol lists and trimming, the MODULE_SIG_PROTECT symbol gate, KCFI-safe callbacks, vendor hooks (android_vh_* / android_rvh_*), kprobes, and what a self-built kernel must keep so stock vendor modules still load. Use when writing a GKI .ko, registering a vendor hook, choosing between a module, a hook, a kprobe, a defconfig change or a source patch, changing structs, exports, enums or Kconfig in an ACK tree, or debugging "disagrees about version of symbol", "Unknown symbol", "Protected symbol" or "Oops - CFI". Triggers on "GKI", "KMI", "ACK", "vendor hook", "android_vh", "android_rvh", "abi_gki_aarch64", "Module.symvers", "GKI 模块", "KMI 兼容", "vendor hook 注册", "内核模块签名", "第三方内核".
license: MIT
compatibility: Building a module needs the kernel source tree, the output directory of a full build of it (.config and a complete Module.symvers), and the branch's clang (clang-r510928 / LLVM 18.0.0 for android15-6.6). Facts were verified on an arm64 android15-6.6 gki_defconfig build; re-check config-dependent ones on your own tree.
metadata:
  kernel-version: "6.6.118"
  ack-branch: "android15-6.6"
  kmi-generation: "8"
---

# Android GKI modules and KMI-safe kernel changes

A GKI kernel is one Google-built kernel per ACK branch; device code (SoC drivers, vendor scheduling
policy) lives in loadable modules that reach the kernel only through exported symbols and vendor
hooks. The KMI is that interface: the symbol set in `android/abi_gki_aarch64*`, the layout of every
type those symbols reach, and the configs that change layouts or semantics.

This skill is pinned to **OGKI `android15-6.6`** (OnePlus's common kernel tree for ACK
`android15-6.6`): Linux **6.6.118**, `KMI_GENERATION=8`, `gki_defconfig`, arm64, clang **r510928**.
Config-dependent facts below describe a plain Kbuild build of that `gki_defconfig`; each row says how
to re-check it on your tree. `$KERNEL_SRC` is the source tree, `$KERNEL_OUT` the full build output
(`O=`); paths are relative to one of them.

## Facts that differ from what you would assume

| You would assume | In this build | Check |
|---|---|---|
| `CONFIG_MODULE_SIG_PROTECT=y` limits unsigned modules to KMI symbols | **The gate is empty.** Without `CONFIG_UNUSED_KSYMS_WHITELIST`, `include/config/abi_gki_kmi_symbols` is generated empty, `gki_is_module_unprotected_symbol()` returns true for every name: an unsigned module may resolve any of the 16923 exports | `grep -A1 'gki_unprotected_symbols\[\]' "$KERNEL_OUT/include/generated/gki_module_unprotected.h"`: next line `};` = empty gate |
| Hook any function with ftrace, fprobe or livepatch | `CONFIG_FUNCTION_TRACER` is **off**: no ftrace hooks, no fprobe, no `CONFIG_LIVEPATCH`. Turning it on grows `struct module`, and the loader then refuses every stock module. `CONFIG_KPROBES=y` and `register_kprobe()` is `EXPORT_SYMBOL_GPL`: **kprobes are the general hooking tool** | `grep -E 'FUNCTION_TRACER\|KPROBES=' $KERNEL_OUT/.config` |
| GKI trims exports outside the KMI lists | `CONFIG_TRIM_UNUSED_KSYMS` is **off**; official builds trim from Kleaf (`trim_nonlisted_kmi`), not the defconfig. 16923 exports, 9197 in the KMI lists | `grep TRIM_UNUSED_KSYMS $KERNEL_OUT/.config` |
| `CONFIG_MODULE_SIG_ALL=y` signs my module | Signing happens only in `modules_install`. An `M=` build is **unsigned**; it still loads (`sig_enforce` is fixed to false under PROTECT) and counts as a vendor module | `tail -c 28 x.ko \| strings`: no `~Module signature appended~` |
| The release string must match to load | With `CONFIG_MODVERSIONS=y`, `same_magic()` skips the release; per-symbol **CRCs** decide. A plain build's release is `6.6.118-4k-g<sha>[-dirty]`, never `-android15-8` | `modinfo -F vermagic x.ko` |
| `struct rq` is private to `kernel/sched/sched.h`, so free to change | `struct rq` (3840 bytes) and `struct cfs_rq` are fully described in `android/abi_gki_aarch64.stg`: scheduler hooks reach them | `grep -A2 'name: "rq"$' $KERNEL_SRC/android/abi_gki_aarch64.stg` |
| `android_rvh_*` hooks unregister like tracepoints | **No unregister API**, **2 probes per hook** (third gets `-EBUSY`), and a module that registers one can **never be unloaded** (`rmmod` fails with `-EBUSY`). Errors include a **positive** `ENOMEM`: check `if (ret)` | [vendor-hooks.md](references/vendor-hooks.md) |
| `CONFIG_ANDROID_VENDOR_HOOKS=n` makes `register_trace_*` return `-ENOSYS` | No `register_trace_*` is generated at all: hook modules fail to compile, prebuilt ones fail with `Unknown symbol` | `include/trace/hooks/vendor_hooks.h` |
| `__nocfi` on my callback avoids a CFI panic | It expands to `__no_sanitize__("kcfi")` but only affects calls made **inside** that function. The failing check sits in the kernel's caller; only an exact prototype fixes it | [cfi.md](references/cfi.md) |
| Writing `*vruntime` in `android_rvh_place_entity` steers placement | **Observe only** in 6.6.118: the value is never read back | [hook-catalog.md](references/hook-catalog.md) |
| A vendor/OEM data slot with no user in the source is free | `android_vendor_data*` / `android_oem_data*` are a **shared convention space** filled by stock vendor modules; fork copies them into the child | [extending-safely.md](references/extending-safely.md) |
| Equal CRCs after a config change mean it is safe | `CONFIG_SLIM_SCHED` (`y` here) changes what `task_struct` KABI slots 1-3 mean with **identical** CRCs and size | [kmi-breaking-changes.md](references/kmi-breaking-changes.md) section 4.7 |
| Rust modules are an option | `CONFIG_RUST` cannot be enabled on this `gki_defconfig` (needs `!MODVERSIONS`, `!SHADOW_CALL_STACK`; ACK refuses Rust with CFI) | [toolchains.md](references/toolchains.md) |
| `kallsyms_lookup_name()` is available | Not exported. Calling any address it would give is a KCFI-checked indirect call; use such addresses to read data only | [choosing-a-path.md](references/choosing-a-path.md) |

These freedoms (every export usable, empty gate, unsigned is fine) belong to **a kernel you built from
this tree**. An OEM's shipped kernel almost certainly trims and has a non-empty gate (inferred), and
then unsigned modules are held to KMI symbols. Never promise the freedoms for a stock image.

## Choosing a path

Take the first that works. Details: [choosing-a-path.md](references/choosing-a-path.md).

1. **Out-of-tree module** using existing exports. Kernel untouched, loads and unloads on its own.
   Template: [assets/kprobe-notifier/](assets/kprobe-notifier/).
2. **Vendor hook**, to step into an internal path (CPU selection, reclaim, lock waits, binder, UFS).
   [vendor-hooks.md](references/vendor-hooks.md), [hook-catalog.md](references/hook-catalog.md),
   template [assets/vendor-hook/](assets/vendor-hook/).
3. **kprobe**, when no hook exists but the function is in kallsyms, not inlined, not blacklisted.
   Handlers run in atomic context from a `BRK` exception: costly, keep off hot paths.
4. **defconfig change**, for an option GKI leaves off, after checking it changes no layout or CRC
   (must-keep list below).
5. **Source patch**, last: prefer a new `EXPORT_SYMBOL_GPL`, then a new vendor hook; never change a
   struct under `include/` except through a reserved slot.

## Hard rules

### KMI

- Keep, or every stock module that depends on it breaks
  ([kmi-breaking-changes.md](references/kmi-breaking-changes.md),
  [extending-safely.md](references/extending-safely.md) section 3):
  - the layout of every type in the `.stg` (public and "private", `struct rq` / `struct cfs_rq` included);
  - exported function signatures, exports and their license (`EXPORT_SYMBOL` to `_GPL` breaks non-GPL users);
  - enum values: no middle inserts, removals or renumbering; an append breaks users of an `NR_*` sentinel;
  - `static inline` bodies and macros in `include/` (no tool checks them);
  - layout-affecting Kconfig: `ANDROID_VENDOR_OEM_DATA`, `ANDROID_KABI_RESERVE`, `ANDROID_VENDOR_HOOKS`
    on; lock debugging (`DEBUG_SPINLOCK`, `DEBUG_MUTEXES`, `DEBUG_LOCK_ALLOC`, `PROVE_LOCKING`) off;
    `HZ=250`, `NR_CPUS=32`, 4K pages, `VA_BITS=39`, `SLIM_SCHED=y`; SMP, preemption model,
    `MODULE_UNLOAD`, `MODVERSIONS` (the compared part of vermagic); `CFI_CLANG`, `SHADOW_CALL_STACK`;
    `FUNCTION_TRACER` off and every other option that gates a `struct module` field in
    `include/linux/module.h` as stock (the loader refuses a module whose `.gnu.linkonce.this_module`
    size differs).
- Add struct fields only with `ANDROID_KABI_USE` on an existing reserve, and only in kernel code (a
  source patch). A module may use such a field only on a kernel that carries the patch.
- **Equal CRCs prove nothing** about semantics, inline bodies, `HZ`-style constants, `__GENKSYMS__`-hidden
  changes or vendor-slot use. CRC and symbol diffs are useful checks, not an ABI or certification gate.
- Adding a symbol does not by itself break existing modules. Turning trimming off does not free you from
  the KMI: stock vendor modules still bind to it.
- Judge a config change by symbols, types, config and runtime semantics together: neither "one config
  changed, so every OEM module fails" nor "the CRCs match, so it is fine".

### CFI ([cfi.md](references/cfi.md))

- `CONFIG_CFI_CLANG=y`, not permissive, `CONFIG_PANIC_ON_OOPS=y`: a type-mismatched indirect call panics.
- Copy each callback's prototype exactly from the typedef, struct field or `TP_PROTO`. **Never cast a
  function pointer**, never detour it through `void *` or an integer, never add `-Wno-...` to silence a
  function-pointer diagnostic.
- Never strip the flags Kbuild adds (`-fsanitize=kcfi`, `-ffixed-x18`, pac-ret); never touch `x18` in
  inline assembly (`CONFIG_DYNAMIC_SCS=y`).

### Vendor hooks ([vendor-hooks.md](references/vendor-hooks.md))

- **Declared, exported, actually called, registrable at runtime** are four separate facts. Check all
  four; a declaration or an export count is not a usable hook. An out-parameter only matters if the call
  site reads it back.
- `#include <trace/hooks/<file>.h>` only; **never** `#define CREATE_TRACE_POINTS`. Use a GPL-compatible
  `MODULE_LICENSE` (all 746 `__tracepoint_android_*` are `EXPORT_SYMBOL_GPL`).
- Plain hooks (552): unregister with the same `(probe, data)` pair, then
  `tracepoint_synchronize_unregister()`. Callbacks run with preemption disabled: no sleeping, no
  `GFP_KERNEL`, no mutexes.
- Restricted hooks (195): no unregister, 2 slots shared with every vendor module, never unloadable.
  Pass `data = NULL`, register last in `module_init`, check `if (ret)` and return
  `ret > 0 ? -ret : ret`. Keep them out of reusable templates.
- A restricted callback runs in its call site's context: `android_rvh_select_task_rq_fair` under
  `p->pi_lock` with IRQs off, most other scheduler hooks under the rq lock. No sleeping, no
  `GFP_KERNEL`, no mutexes, `printk_deferred()` only ([hook-catalog.md](references/hook-catalog.md)).
- Hooks passing private types (`struct rq`, `binder_proc`, `scan_control`) only forward-declare them.
  Do not copy private headers or guess offsets; a forward declaration does not license copying a layout.

### Vendor/OEM data slots ([extending-safely.md](references/extending-safely.md))

- `task_struct.android_vendor_data1[64]`, `android_oem_data1[6]` and their siblings are shared vendor/OEM
  space, not free third-party slots. "No in-tree user" never means "free on the device": establish
  ownership on the target or treat the slot as taken. Fork copies the slots into the child.
- This skill ships no slot template on purpose. If you use a slot, `static_assert` every offset you rely on.
- No established ownership: keep per-task state in module-owned storage (an `rhashtable` keyed by the
  `struct task_struct *`), set up in plain hook `android_vh_dup_task_struct` or lazily, and removed in
  plain hook `android_vh_free_task` ([extending-safely.md](references/extending-safely.md) section 2).

### Loading

- Never force-load (`insmod -f`, `--force-vermagic`, `--force-modversion`, `CONFIG_MODULE_FORCE_LOAD`).
  A CRC mismatch means the layouts differ.

## Build

```sh
export PATH=/path/to/clang-r510928/bin:$PATH       # the branch's clang, see build.config.constants
make -C "$KERNEL_SRC" O="$KERNEL_OUT" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
     KCFLAGS=-D__ANDROID_COMMON_KERNEL__ M="$PWD" modules
```

- `$KERNEL_OUT` must be a **full** build: `.config` plus a complete `Module.symvers`. `make Image` alone
  does not produce one.
- Use the clang the ACK branch pins, not a platform or distro clang; treat
  `the compiler differs from the one used to build the kernel` as an error. Branch table:
  [toolchains.md](references/toolchains.md).
- Kbuild adds `-fsanitize=kcfi`, `-ffixed-x18`, pac-ret and `-Werror` (`CONFIG_WERROR=y`) itself.
- The `.ko` is unsigned; its vermagic reads `6.6.118-4k-g<sha> SMP preempt mod_unload modversions aarch64`.
- Templates: copy [assets/kprobe-notifier/](assets/kprobe-notifier/) or
  [assets/vendor-hook/](assets/vendor-hook/), then `make KERNEL_SRC=... KERNEL_OUT=...` (`make ... clean`
  to clean). Both build warning-free against a 6.6.118 `gki_defconfig` build.
- List what a module imports from outside the KMI lists before relying on it (`llvm-nm -u` plus `comm`,
  [choosing-a-path.md](references/choosing-a-path.md) section 1).
- On the device after loading anything or flashing a kernel:
  `dmesg | grep -iE 'disagrees about version|Unknown symbol|Protected symbol|version magic|struct module size|CFI failure'`.

## Pre-change checklist

Condensed from [extending-safely.md](references/extending-safely.md) section 4; stop at the first failure.

0. **Scope.** A file under `include/` or `gki_defconfig` is high risk. For a "private" header, check
   whether the `.stg` describes the type before treating it as internal.
1. **Layout.** Any field added, removed, retyped or moved in a KMI struct? Use a reserved slot or don't.
2. **Symbols.** Any export deleted, renamed, turned `_GPL`, or moved from `obj-y` to `obj-m`?
3. **Enums.** Any value inserted, removed or renumbered; any append behind an `NR_*` sentinel?
4. **Inline and macro semantics.** Any `static inline` body or macro expansion changed? Check by hand.
5. **Kconfig.** Diff against the baseline (`scripts/diffconfig`) and walk the must-keep list, `SLIM_SCHED`
   first.
6. **Measure.** Before and after full builds: diff `Module.symvers` symbols and CRCs, compare `pahole`
   sizes of core structs, compare the vermagic string. A partial substitute for `stgdiff`, not a gate.
7. **Module side.** `static_assert` every layout assumption, no copied private headers, GPL license.
8. **Device.** `dmesg` grep above, `lsmod | wc -l` equal to before, real workloads (camera, games,
   charging). Plain QEMU cannot validate real-SoC power, frame performance or vendor behaviour.

## Common mistakes

| Mistake | Fix |
|---|---|
| `#define CREATE_TRACE_POINTS` before a hook header | Include the header only; the kernel already defines and exports the tracepoints |
| Casting a callback so `register_trace_*()` or a struct field accepts it | Copy `void *data` + `TP_PROTO` (or the typedef) exactly; the cast still panics under KCFI |
| `__nocfi` on a callback to stop `Oops - CFI` | Fix the prototype; the check is in the kernel's caller |
| `module_exit` for a module that registered an `android_rvh_*` hook | There is no unregister; design the module never to unload |
| `if (ret < 0)` after a restricted-hook registration | `if (ret)`: `ENOMEM` comes back positive |
| `return ret;` from `module_init` after a failed restricted-hook registration | `return ret > 0 ? -ret : ret;`: `do_init_module()` treats a positive return as success and keeps the module loaded without its hook |
| Sleeping or `GFP_KERNEL` in a plain-hook callback or kprobe handler | Both run in atomic context |
| Using `android_rvh_place_entity`'s `*vruntime` to steer placement | Observe-only in 6.6.118; pick a hook whose out-parameter is read back |
| Rewriting `*target_freq` in `android_vh_cpufreq_target` | Too late for `->target_index` drivers; use `android_vh_cpufreq_resolve_freq` and respect `policy->max` |
| Copying `kernel/sched/sched.h` to dereference `struct rq` | Prefer hooks with public argument types and exported accessors |
| Storing per-task state in `android_vendor_data1[k]` because no in-tree code uses it | Establish ownership on the device and handle fork copying the slot, or use module-owned storage cleaned up in `android_vh_free_task` |
| Non-GPL `MODULE_LICENSE` in a hook or kprobe module | Hook tracepoints and `register_kprobe()` are GPL-only |
| Building against `make Image` output, or with another clang | Full build output and the branch's clang |
| Reading "exported minus KMI union" as what an official build trims | It is not; it only counts exports outside the lists here |
| Explaining a KMI-union count difference by `vmlinux.symvers` vs `Module.symvers` | The union comes from the list files alone; a different count is a parsing difference |
| "CRCs match, so the change is safe" | CRCs miss inline bodies, constants, `__GENKSYMS__` changes and slot semantics |
| Turning on lock debugging or `FUNCTION_TRACER`, or off `ANDROID_VENDOR_OEM_DATA`, in a self-built kernel | Keep the must-keep configs; they shift structs every vendor module embeds or loads with (`struct module`) |
| Promising "any export, no signature needed" for a stock OEM kernel | True only for a kernel built from this tree without trimming |

## Verified vs inferred

Everything above was read from the 6.6.118 source or measured on a `gki_defconfig` build, except what the
references mark `(inferred)`. Could not confirm: whether a given device runs a kernel built from this
tree; what `vendor_boot` / `vendor_dlkm` contain; which hooks and data slots a device's vendor modules
use; the official `stgdiff` check (not runnable from a plain source tree).

## References

Read on demand; do not load all at once.

- [references/architecture.md](references/architecture.md): fact table, GKI 2.0 split, KMI generation,
  vermagic and CRCs, the `abi_gki_aarch64*` lists and measured counts.
- [references/symbols-and-signing.md](references/symbols-and-signing.md): trimming in modpost,
  `MODULE_SIG_PROTECT`, the empty gate, why `M=` modules are unsigned.
- [references/cfi.md](references/cfi.md): KCFI mechanics, the four callback rules, `__nocfi`, shadow
  call stack.
- [references/choosing-a-path.md](references/choosing-a-path.md): third-party kernel vs vendor, the
  five paths in order, kprobe limits.
- [references/toolchains.md](references/toolchains.md): ACK branch to clang table, the build command,
  flags Kbuild adds, Rust, pahole.
- [references/kmi-breaking-changes.md](references/kmi-breaking-changes.md): the three parts of the KMI,
  the `.stg`, CRC vs `stgdiff`, `__GENKSYMS__`, every KMI-breaking operation, `CONFIG_SLIM_SCHED`.
- [references/extending-safely.md](references/extending-safely.md): reserved slots, vendor/OEM data
  slots, must-keep vs may-relax, the full pre-change checklist.
- [references/vendor-hooks.md](references/vendor-hooks.md): the four checks, plain vs restricted,
  which hooks a module can use, the type trap, registration patterns.
- [references/hook-catalog.md](references/hook-catalog.md): hooks by subsystem, call-site density,
  scheduler, cpufreq, cpuidle, reclaim and binder hook signatures.
- [assets/kprobe-notifier/](assets/kprobe-notifier/): out-of-tree module with a kprobe and a reboot
  notifier, CFI-exact callbacks, full teardown.
- [assets/vendor-hook/](assets/vendor-hook/): registers two plain vendor hooks
  (`android_vh_cpufreq_resolve_freq`, `android_vh_cpu_idle_enter`) and unregisters them cleanly.
