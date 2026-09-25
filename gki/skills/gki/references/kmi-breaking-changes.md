# KMI: what it is made of and what breaks it

Facts below come from the OGKI `android15-6.6` tree (Linux 6.6.118, `KMI_GENERATION=8`,
`gki_defconfig`, arm64) and a plain `make gki_defconfig` build of it. Re-check them on your own tree
with the command in the last column; config-dependent facts change with the build.

| Item | Value in 6.6.118 | Check with |
|---|---|---|
| Branch / KMI generation | `android15-6.6` / `8` | `build.config.common` |
| ABI freeze point | commit `666cbbfe5c567ca79da30dccad8b5257ca88f02c` | line 2 of `android/abi_gki_aarch64.stg.allowed_breaks` |
| KMI symbols | **9197** (8101 FUNCTION + 1096 OBJECT) | union of the text lists = `elf_symbol` count in `.stg` (commands in §1) |
| `CONFIG_MODVERSIONS` | `y` | `grep CONFIG_MODVERSIONS "$KERNEL_OUT/.config"` |
| `CONFIG_TRIM_UNUSED_KSYMS` | not set (plain Kbuild build) | same |
| `CONFIG_MODULE_SIG_PROTECT` | `y` | same |
| `CONFIG_ANDROID_KABI_RESERVE` / `ANDROID_VENDOR_OEM_DATA` / `ANDROID_VENDOR_HOOKS` | `y` / `y` / `y` | same |
| `sizeof(struct task_struct)` | **4800** (build) = `bytesize: 4800` (`.stg`) | `pahole -C task_struct "$KERNEL_OUT/vmlinux"` |
| Module vermagic | `6.6.118-4k-g<sha> SMP preempt mod_unload modversions aarch64` | `modinfo -F vermagic x.ko` |

## 1. The KMI has three parts

1. **An exported-symbol set** — not every `EXPORT_SYMBOL`, only the names in the
   `android/abi_gki_aarch64*` lists. In 6.6.118: `abi_gki_aarch64` (main list, 3 symbols:
   `module_layout`, `__put_task_struct`, `utf8_data_table`), 31 partner lists
   (`_oplus` 602, `_qcom` 2478, `_pixel` 3357 unique symbols, …) and `abi_gki_aarch64_type_visibility`.
   Sizes in this skill count unique symbols, not `wc -l` lines (see `architecture.md` §4.1).
   Format: first line `[abi_symbol_list]`, then one indented symbol per line, `#` comments.
   The official Kleaf build (`BUILD.bazel`) sets `kmi_symbol_list_strict_mode = True` and
   `trim_nonlisted_kmi = True`, so exports that are in no list are trimmed.
2. **The layouts of every type those symbols reach**, recursively. `__put_task_struct(struct
   task_struct *)` puts the whole `task_struct` — every field offset, every field's own type — into
   the KMI. Private types are not exempt: `struct rq` (3840 bytes) and `struct cfs_rq` from
   `kernel/sched/sched.h` are fully described in the 6.6.118 `.stg`, because scheduler vendor hooks
   take pointers to them.
3. **Some kernel configs** that change layouts or semantics without touching any name or signature
   (§4.5, §4.7).

The KMI symbol count comes from the text lists alone:

```sh
cd "$KERNEL_SRC"
cat android/abi_gki_aarch64 android/abi_gki_aarch64_* \
  | grep -vE '^\[|^\s*#|^\s*$' | tr -d ' ' | sort -u | wc -l     # 9197
grep -c '^elf_symbol {' android/abi_gki_aarch64.stg              # 9197
```

This union does not depend on whether you compare it with `vmlinux.symvers` or `Module.symvers`,
so do not explain a count difference that way. A plain build with trimming off exports more:
16923 lines in 6.6.118's `Module.symvers`, 518 of them from in-tree modules. That surplus is **not**
the number of symbols the official build trims, and it says nothing about what a stock device
kernel exports.

## 2. `android/abi_gki_aarch64.stg`

**Format.** STG (Symbol-Type-Graph): protobuf text, an ID-indexed type graph. One root
`interface` node lists every symbol id. In 6.6.118 it has 9197 `elf_symbol`, 4432 `struct_union`,
30208 `member`, 7759 `function`, 526 `enumeration` nodes (plus pointers, typedefs, arrays, …).

