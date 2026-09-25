# Extending the kernel without breaking the KMI

Facts are from the OGKI `android15-6.6` tree (Linux 6.6.118, `gki_defconfig`, arm64). Background on
what breaks the KMI and why is in `kmi-breaking-changes.md`. `$KERNEL_SRC` is the kernel source tree.
`$KERNEL_OUT` is the output directory of a **full** build, holding `.config`, `vmlinux` and a
complete `Module.symvers` (`make Image` alone does not produce a complete one).

## 1. Reserved slots

| Macro (config on) | Expands to | Belongs to |
|---|---|---|
| `ANDROID_KABI_RESERVE(n)` | `u64 android_kabi_reserved##n` | the kernel tree; consumed with `ANDROID_KABI_USE` |
| `ANDROID_VENDOR_DATA(n)`, `ANDROID_VENDOR_DATA_ARRAY(n, s)` | `u64 android_vendor_data##n` / `[s]` | a **shared convention space** for SoC-vendor code |
| `ANDROID_OEM_DATA(n)`, `ANDROID_OEM_DATA_ARRAY(n, s)` | `u64 android_oem_data##n` / `[s]` | a **shared convention space** for OEM code |

A slot in a struct does not change that struct's layout, so it does not break the KMI. Using a slot
is still not automatically safe. The two sections below explain why.

### `ANDROID_KABI_RESERVE` / `ANDROID_KABI_USE` (kernel code)

- Upstream places these before the freeze. After the freeze, `ANDROID_KABI_USE(n, new_field)` swaps
  one of them for a real field. `_ANDROID_KABI_REPLACE` (`include/linux/android_kabi.h`) builds a
  union and uses `_Static_assert` to check that the new field is no larger and no more aligned than
  the `u64` it replaces.
- There are 631 in `include/` in 6.6.118. Already consumed:

| Location | Holds |
|---|---|
| `include/linux/sched.h` (`task_struct` slots 1–3) | `sched_prop` / `scx` / `dmabuf_info`; the meaning depends on `CONFIG_SLIM_SCHED` |
| `include/linux/dma-buf.h` | `atomic64_t nr_task_refs` |
| `include/linux/tty_driver.h` | `int (*ldisc_ok)(…)` |
| `include/crypto/hash.h` | `finup_mb`, `mb_max_msgs` |
| `include/linux/cgroup-defs.h` | `kmi_ext_info`, `rcu` |
| `include/linux/mm_types.h` | `dmabuf_info` |

- `task_struct` reserves 4–8 (`include/linux/sched.h`, bytes 3600–3639) are unconsumed in 6.6.118.
  Check your tree with `grep -n 'ANDROID_KABI_' "$KERNEL_SRC/include/linux/sched.h"`.
- **Who may consume a reserve:** only kernel code, by a source patch that turns
  `ANDROID_KABI_RESERVE(n)` into `ANDROID_KABI_USE(n, field)` in the header. An out-of-tree module
  cannot consume one: it has no header of its own for a kernel struct.
- **Who may then use the field:** a module built against the patched headers, loaded on a kernel that
  carries the patch, may read and write it like any field. Stock modules are unaffected: the union
  keeps the size and every offset (`_Static_assert` in `include/linux/android_kabi.h`), and genksyms
  sees the original `u64` (`__GENKSYMS__`), so no CRC changes.
- **The catch:** for the same reason, nothing stops that module loading on a kernel **without** the
  patch. It then reads and writes an unused reserve and nothing logs it. Tie the module to the patch,
  for example by making it import a symbol only the patched kernel exports, so it fails with
  `Unknown symbol` elsewhere. The kernel and every module must read the slot the same way, and nothing
  catches a disagreement (see the `CONFIG_SLIM_SCHED` trap in `kmi-breaking-changes.md` §4.7).
- Fork copies a consumed reserve into the child like any other field. Reset it in kernel code.

### `ANDROID_VENDOR_DATA` / `ANDROID_OEM_DATA`: shared, not free

> **These arrays are a shared convention space, not free slots for third-party code.** No allocation
> registry exists and nothing checks at runtime who owns which slot. If two modules use the same
> `u64`, each silently corrupts the other's state. The layout does not change, so this is not a KMI
> break, but the device still fails. **Before using a slot, establish who owns it on the target device.**

