# Third-party kernel vs vendor, and choosing a path for a change

Facts are for OGKI `android15-6.6` (Linux 6.6.118) built with plain Kbuild from `gki_defconfig`.
Config-dependent statements say how to re-check them.

## 1. Third-party kernel builder vs vendor/OEM developer

| Aspect | Vendor shipping to an OEM | You (own kernel build, flashed yourself) |
|---|---|---|
| Change GKI kernel source | No: a modified kernel loses GKI certification | **Yes**, the tree is yours |
| Exports a module can use | KMI list union (9197 here) on a trimmed, protected official build (inferred from the build rules) | **All 16923** (no trimming, empty gate: [symbols-and-signing.md](symbols-and-signing.md)) |
| New symbol | Edit the vendor symbol list, upstream to ACK, wait for a later GKI release | One `EXPORT_SYMBOL_GPL` line |
| Module signing | Unsigned modules are held to KMI symbols by the gate | Gate empty in this build; unsigned is fine |
| defconfig | Only non-GKI options, in the vendor fragment | Anything |
| CFI | Mandatory | Your choice, but **keep it on** (below) |
| ABI change check | Kleaf strict mode and ABI diff fail the build | None, unless you run one |

### The three costs you must carry

1. **You own the compatibility of every stock module on the device.** Changing any type or config that a
   vendor module's imported symbols depend on can change CRCs; that module then refuses to load
   (`disagrees about version of symbol`). Which modules fail must be judged per symbol, type, config and
   runtime semantics; one config change does not automatically break all of them, and matching CRCs do
   not prove compatibility either ([architecture.md](architecture.md) section 3.4). `vendor_dlkm` usually
   holds many `.ko` files you have no source for. After every kernel change check on the device:
   `dmesg | grep -iE 'disagrees about version|Unknown symbol|Protected symbol|version magic|struct module size|CFI failure'`.
2. **Do not turn off CFI or SCS to make something build.** Stock modules are built with KCFI and a
   reserved x18; their indirect calls into kernel code expect type-hash prefixes that a non-CFI kernel
   does not emit (inferred: expect a trap at the first such call). Do not enable
   `CONFIG_MODULE_FORCE_LOAD` (off in this build) and do not force-load modules: loading a module whose
   CRCs mismatch makes the kernel access memory with the wrong layouts.
3. **Do not build long-lived code on the ~7.7k non-KMI exports.** They can vanish at any ACK merge. A
   module that uses only KMI-listed symbols runs on your kernel and on an official one. List what your
   module needs outside the KMI:

   ```sh
   awk '!/^\[/ && !/^[[:space:]]*#/ && NF {print $1}' \
       "$KERNEL_SRC"/android/abi_gki_aarch64 "$KERNEL_SRC"/android/abi_gki_aarch64_* \
     | LC_ALL=C sort -u > kmi.txt
   llvm-nm -u mymod.ko | awk '{print $2}' | LC_ALL=C sort -u > need.txt
   LC_ALL=C comm -23 need.txt kmi.txt       # imported symbols not in any KMI list
   ```

## 2. Which path for a change

Try in this order; take the first that works.

### 1. Plain out-of-tree module

The change needs only existing exported APIs. Cheapest: the kernel is untouched, stock modules are
unaffected, and the module builds, loads and unloads on its own. Start from
[`../assets/kprobe-notifier/`](../assets/kprobe-notifier/).

### 2. Vendor hook

You must step into an internal kernel path (CPU selection, reclaim policy, lock waits, binder, UFS I/O).
Rules, in short ([vendor-hooks.md](vendor-hooks.md) has the full treatment):

- Only `#include <trace/hooks/<file>.h>`; **never** define `CREATE_TRACE_POINTS` in a module.
- `MODULE_LICENSE` must be GPL-compatible: all 746 `__tracepoint_android_*` exports in this build are
  `EXPORT_SYMBOL_GPL`.
- A hook being **declared**, **exported**, **actually called** at the point you need, and **registrable
  at runtime** are four separate facts. Check each; the export count is not a count of usable hooks.
- Restricted hooks (`android_rvh_*`) have **no unregister API** and a limited number of slots: once
  registered, the callback code can never be unloaded. Check the result with `if (ret)`; do not assume
  errors are always positive or always negative.

### 3. kprobe

There is no hook where you need one, but the function is visible in kallsyms.
`CONFIG_KPROBES=y` and `CONFIG_KRETPROBES=y`; `register_kprobe()` is `EXPORT_SYMBOL_GPL`.

- The target must resolve through kallsyms (global or `static`), must not be inlined away and must not be
  on the kprobe blacklist; otherwise registration fails (`-ENOENT` / `-EINVAL`). Check
  `grep -w <sym> /proc/kallsyms` on the device.