```
# condensed; the file puts one field per line
elf_symbol { id: 0x698a526c  name: "ANDROID_GKI_memcg_stat_item"  is_defined: true
             symbol_type: OBJECT  crc: 0x7a01e9f7  type_id: 0xc9099682 }
struct_union { id: 0x5e2641cb  kind: STRUCT  name: "task_struct"
               definition { bytesize: 4800  member_id: …  (declaration order) } }
member { id: 0xa175f0a0  name: "__state"  type_id: 0x4585663f  offset: 384 }   # bits, not bytes
enumeration { definition { underlying_type_id: …
    enumerator { name: "STATUSTYPE_INFO" }                 # value 0 omitted
    enumerator { name: "STATUSTYPE_TABLE" value: 1 } } }
```

`member.offset` is in **bits** and is omitted when 0. Every field offset and every enumerator value
is written down, so both are part of the KMI (verified by reading the file).

**Coverage.** The `.stg` covers exactly the union of all symbol lists. A symbol in *any* partner
list, plus every type it reaches, is monitored. 746 of the 9197 are `__tracepoint_android_*`.

**`task_struct` still matches the frozen KMI** (verified, `pahole` against `.stg`):

| Field | `.stg` | Build |
|---|---|---|
| `sizeof(task_struct)` | 4800 bytes | 4800 |
| `__state` | 384 bit | 48 bytes |
| `android_vendor_data1` | 24064 bit | 3008 bytes |
| `android_oem_data1` | 28160 bit | 3520 bytes |

The tree's own `task_struct` changes went into KABI reserve slots (§4.7), so no offset moved.

**`android/abi_gki_aarch64.stg.allowed_breaks`** is the list of approved ABI breaks. Every entry is a
real KMI break, which makes it the best catalogue of what not to do:

```
type 'struct fsverity_info' changed
  byte size changed from 272 to 264
  member 'spinlock_t hash_page_init_lock' was removed
type 'enum binder_work_type' changed
  enumerator 'BINDER_WORK_FROZEN_BINDER' (10) was added
11 variable symbol(s) removed
  'struct tracepoint __tracepoint_android_rvh_ogki_hiview_hievent_create' …
```

The last entry shows that **deleting a vendor hook is an ABI break** too, and it needs approval.

**`android/abi_gki_aarch64_type_visibility`** lists 4 symbols: `ANDROID_GKI_struct_dwc3`,
`ANDROID_GKI_struct_kernel_all_info`, `ANDROID_GKI_node_stat_item`, `ANDROID_GKI_memcg_stat_item`.
They are dummy exported `const` variables (`drivers/usb/dwc3/core.c`, `drivers/android/debug_kinfo.c`,
`mm/memcontrol.c`) that exist only to pull their types into the KMI. So `enum node_stat_item`,
`enum memcg_stat_item`, `struct dwc3` and `struct kernel_all_info` are locked even though no exported
function uses them. Inserting a value into the middle of `enum node_stat_item` is a break.

## 3. Two different checks: load-time CRC and release-time `stgdiff`

### CRC (`scripts/genksyms` + `CONFIG_MODVERSIONS`)

- Every exported symbol gets a CRC computed over the **textual expansion** of its type, recursively.
  A module records the CRCs it was built against. The loader compares them
  (`kernel/module/version.c`) and refuses a mismatch ("disagrees about version of symbol").
- `module_layout` is an empty exported function whose signature pulls in `struct module`,
  `modversion_info`, `kernel_param`, `kernel_symbol` and `tracepoint`. `check_modstruct_version()`
  checks it for every module, which is why it sits in the main list. Before that, the loader already
  compares the size of the module's `struct module` copy with the kernel's (§4.5e).
- **Caught:** adding, removing or retyping a field; changing a function signature.
- **Not caught:**
  - reordering fields when the expanded text stays identical, for example macro-generated fields or
    a moved `#ifdef` block. This is inferred from how genksyms works and not reproduced, so treat
    every reorder as a break;
  - anything hidden behind `__GENKSYMS__` (below);
  - enum **values** that were constant-folded into inline code (enumerator names enter the CRC,
    folded values do not);
  - inline-function bodies;
  - macro and config constants such as `HZ`.