In `task_struct` (`include/linux/sched.h`):
`ANDROID_VENDOR_DATA_ARRAY(1, 64)` → `u64 android_vendor_data1[64]` at byte 3008, and
`ANDROID_OEM_DATA_ARRAY(1, 6)` → `u64 android_oem_data1[6]` at byte 3520.

In-tree users in 6.6.118 (verified by reading the source):

| Array | In-tree use |
|---|---|
| `task_struct.android_vendor_data1[64]` | none in the tree |
| `task_struct.android_oem_data1[6]` | `[0]` = `struct oplus_task_struct *` (`kernel/locking/locking_main.h`); `[1]` = `struct hmbird_entity *` (`include/linux/sched/hmbird.h`) |
| `rq.android_oem_data1[16]` (`kernel/sched/sched.h`) | `[14]` = HMBIRD ops, `[15]` = HMBIRD rq (`include/linux/sched/hmbird.h`) |

**No user in the tree does not mean the slot is free on a device.** The prebuilt SoC-vendor and OEM
modules in `vendor_dlkm` and `vendor_boot` fill these arrays by private convention. A SoC scheduler
module keeping per-task state in `task_struct.android_vendor_data1` is the typical case (inferred,
not verified on a device). Nothing in the kernel source can tell you what those modules use. Use the
vendor's module sources, or investigate on the device itself. If you cannot establish ownership,
treat the slot as taken.

## 2. The per-task state pattern, and why it is dangerous

This section has no template on purpose. The pattern works only once slot ownership is settled
(§1), and a copy-paste template would skip that step.

The pattern: a module needs per-task state without changing `task_struct`.

1. It borrows one element of `android_vendor_data1[]`, either to store a value or to hold a pointer
   to its own allocation.
2. It reads and writes the element with `READ_ONCE`/`WRITE_ONCE` from a vendor-hook callback.
3. It turns its layout assumptions into build errors, so a KMI drift fails the build instead of the
   device:

```c
static_assert(sizeof(struct task_struct) == 4800);
static_assert(offsetof(struct task_struct, android_vendor_data1) == 3008);
static_assert(offsetof(struct task_struct, android_oem_data1) == 3520);
static_assert(MY_SLOT < ARRAY_SIZE(((struct task_struct *)0)->android_vendor_data1));
```

If one of these fires on a new kernel, the KMI changed. Do not force-load the module; find out what
changed.

What the pattern does **not** protect against:

- **Ownership.** The asserts check layout only. They cannot see another module using the same
  element (§1).
- **Inheritance at fork.** arm64 `arch_dup_task_struct()` copies the whole struct (`*dst = *src`), and
  `kernel/fork.c` does not clear these arrays (verified in 6.6.118). A child starts with its parent's
  value, and tasks that existed before the module loaded contain whatever was there before. Stored
  pointers need a fork and exit story of their own.
- **Hook facts.** A hook being declared, exported, actually called and registrable at runtime are
  four separate facts; check each one. Normal `android_vh_*` callbacks run with preemption disabled:
  no sleeping, no `GFP_KERNEL`, no mutexes. In exit, unregister and then call
  `tracepoint_synchronize_unregister()`. Restricted `android_rvh_*` hooks have no unregister API, so
  a module that registers one can never safely unload. Check registration with `if (ret)` and return
  `ret > 0 ? -ret : ret` from init. The `__tracepoint_android_*` symbols are `EXPORT_SYMBOL_GPL`, so
  the module needs a GPL-compatible `MODULE_LICENSE`. Details are in `vendor-hooks.md`.

### Fallback: module-owned storage

If you cannot establish slot ownership, do not use a slot. Keep the state in the module:

- An `rhashtable` keyed by the `struct task_struct *`. Its bucket locks disable IRQs
  (`rht_lock()` in `include/linux/rhashtable.h`), so it works from any hook context. `rhashtable_init`,
  `rhashtable_insert_slow` and `rhashtable_free_and_destroy` are `EXPORT_SYMBOL_GPL` and in the KMI union.
  Key by pointer, not pid: when the fork hook runs, the child's `pid` still holds the parent's value
  (`alloc_pid()` comes later in `copy_process()`), and pids are reused.
- **Create** entries in plain hook `android_vh_dup_task_struct(tsk, orig)`, or lazily on first use.
  Tasks that existed before the module loaded have no entry, so treat "absent" as the default state.