- `CONFIG_FUNCTION_TRACER` is off in this build (`grep FUNCTION_TRACER "$KERNEL_OUT"/.config`): no ftrace
  function hooks, no fprobe, and `CONFIG_LIVEPATCH` does not exist (it depends on ftrace). Turning it on
  in your kernel is not an option because it adds `struct module` fields (via `FTRACE_MCOUNT_RECORD`),
  and the loader then refuses every stock module ([kmi-breaking-changes.md](kmi-breaking-changes.md)
  section 4.5e).
- A kprobe replaces an instruction with `BRK` and runs the handler from the debug exception: far costlier
  than ftrace. Keep it off hot paths. Handlers run in atomic context: no sleeping, no `GFP_KERNEL`.
- For tracing without a module, `CONFIG_KPROBE_EVENTS=y` gives tracefs kprobe events.
- `kallsyms_lookup_name()` is **not exported** (`kernel/kallsyms.c` exports only the `sprint_symbol*`
  family). The usual workaround registers a kprobe on `kallsyms_lookup_name` just to read `kp.addr`. Calling
  through that address, or through any address it returns, is an indirect call checked by KCFI
  ([cfi.md](cfi.md) rule 4). Prefer using such addresses only to read data.

Complete example: [`../assets/kprobe-notifier/kprobe_notifier.c`](../assets/kprobe-notifier/kprobe_notifier.c).

### 4. defconfig change

You only need an option GKI leaves off. Editing `arch/arm64/configs/gki_defconfig` is the smallest kernel
change, **but** check whether the option changes a struct layout or an exported function's signature: a
debug option that adds a field to `struct task_struct` changes the CRC of every symbol that reaches that
type. Compare CRCs before and after the change:

```sh
awk '{print $2, $1}' before/Module.symvers | LC_ALL=C sort > a.txt   # symbol CRC
awk '{print $2, $1}' after/Module.symvers  | LC_ALL=C sort > b.txt
diff a.txt b.txt
```

This catches CRC changes only, not semantic or runtime-behaviour changes, and has not been validated as a
complete check.

### 5. Patch the kernel source

Only when 1 to 4 all fail. Discipline:

1. **Prefer adding `EXPORT_SYMBOL_GPL` to changing logic.** A new export changes no type layout and does
   not by itself break existing modules.
2. **Prefer adding a new vendor hook to editing a function body:** one `DECLARE_HOOK`, one `trace_...()`
   call and one `EXPORT_TRACEPOINT_SYMBOL_GPL`, with the logic kept in your module.
3. **Never change struct definitions under `include/`.** If a field is unavoidable, see the reserved-slot
   rules in [extending-safely.md](extending-safely.md) and what breaks the KMI in
   [kmi-breaking-changes.md](kmi-breaking-changes.md). `android_vendor_data*` / `android_oem_data*` are
   shared vendor/OEM space, not free slots: stock modules may already use them even if the source shows
   no user.
4. One patch per file, each stating why paths 1 to 4 do not work.

## 3. Verified vs inferred, and open questions

Verified in the 6.6.118 source and a `gki_defconfig` build: every config value quoted in this skill; the
trimming path in modpost; the three `MODULE_SIG_PROTECT` changes and the empty gate; `M=` builds are
unsigned; the build-time throwaway signing key; the KCFI failure chain; `same_magic()` skipping the release
string; `kallsyms_lookup_name()` not exported; no `CONFIG_LIVEPATCH`.

Inferred, not verified:

- Partition contents of `vendor_boot` / `vendor_dlkm` (Android background; no evidence in the tree).
- A failed boot-critical vendor module stops boot.
- Signing your own module gains nothing.
- A never-address-taken `static` function lacks a KCFI hash.
- A non-CFI kernel traps stock KCFI modules.

Could not confirm:

1. **Whether the device runs a kernel built from this tree.** An OEM image almost certainly trims and
   has a non-empty gate; then only KMI symbols are available to unsigned modules and the "freedoms" here
   reverse. They hold only for a kernel you built and flashed yourself.
2. **What is in `vendor_boot` / `vendor_dlkm`.** The tree has no list. On the device, list
   `/vendor/lib/modules/` (and the vendor_boot ramdisk) and run `llvm-nm -u` on each `.ko`; that decides
   which types you may touch.
3. **How binding `abi_gki_aarch64.stg` is in practice**: see [kmi-breaking-changes.md](kmi-breaking-changes.md).
4. **Which of the 602 `abi_gki_aarch64_oplus` symbols the OEM modules really use.** Only counted.
5. **A validated method to measure a defconfig change's CRC blast radius** (the `Module.symvers` diff
   above is the starting point, not a proven procedure).