**Equal CRCs do not prove compatibility.** They say nothing about semantics, and nothing about who
uses which vendor slot. A changed CRC on a symbol a module uses is a guaranteed load failure. An
unchanged CRC only shows that genksyms saw the same text. Adding a symbol does not by itself break
existing modules. CRC and symbol-set diffs are useful checks, but they are **not** a full ABI or
certification gate.

### `stgdiff` (release time)

- `stgdiff` comes from the STG project; the older flow used `abidiff` (libabigail). Kleaf's
  `kernel_abi` rule drives it: `BUILD.bazel` loads it from `@kleaf//build/kernel/kleaf:kernel.bzl`.
  In 6.6.118, neither tool nor `@kleaf` is in the kernel tree (a grep finds only unrelated names). From
  a plain source checkout you cannot run the official ABI check. Use the checklist in
  `extending-safely.md` step 6 as a partial substitute.
- Its report vocabulary, taken from `allowed_breaks`, is: `byte size changed`,
  `member '…' was added|removed`, `member changed from '…' to '…'`, `offset changed by N`,
  `enumerator '…' was added`, `N function symbol(s) removed`, `N variable symbol(s) removed`.
  (not verified by running it: the command line and exit codes are unknown here)

### `__GENKSYMS__`: changes hidden from the CRC

genksyms defines `__GENKSYMS__` while preprocessing. The kernel uses it to make a change invisible to
the CRC. `include/linux/android_kabi.h`:

```c
#ifdef __GENKSYMS__
#define _ANDROID_KABI_REPLACE(_orig, _new)  _orig
#else
#define _ANDROID_KABI_REPLACE(_orig, _new)                      \
        union { _new; struct { _orig; };                        \
                __ANDROID_KABI_CHECK_SIZE_ALIGN(_orig, _new); }
#endif
```

So `ANDROID_KABI_USE(n, field)` produces the same CRC as the untouched reserve. In 6.6.118 there are
20+ direct `__GENKSYMS__` uses under `include/`. Two examples:

- `drivers/android/binder_internal.h` appends two `enum binder_work_type` values inside
  `#ifndef __GENKSYMS__`.
- `include/trace/hooks/wqlockup.h` declares `android_rvh_alloc_and_link_pwqs` as a
  `DECLARE_RESTRICTED_HOOK` for real, but as a plain `DECLARE_HOOK` for genksyms.

These changes pass `insmod`, but they can contradict what a prebuilt module assumes. The worst case in
this tree is in §4.7.

## 4. Operations that break the KMI

### 4.1 Fields of a public struct

A struct is in the `.stg` if any KMI symbol reaches it, directly or indirectly.

| Change | `stgdiff` reports | CRC catches it? |
|---|---|---|
| Add a field (not a reserved slot) | `byte size changed`, `member … was added`, `offset changed by N` on everything after it | yes |
| Remove a field | `byte size changed`, `member … was removed` | yes |
| Change a field's type (even same width) | `member changed from 'A x' to 'B x'` | yes |
| Reorder fields | a run of `offset changed by N` | **not always** |

A prebuilt module has `offsetof(struct foo, b)` compiled in as an immediate. After a reorder that the
CRC misses, `insmod` succeeds and the module reads the wrong field. Extend through reserved slots
instead; see `extending-safely.md`.

### 4.2 An exported function's signature

Changing the number of parameters, a parameter type, the return type or a `const` qualifier is a
break. A `.stg` `function` node records a `return_type_id` and a list of `parameter_id`s, each of
which points into the full type graph. So a function whose declaration is unchanged still changes if
the layout of a type it takes (for example `struct bar *`) changes. Real sample from
`allowed_breaks`: `1 function symbol(s) removed 'int
__traceiter_android_vh_suitable_migration_target_bypass(void*, struct page*, bool*)'`.

### 4.3 Deleting or renaming an exported symbol

- A deleted symbol makes prebuilt modules fail with `Unknown symbol`. `stgdiff` reports
  `N function|variable symbol(s) removed`. Removing a vendor hook removes its `__tracepoint_*` and
  `__traceiter_*` symbols.