- **Remove** entries in plain hook `android_vh_free_task(p)`. It fires in `free_task()` just before
  the `task_struct` memory is freed, including on `copy_process()` failure, so a pointer key is never
  reused while its entry exists.

Both hooks are verified in 6.6.118: declared with `DECLARE_HOOK` in `include/trace/hooks/sched.h`,
exported by `kernel/sched/vendor_hooks.c` (`EXPORT_SYMBOL_GPL`, in the KMI union), and called from
`kernel/fork.c`. Both callbacks run with preemption disabled, and `free_task()` can run from an RCU
callback: allocate with `GFP_ATOMIC` (or `GFP_NOWAIT`) and never sleep. Use `rhashtable_lookup()`
inside `rcu_read_lock()` and free removed entries with `kfree_rcu()`: lookups walk bucket chains under
RCU (`include/linux/rhashtable.h`). On unload, unregister both hooks, call
`tracepoint_synchronize_unregister()`, then `rhashtable_free_and_destroy()`. The cost is one hash
lookup per access and per task free.

## 3. Third-party kernel: what to keep, what you may relax

Premise: you build and flash your own kernel, but the vendor partitions stay stock. The prebuilt
`.ko` files in `vendor_dlkm` and `vendor_boot` must still load and behave. The values below are those
of the 6.6.118 `gki_defconfig`. Match the stock kernel your device actually shipped
(`grep CONFIG_X "$KERNEL_OUT/.config"` on your side, and the stock config on the device's side).

### Must keep

| Constraint | Why |
|---|---|
| `CONFIG_ANDROID_VENDOR_OEM_DATA=y` | the vendor/OEM fields vanish; `mutex`, `rwsem` and `task_struct` shrink (`kmi-breaking-changes.md` §4.5a) |
| `CONFIG_ANDROID_KABI_RESERVE=y` | the 631 reserve fields vanish |
| `CONFIG_ANDROID_VENDOR_HOOKS=y` | when off, `include/trace/hooks/vendor_hooks.h` turns every hook into a no-op: call sites compile out and `__tracepoint_android_*` / `register_trace_android_*` no longer exist, so hook-using modules fail with `Unknown symbol` (verified in source) |
| `CONFIG_MODVERSIONS=y`, `CONFIG_SMP`, preemption model, `CONFIG_MODULE_UNLOAD` | these are the compared part of vermagic; change one and the loader refuses modules built against the old string |
| `CONFIG_HZ=250` | caught by no check; jiffies conversions compiled into modules drift (`kmi-breaking-changes.md` §4.5c) |
| `CONFIG_NR_CPUS=32` | `cpumask` size; enters the CRC |
| `CONFIG_ARM64_4K_PAGES`, `CONFIG_ARM64_VA_BITS=39` | `PAGE_SIZE` and address-space assumptions everywhere in mm |
| `CONFIG_SLIM_SCHED=y` | decides what `task_struct` KABI slots 1–3 mean; **invisible to the CRC** (`kmi-breaking-changes.md` §4.7) |
| `DEBUG_SPINLOCK`, `DEBUG_MUTEXES`, `PROVE_LOCKING`, `LOCKDEP` **off** | lock structs are embedded everywhere (`kmi-breaking-changes.md` §4.5b) |
| `CONFIG_CFI_CLANG`, `CONFIG_SHADOW_CALL_STACK` as stock | calling contract (`kmi-breaking-changes.md` §4.5d, `cfi.md`) |
| `CONFIG_FUNCTION_TRACER` **off**, and every option that gates a `struct module` field as stock | the loader rejects any module whose `.gnu.linkonce.this_module` size differs from the kernel's `sizeof(struct module)` (`kmi-breaking-changes.md` §4.5e) |
| Layout of every type the `.stg` describes | including private ones such as `struct rq` (`kmi-breaking-changes.md` §1, §4.1) |
| Semantics of every `static inline` and macro in `include/` | no tool checks this (`kmi-breaking-changes.md` §4.6) |
| Every export a stock `.ko` uses, with the same license | `kmi-breaking-changes.md` §4.3 |

### May relax (your own kernel only)

- **(a) Symbol trimming.** A plain `make gki_defconfig` build leaves `CONFIG_TRIM_UNUSED_KSYMS` off,
  so your kernel exports more than the 9197 KMI symbols, and your own modules may use any export.
  Three caveats:
  - The size of the surplus is not what the official build trims.
  - A module that uses a non-KMI export will not load on a stock (trimmed) kernel.
  - Turning trimming off does **not** free your kernel from the KMI. The stock vendor modules still
    depend on it.
- **(b) The unprotected-symbol gate is open in a local build** (verified in 6.6.118 source).
  - Without `CONFIG_UNUSED_KSYMS_WHITELIST`, which exists only with trimming,
    `kernel/module/Makefile` writes an empty `include/config/abi_gki_kmi_symbols`.
    `NR_UNPROTECTED_SYMBOLS` is then 0.
  - With that, `gki_is_module_unprotected_symbol()` (`kernel/module/gki_module.c`) returns `true` for
    everything, and `gki_is_module_protected_export()` returns `false`.
  - So unsigned modules may use, and export, any symbol. Details are in `symbols-and-signing.md`.
- **(c) Signatures are not enforced.** Under `CONFIG_MODULE_SIG_PROTECT`, `sig_enforce` is fixed to
  `false` (`kernel/module/signing.c`). Unsigned modules load, and no `TAINT_UNSIGNED_MODULE` is set.
- **(d) Additions.** New exports, new structs and new enum values appended at the end do not affect
  modules that are already built. An appended enum value still breaks them if a `NR_*` sentinel sizes
  an array or bounds a loop that those modules compiled in. If other people will build modules
  against your kernel, keep your own symbol list.
- **(e) Types private to your own code.** A type is free only if it is absent from the `.stg` and no
  prebuilt module can see it. `kernel/sched/sched.h` is not under `include/`, yet `struct rq` and
  `struct cfs_rq` are in the `.stg`, and SoC-vendor modules may be built against private headers
  (inferred). In-tree HMBIRD also uses `rq.android_oem_data1[14..15]`.

**Rule of thumb:** you can change something only if **no binary on the device that you did not
compile depends on it**. Stock modules depend on:

- public and `.stg`-described layouts;
- inline and macro semantics;
- exports;
- the compared part of vermagic;
- compile-time constants;
- the vendor/OEM slot conventions.

Only your own code depends on the symbol lists, the trim and signing policy, and types that no
prebuilt module can see.

## 4. Pre-change checklist

Work through the steps in order. Stop at the first one that fails.

0. **Scope.** Is the file under `include/`? High risk: do every step. Is it `gki_defconfig`? High
   risk. Is it a private header? Check whether the `.stg` describes the type before you treat it as
   internal:
   ```sh
   grep -A2 'name: "rq"$' "$KERNEL_SRC/android/abi_gki_aarch64.stg" | grep -A1 'definition {'
   # prints "bytesize: N" if the struct is in the KMI
   ```
1. **Layout.** Did you add, remove, retype or move a field of a struct that is in the KMI? To add
   one, use `ANDROID_KABI_USE(n, …)` on an existing reserve. Does a struct used only by your module
   need to be in `include/` at all?
2. **Symbols.** Did you delete or rename an `EXPORT_SYMBOL*`, change one to `_GPL`, or turn `obj-y`
   into `obj-m`? Check whether the symbol is in the KMI:
   ```sh
   grep -n "^  <sym>$" "$KERNEL_SRC"/android/abi_gki_aarch64*            # in any list?
   grep -n "name: \"<sym>\"" "$KERNEL_SRC/android/abi_gki_aarch64.stg"   # in the frozen ABI?
   ```
3. **Enums.** Did you change an enum in `include/`? A pure end-append can be wrapped in
   `#ifndef __GENKSYMS__` (see `drivers/android/binder_internal.h`); this keeps the CRC but does not
   make the change harmless. Is a `NR_*` sentinel used as an array length?
4. **Inline functions and macros.** Did you change the body of a `static inline` or the expansion of
   a macro that modules use? No automatic check finds this. Confirm by hand that old modules stay
   correct, or accept the incompatibility.
5. **Kconfig.** Check every row of the must-keep table above, `CONFIG_SLIM_SCHED` in particular:
   ```sh
   git -C "$KERNEL_SRC" diff -- arch/arm64/configs/gki_defconfig
   "$KERNEL_SRC/scripts/diffconfig" baseline.config "$KERNEL_OUT/.config"
   ```
6. **Measured comparison** (a partial substitute for `stgdiff`). Save the `*.before` files from the
   unmodified tree's full build first:
   ```sh
   cd "$KERNEL_OUT"
   for s in task_struct mutex rw_semaphore sock sk_buff cpufreq_policy; do
       echo "=== $s ==="; pahole -C "$s" vmlinux | tail -8        # needs debug info in vmlinux
   done
   grep -A4 'name: "task_struct"$' "$KERNEL_SRC/android/abi_gki_aarch64.stg"   # expect bytesize: 4800
   # .stg offsets are in bits; pahole prints bytes
   awk -F'\t' '{print $2}'     Module.symvers | sort > syms.after && diff syms.before syms.after
   awk -F'\t' '{print $2, $1}' Module.symvers | sort > crc.after  && diff crc.before  crc.after
   strings vmlinux | grep -m1 'SMP preempt mod_unload modversions'
   ```
   The CRC diff is the most valuable step: it shows every change genksyms can see. A changed CRC on
   a symbol a stock module uses is a load failure. An unchanged CRC proves nothing about semantics or
   slot ownership. This step covers layouts and CRCs only, not inline semantics or macro values. It
   is not equivalent to `stgdiff`, and it is not a certification gate.
7. **Module-side defences.** Add a `static_assert` for every layout assumption (§2). Do not copy
   private headers such as `kernel/sched/sched.h` into a module. Use a GPL-compatible
   `MODULE_LICENSE`.
8. **Device test.** After flashing:
   - Run `dmesg | grep -iE 'disagrees about version|Unknown symbol|Protected symbol|version magic|struct module size|CFI failure'`.
   - Compare `lsmod | wc -l` with the count before flashing; every stock module should still load.
   - Run real workloads (camera, games, charging), not just a boot. `HZ`-style drift and slot
     collisions log nothing. Plain QEMU cannot validate real-SoC power, frame performance or vendor
     behaviour.

## 5. Verified, inferred, open

**Verified in 6.6.118 by source, file statistics or build output:**

- the 9197-symbol union and its match with the `.stg`;
- `.stg` offsets are in bits;
- `task_struct` 4800 bytes, `mutex` 48, `rw_semaphore` 64, `struct rq` 3840, all matching the `.stg`;
- `SLIM_SCHED` changes the meaning of the KABI slots without changing the CRC or the size;
- the empty unprotected-symbol list, `sig_enforce` false, and vermagic skipping `UTS_RELEASE`;
- the no-op hooks when `CONFIG_ANDROID_VENDOR_HOOKS` is off;
- fork copying the vendor/OEM slots;
- `task_struct` KABI reserves 4–8 unconsumed; `ANDROID_KABI_USE` keeping size, offsets and CRC;
- `android_vh_dup_task_struct` / `android_vh_free_task` declared, exported and called from `kernel/fork.c`;
- the loader's `struct module` size check, and `FUNCTION_TRACER` → `FTRACE_MCOUNT_RECORD` adding
  `struct module` fields (the resulting size is computed, not built).

**Inferred, not tested:**

- the module-owned-storage fallback in §2 (built from verified parts, but not compiled or run);
- the sizes with `ANDROID_VENDOR_OEM_DATA` off;
- that a reorder can keep the CRC unchanged;
- the `HZ` drift;
- a panic on a CFI mismatch;
- the `stgdiff` command line and exit codes;
- how complete the step 6 substitute is.

**Could not confirm:**

1. Whether the `.stg` fully reflects every OEM change in the tree. Only `task_struct` and `struct rq`
   were compared. If you run `stgdiff` locally, some of its diffs may be pre-existing rather than
   yours.
2. Whether the stock device kernel was built with Kleaf trimming. If it was, relaxations (a) and (b)
   do not hold on the stock image. Check the device's `/proc/kallsyms` or an extracted `vmlinux`.
3. Whether `CONFIG_SLIM_SCHED` comes from the OEM or from upstream ACK. It is probably OEM, judging
   by the HMBIRD copyright header, but it was not diffed against ACK.
4. Which vendor/OEM slots the stock modules on a given device occupy. Only the device and the vendor
   sources can answer this.
5. Whether `CONFIG_KASAN_HW_TAGS=y` touches any `include/` layout. It is expected not to, because it
   is MTE-based and adds no redzones, but this was not checked.
6. The real effect of `android/abi_gki_protected_exports_aarch64`. The generated
   `gki_module_protected_exports.h` was not inspected. Note that the protected-export check tests
   `NR_UNPROTECTED_SYMBOLS`, not the protected-exports count.