- A rename is a delete plus an add. Adding a symbol does not break modules that don't use it.
- Changing `EXPORT_SYMBOL` to `EXPORT_SYMBOL_GPL` keeps the name, but non-GPL modules then fail to
  load. `.stg` entries carry no license flag, so `stgdiff` does not see it (inferred from the
  format). The reverse change is safe.
- Changing built-in code (`obj-y`) to a module (`obj-m`) moves its exports from `vmlinux` into a
  `.ko`. Prebuilt modules were linked against `vmlinux` and have no `depends=` on the new module,
  so nothing makes it load first.

### 4.4 Enum values

`.stg` records each `enumerator { name value }`. These changes break the KMI:

- inserting an enumerator in the middle (every later value shifts);
- removing an enumerator;
- changing an explicit value;
- **appending at the end**. `stgdiff` still reports `enumerator … was added`, so it needs approval,
  though it is usually approvable. It really breaks when a `NR_*` sentinel sizes an array or bounds a
  loop. Example: `NR_VM_NODE_STAT_ITEMS` sizes `struct pglist_data.vm_stat[]`, which is why
  `enum node_stat_item` is locked by `type_visibility`.

The binder example in §3 appends inside `#ifndef __GENKSYMS__`. The CRC stays the same, so old modules
load, but those modules see an `enum binder_work_type` with two fewer values.

### 4.5 Kconfig that changes layout

These changes look like a single switch, which makes them the easiest trap in a self-built kernel.
Do not reason "one config changed, so every vendor module fails", and do not reason "the CRCs still
match, so it is fine" either. Judge each change by symbols, types, config and runtime semantics
together.

**(a) `CONFIG_ANDROID_VENDOR_OEM_DATA` and `CONFIG_ANDROID_KABI_RESERVE`.**
`include/linux/android_vendor.h` defines `ANDROID_VENDOR_DATA(n)` as `u64 android_vendor_data##n`
(`_ARRAY(n, s)` → `[s]`), and the same for `ANDROID_OEM_DATA`. With the option off, the macros
expand to nothing, and every such field disappears: 42 sites in 27 headers under `include/` in
6.6.118. The effect on sizes:

| Struct | On (measured) | Off |
|---|---|---|
| `struct mutex` | 48 bytes, `android_oem_data1[2]` at 32 | 32 bytes (inferred, not built) |
| `struct rw_semaphore` | 64 bytes, `android_vendor_data1` at 40, `android_oem_data1[2]` at 48 | 40 bytes (inferred) |
| `struct task_struct` | 4800 bytes | at least 560 bytes smaller (inferred) |

`mutex` and `rw_semaphore` are embedded in a huge number of structs, so their layouts all shift.
Prebuilt modules that reach those types get CRC rejections, and whatever slips past reads the wrong
offsets. `CONFIG_ANDROID_KABI_RESERVE` is the same kind of switch: turning it off removes the 631
`ANDROID_KABI_RESERVE()` fields under `include/`. The Kconfig help for the option (in
`drivers/android/Kconfig`) says: "If even slightly unsure, say Y". Keep both on.

**(b) Lock debugging.** `raw_spinlock_t` grows under `CONFIG_DEBUG_SPINLOCK` (`magic`, `owner_cpu`,
`owner`) and under `CONFIG_DEBUG_LOCK_ALLOC` (`dep_map`). `struct mutex` grows under
`CONFIG_DEBUG_MUTEXES` and `CONFIG_DEBUG_LOCK_ALLOC`. `CONFIG_PROVE_LOCKING` selects
`DEBUG_LOCK_ALLOC`. `gki_defconfig` leaves all of them off. Turning any of them on shifts lock-bearing
structs across the whole kernel. Treat such a kernel as one that runs only modules built against it.

**(c) `CONFIG_HZ` and other compile-time constants.** `HZ` is `CONFIG_HZ`
(`include/asm-generic/param.h`), which is 250 in `gki_defconfig`. It changes no layout, so neither the
CRC nor `stgdiff` sees it. It is folded into modules as an immediate through `msecs_to_jiffies()`,
`HZ/10` and similar. If you change it (say to 300) without rebuilding the modules, every
jiffies-based timeout in them drifts by 250/300, with no error and no panic (inferred, not
measured). Other constants of this kind:

| Constant | 6.6.118 value | Effect | Checked? |
|---|---|---|---|
| `CONFIG_HZ` | 250 | all jiffies conversions | no |
| `CONFIG_NR_CPUS` | 32 | `struct cpumask` size, which appears in hook signatures such as `android_rvh_find_lowest_rq` | CRC catches it |
| `CONFIG_ARM64_4K_PAGES` (`PAGE_SHIFT` 12) | y | `PAGE_SIZE`, nearly all mm code | no |
| `CONFIG_ARM64_VA_BITS` | 39 | address-space layout, `virt_to_phys` | no |
| `CONFIG_LOCALVERSION` | `"-4k"` | `UTS_RELEASE` inside vermagic (skipped, see below) | — |

**(d) Vermagic, toolchain and hardening.** `include/linux/vermagic.h` builds `VERMAGIC_STRING` as
`UTS_RELEASE`, then SMP, PREEMPT, MODULE_UNLOAD and MODVERSIONS markers, the arch and
`MODULE_RANDSTRUCT`. With modversions, `same_magic()` (`kernel/module/version.c`) **skips the first
field** (`UTS_RELEASE`) and compares the rest (`SMP preempt mod_unload modversions aarch64`). That is
what lets GKI modules load across sublevel updates.

- Changing `CONFIG_SMP`, the preemption model, `CONFIG_MODULE_UNLOAD` or `CONFIG_MODVERSIONS`
  changes the compared part of vermagic. The loader then refuses every module built against the old
  string. This is a fixed load-time check, not a guess.
- `CONFIG_RANDSTRUCT` puts a per-build seed hash into vermagic. It is off in `gki_defconfig`
  (`RANDSTRUCT_NONE`).
- `CONFIG_CFI_CLANG=y` and `CONFIG_SHADOW_CALL_STACK=y` are not in vermagic, but they change the
  calling contract: kCFI type-checks indirect calls, and SCS reserves `x18`. If the kernel and a
  module disagree on CFI, an indirect call between them hits a CFI failure (inferred from generic CFI
  semantics). `gki_defconfig` uses `CONFIG_LTO_NONE=y`, the non-LTO kCFI variant. See `cfi.md` and
  `toolchains.md`.

**(e) `struct module`, and `CONFIG_FUNCTION_TRACER`.** Every module carries its own `struct module`
in `.gnu.linkonce.this_module`. `kernel/module/main.c` refuses the module with `-ENOEXEC` ("section
size must match the kernel's built struct module size at run time") when that section's size differs
from the kernel's `sizeof(struct module)`. `struct module` (`include/linux/module.h`) has config-gated
fields, so each of those options is a whole-KMI switch:

- `CONFIG_FUNCTION_TRACER=y` enables `DYNAMIC_FTRACE` (`default y`, and arm64 has
  `HAVE_DYNAMIC_FTRACE`), which enables `FTRACE_MCOUNT_RECORD` (`def_bool y`, `kernel/trace/Kconfig`).
  That adds `num_ftrace_callsites` and `ftrace_callsites` to `struct module`. This build's
  `struct module` is 1536 bytes, 64-byte aligned, with no tail padding (`pahole`), so the two fields
  make it 1600 bytes (computed from the layout, not built): **every stock module is refused**. The
  `module_layout` CRC changes too (inferred: genksyms expands the struct).
- `FUNCTION_GRAPH_TRACER` (`default y` once `FUNCTION_TRACER` is on) also adds fields to `task_struct`
  (`include/linux/sched.h`), moving every field after them.
- Keep every option that gates a `struct module` field as stock. In this build: `KPROBES`,
  `TRACEPOINTS`, `TRACING`, `EVENT_TRACING`, `BPF_EVENTS`, `JUMP_LABEL`, `DYNAMIC_DEBUG_CORE`,
  `DEBUG_INFO_BTF_MODULES`, `STACKTRACE_BUILD_ID`, `TREE_SRCU`, `MODULE_UNLOAD`, `SMP`, `KALLSYMS`,
  `GENERIC_BUG`, `SYSFS` are `y` and `KUNIT` is `m`; `FTRACE_MCOUNT_RECORD`,
  `FUNCTION_ERROR_INJECTION`, `PRINTK_INDEX` and `LIVEPATCH` are off. List them on your tree:
  ```sh
  sed -n '/^struct module {/,/^}/p' "$KERNEL_SRC/include/linux/module.h" | grep -o 'CONFIG_[A-Z0-9_]*' | sort -u
  ```
- `sig_ok` is unconditional in this tree (commented "Unconditionally compiled in Android to preserve ABI
  compatibility"), so module signing options do not move it.

### 4.6 Semantics of inline functions and macros

**No tool catches this.** A `static inline` function in `include/` is copied into every module that
calls it. Its body is not in the CRC (genksyms looks only at signatures), not in the `.stg` (it
emits no symbol), and not in vermagic.

- `put_task_struct()` (`include/linux/sched/task.h`) inlines the refcount decision and calls the
  exported `__put_task_struct()` only when the count hits zero. If you change that policy (for
  example, always going through RCU), old modules keep the old one. The result is a use-after-free
  or a leak.
- `task_cpu()` (`include/linux/sched.h`) inlines "the CPU number lives in `thread_info`". Move it,
  and prebuilt modules read garbage.

Treat an inline body as a struct layout that nobody diffs. The same holds for macros in `include/`:
`container_of`, `list_for_each_entry`, the field names `ANDROID_VENDOR_DATA` generates, and accessor
macros such as `get_hmbird_ts(p)` (`include/linux/sched/hmbird.h`).

### 4.7 `task_struct` and other core structs

`task_struct` is the worst case. It is 4800 bytes with 217 members, fully recorded in the `.stg`, and
referenced by almost every vendor-hook signature. Its layout in 6.6.118 (measured):

| Region | Offset (bytes) | Source |
|---|---|---|
| `thread_info` | 0 | `CONFIG_THREAD_INFO_IN_TASK=y` |
| ordinary fields | 48 – 3007 | |
| `android_vendor_data1[64]` | 3008 – 3519 | `include/linux/sched.h` |
| `android_oem_data1[6]` | 3520 – 3567 | same |
| KABI slots 1 / 2 / 3 (unions) | 3576 / 3584 / 3592 | same |
| `android_kabi_reserved4..8` | 3600 – 3639 | same |
| `struct thread_struct thread` | 3648 – 4767 (1120 bytes) | must stay last (arch, variable-size) |
| tail padding | 32 | 64-byte alignment |

Because `thread` must stay last, there is no safe place to insert a field. The same applies to the
private scheduler structs in the `.stg` (`struct rq`, `struct cfs_rq`; see §1).

**The trap CRC cannot see: `CONFIG_SLIM_SCHED`.** `include/linux/sched.h`:

```c
#ifdef CONFIG_SLIM_SCHED
        ANDROID_KABI_USE(1, unsigned long sched_prop);
        ANDROID_KABI_USE(2, struct sched_ext_entity *scx);
        ANDROID_KABI_USE(3, struct task_dma_buf_info *dmabuf_info);
#else
        ANDROID_KABI_USE(1, struct task_dma_buf_info *dmabuf_info);
        ANDROID_KABI_RESERVE(2);
        ANDROID_KABI_RESERVE(3);
#endif
```

`SLIM_SCHED` is `default n` in `kernel/Kconfig.preempt`, but `gki_defconfig` sets it to `y` (verified).

- With `y`, byte offset 3576 is `sched_prop` (an integer) and `dmabuf_info` is in slot 3.
- With `n`, the same offset 3576 is `dmabuf_info` (a pointer), and slots 2 and 3 are empty.
- `ANDROID_KABI_USE` collapses to `u64 android_kabi_reservedN` under `__GENKSYMS__`, so **both
  configs give identical CRCs**. The size is also identical (union), so `insmod` succeeds.
- A module built with `y` that reads `p->sched_prop` reads a pointer as an integer on an `n` kernel.
  The reverse dereferences an integer, which panics.

Flipping `CONFIG_SLIM_SCHED` silently changes the meaning of those slots for every prebuilt module
that touches `sched_prop`, `scx` or `dmabuf_info`, and nothing prevents such a module from loading.
Modules that never touch the slots are unaffected, so check each one. The in-tree user of
`sched_prop` is the HMBIRD scheduling class (`include/linux/sched/hmbird.h`, `kernel/sched/ext.c`).
