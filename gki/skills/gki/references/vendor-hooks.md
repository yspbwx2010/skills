# Vendor hooks (`android_vh_*` / `android_rvh_*`)

Pinned to OGKI `android15-6.6` (Linux 6.6.118, `KMI_GENERATION=8`, `gki_defconfig`, arm64, clang-r510928).
Counts and config facts below come from that tree and its `gki_defconfig` build. Re-verify on your tree
with the commands given. The hooks themselves, grouped by subsystem, are in [hook-catalog.md](hook-catalog.md).
A compilable module is in [../assets/vendor-hook/](../assets/vendor-hook/).

## Four checks, not one

These are four separate facts. Passing one says nothing about the others.

| Fact | How to check | Fails when |
|---|---|---|
| **Declared** (and with which macro) | `grep -rn -A3 'HOOK(android_vh_foo,' "$KERNEL_SRC/include/trace/hooks/"` | The name is missing. Read the macro, not the prefix: `android_rvh_ogki_check_task_tags` is a plain `DECLARE_HOOK`. |
| **Exported** | `grep -w __tracepoint_android_vh_foo "$KERNEL_OUT/Module.symvers"` must print an `EXPORT_SYMBOL_GPL` line | No `EXPORT_TRACEPOINT_SYMBOL_GPL` line exists for it (2 hooks in this tree). |
| **Actually called** | `grep -rn 'trace_android_vh_foo(' "$KERNEL_SRC" --include='*.[ch]' \| grep -v include/trace/hooks/`, then read the call site | No call site (39 hooks in this tree). The call site is compiled out by your config. **The caller never reads your out-parameter back** (see `android_rvh_place_entity` in the catalog). |
| **Registrable at runtime on the target** | `insmod` plus the return code of `register_trace_*()` | Non-GPL license. CRC mismatch. An unsigned module hits the unprotected-symbol gate. Both restricted slots are taken (`-EBUSY`). The device kernel is not built from your tree. |

Never make an error go away with a function-pointer cast, a guessed struct offset, or forced loading
(`insmod -f`, `--force-vermagic`, `--force-modversion`). A cast defeats the prototype check that
`register_trace_*()` does. KCFI (`CONFIG_CFI_CLANG=y`) then traps the mismatched indirect call at runtime.

## Quick start

1. **Include the hook header only. Never `#define CREATE_TRACE_POINTS`.** The tracepoints are already
   defined and exported by `drivers/android/vendor_hooks.c` (all headers except `sched.h`) and
   `kernel/sched/vendor_hooks.c` (`sched.h`). Defining them again duplicates `__tracepoint_*` /
   `__traceiter_*`. `#include <trace/hooks/cpufreq.h>` gives you `register_trace_android_vh_*()`.
2. **Use a GPL-compatible `MODULE_LICENSE`.** All 746 `__tracepoint_android_*` exports are
   `EXPORT_SYMBOL_GPL`, as are `tracepoint_probe_register`, `tracepoint_probe_unregister` and
   `android_rvh_probe_register`. Otherwise `insmod` fails with unknown symbols.
3. **Know which macro declared the hook.** `DECLARE_HOOK` hooks can be registered and unregistered
   freely. `DECLARE_RESTRICTED_HOOK` hooks can be registered but **never unregistered**, with 2 probes
   per hook. See "Restricted hooks" below.

The callback prototype is `void *data` followed by the hook's `TP_PROTO(...)`, with nothing changed. The
second argument of `register_trace_<hook>(probe, data)` is passed back as `data`.

```c
#include <linux/cpufreq.h>
#include <linux/module.h>
#include <trace/hooks/cpufreq.h>        /* no CREATE_TRACE_POINTS */

/* TP_PROTO(struct cpufreq_policy *policy, unsigned int *target_freq, unsigned int old_target_freq) */
static void cb(void *data, struct cpufreq_policy *policy,
               unsigned int *target_freq, unsigned int old_target_freq) { }

static int __init m_init(void)
{
        return register_trace_android_vh_cpufreq_resolve_freq(cb, NULL);
}
static void __exit m_exit(void)
{
        unregister_trace_android_vh_cpufreq_resolve_freq(cb, NULL);
        tracepoint_synchronize_unregister();   /* before the code is freed */
}
module_init(m_init);
module_exit(m_exit);
MODULE_LICENSE("GPL");
```

Build (`KERNEL_OUT` must hold the full kernel build's `.config` and `Module.symvers`. `make Image`
alone does not produce a complete `Module.symvers`):

```sh
make -C "$KERNEL_SRC" O="$KERNEL_OUT" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
     KCFLAGS=-D__ANDROID_COMMON_KERNEL__ M="$PWD" modules
```

## Plain vs restricted

Both macros are in `include/trace/hooks/vendor_hooks.h`. `DECLARE_HOOK` is `DECLARE_TRACE`, a plain
tracepoint. `DECLARE_RESTRICTED_HOOK` generates a cut-down variant.

| | `DECLARE_HOOK` | `DECLARE_RESTRICTED_HOOK` |
|---|---|---|
| Register | `register_trace_<h>()` → `tracepoint_probe_register()`; also `register_trace_prio_<h>()` | `register_trace_<h>()` → `android_rvh_probe_register()` |
| Unregister | `unregister_trace_<h>()` | **not generated** ("vendor hooks cannot be unregistered") |
| Probes per hook | unlimited | **2** (`ANDROID_RVH_NR_PROBES_MAX`), then `-EBUSY` |
| `data` | free | once the hook has a probe, a non-NULL `data` gives `WARN_ON` + `-EINVAL`. Pass `NULL`. |
| Call path | `__DO_TRACE`: `preempt_disable_notrace()`, probe iterator. With LOCKDEP, warns if RCU is not watching. | no preempt disable, no RCU. arm64 6.6 has no `CONFIG_HAVE_STATIC_CALL`, so the call goes directly to `__traceiter_<h>()` |
| Where the kernel uses it | paths where RCU is watching | rq-lock, idle, IRQ-off and other paths where a tracepoint is not allowed (inferred design intent) |

Consequences:

- A plain-hook callback runs with preemption disabled. It must not sleep, take a mutex or allocate with
  `GFP_KERNEL`.
- A restricted-hook callback runs in whatever context its call site has: often the rq lock is held and
  IRQs are off. Read the call site. Under the rq lock or `p->pi_lock`, use `printk_deferred()`, not
  `printk()`. Example: `android_rvh_select_task_rq_fair` runs under `p->pi_lock` with IRQs off and no
  rq lock; the per-hook contexts are in [hook-catalog.md](hook-catalog.md).
- All probes on a hook run in turn and share the same out-pointers. The last writer wins. On a device,
  other vendor modules may register the same plain hook and overwrite what you wrote.
- `register_trace_*()` takes `tracepoints_mutex`, so call it from process context (`module_init` is fine).
  Probes may run on other CPUs before `register_*()` returns, so initialise your state first.

**If the config is off.** If `CONFIG_TRACEPOINTS` or `CONFIG_ANDROID_VENDOR_HOOKS` is `n`, both macros
become `DECLARE_EVENT_NOP`. That leaves an empty `trace_<h>()` and **no `register_trace_*` /
`unregister_trace_*` at all**, so a module that registers hooks does not compile. The `-ENOSYS` stubs
exist only for plain tracepoints built with tracepoints disabled. Both options are `y` in this
`gki_defconfig`. Check with `grep -E 'CONFIG_(TRACEPOINTS|ANDROID_VENDOR_HOOKS)=' "$KERNEL_OUT/.config"`.

## Which hooks an out-of-tree module can use

**`DECLARE_HOOK` does not export anything.** It only emits declarations and inline helpers. Each hook
is defined and exported by one `EXPORT_TRACEPOINT_SYMBOL_GPL(<h>)` line, which exports
`__tracepoint_<h>`, `__traceiter_<h>` and `__SCK__tp_func_<h>`:

| File | Defines `CREATE_TRACE_POINTS` for | GPL exports |
|---|---|---|
| `drivers/android/vendor_hooks.c` | every hook header except `sched.h` | 630 |
| `kernel/sched/vendor_hooks.c` | `sched.h` | 116 |

No vendor hook uses a non-GPL `EXPORT_TRACEPOINT_SYMBOL()`.

Counts in 6.6.118 (verified against the `gki_defconfig` build's `Module.symvers`):

| | |
|---|---|
| Hook headers | 71 in `include/trace/hooks/` (`vendor_hooks.h` holds only macros) |
| Unique hook names | 747. There are 748 declarations because `android_rvh_alloc_and_link_pwqs` is declared twice around `__GENKSYMS__` and is compiled as restricted. |
| As compiled | 552 `DECLARE_HOOK` + 195 `DECLARE_RESTRICTED_HOOK` (by name prefix: 551 `vh` / 197 `rvh`) |
| `__tracepoint_android_*` exports | 746, all `EXPORT_SYMBOL_GPL`. One of them, `android_trigger_vendor_lmk_kill`, is a real `TRACE_EVENT` and not a hook. |
| Exported hooks | **745 of 747** |
| Hooks with an in-tree call site | 708. The other 39 never fire from the kernel itself. |

Declared but not exported, so not registrable from a module:

| Hook | Status |
|---|---|
| `android_rvh_do_traversal_lruvec_ex` (`mm.h`) | Called from `mm/memcontrol.c` but not exported. Only built-in code can use it. |
| `android_vh_ogki_ufs_clock_scaling` (`ogki_honor.h`) | Neither exported nor called anywhere. |

A module that only registers a hook references `__tracepoint_<h>` plus the register/unregister function.
`__traceiter_<h>` and `__SCK__tp_func_<h>` are needed only if the module fires the hook itself (from the
macro expansion). Run `llvm-nm -u your.ko` to see exactly which symbols the module imports.

**Trimming and the unprotected-symbol gate** (config-dependent):

- `CONFIG_TRIM_UNUSED_KSYMS` is not set in this `gki_defconfig` build, so all 746 exports are in
  `vmlinux`. Check with `grep TRIM_UNUSED_KSYMS "$KERNEL_OUT/.config"`.
- A trimmed or KMI-enforcing build keeps the **union** of all `android/abi_gki_aarch64*` symbol lists,
  not only one vendor's list. In 6.6.118 that union contains all 746 `__tracepoint_android_*` and
  `__traceiter_android_*`, plus the three register/unregister functions. A single vendor list being
  short does not mean hooks get trimmed.
- With `CONFIG_MODULE_SIG_PROTECT=y`, an **unsigned** module may resolve only symbols exported by other
  unsigned modules or listed in the KMI symbol list (`-EACCES` otherwise, see `kernel/module/main.c`).
  A build without a symbol list generates an empty list, and then the gate is open. Check with
  `grep -A1 'gki_unprotected_symbols\[\]' "$KERNEL_OUT/include/generated/gki_module_unprotected.h"`:
  a next line of `};` means the gate is empty.
- `CONFIG_MODVERSIONS=y`: build against the `Module.symvers` of the kernel that will load the module.
  A CRC mismatch fails the load. Equal CRCs do not prove the semantics are compatible.

## The type trap

Many high-value scheduler hooks pass types whose definitions are private, outside `include/`:

| Private type | Defined in | Seen in |
|---|---|---|
| `struct rq`, `struct cfs_rq`, `struct rq_flags`, `struct sched_group` | `kernel/sched/sched.h` | most `sched.h` restricted hooks |
| `struct binder_proc`, `binder_thread`, `binder_transaction`, `binder_work` | `drivers/android/binder_internal.h` | most `binder.h` hooks |
| `enum scan_balance`, `struct scan_control` | `mm/vmscan.c` | `vmscan.h` hooks |

The hook header only forward-declares them. A module can pass such pointers along but not dereference
them. `struct sched_entity`, `struct task_struct`, `struct uclamp_se`, `struct cpufreq_policy` and
`struct cpuidle_device` are public (`include/linux/`).

What to do, in order:

1. Prefer hooks whose arguments are public types or scalars/out-pointers (`struct task_struct *`,
   `struct cpufreq_policy *`, `struct cpuidle_device *`, `struct folio *`, `int *`, `bool *`).
2. Use exported accessors and public fields, not the private struct.
3. Do not copy `kernel/sched/sched.h` (or part of it) into your module, and do not hard-code offsets. A
   forward declaration does not license copying the layout. The full `struct rq` does appear in
   `android/abi_gki_aarch64.stg`. That makes changes to it detectable, but it does not make it an
   interface. The only layout that is correct is the one from the exact source and config the device
   kernel was built from.

`task_struct` carries `android_vendor_data1[64]` and `android_oem_data1[6]` (`ANDROID_VENDOR_DATA_ARRAY` /
`ANDROID_OEM_DATA_ARRAY`, `CONFIG_ANDROID_VENDOR_OEM_DATA=y`). These are a **shared convention space**
used by SoC and OEM modules. They are not free slots for a third-party module. Seeing no user in the
source does not mean that a device's vendor modules leave a slot unused. Do not store state there unless
you own the convention on that device.

## Registration patterns

### Plain hooks

- Register in `module_init`. Check every return with `if (ret)`. On failure, unregister what you already
  registered, in reverse order, then call `tracepoint_synchronize_unregister()` and return the error.
- In `module_exit`, unregister every probe with the **same `(probe, data)` pair**, then call
  `tracepoint_synchronize_unregister()` before returning. It waits for callbacks still running on
  other CPUs. Without it, unload can free code that is still executing.
- `register_trace_prio_<h>(probe, data, prio)` orders your probe relative to others on the same hook.
- In-tree patterns: `crypto/fips140-module.c` (chained `register_trace_*() ?: ...`) and
  `kernel/locking/oplus_locking.c` (register macro with `goto` unwind).

The template in `../assets/vendor-hook/` does exactly this with `android_vh_cpufreq_resolve_freq` and
`android_vh_cpu_idle_enter`.

### Restricted hooks

The rules:

- **There is no unregister API.** Once registered, the callback stays in the hook's probe array for the
  life of the kernel, so **the module can never be unloaded**. Do not provide `module_exit()`. A module
  with an init but no exit is refused by `rmmod` with `-EBUSY` (`CONFIG_MODULE_FORCE_UNLOAD` is off in
  `gki_defconfig`). If a module_exit did free the code, the next hook call would jump into freed memory
  (inferred, not tested).
- **Only 2 slots per hook**, shared by every built-in and loaded registrant. The third registration gets
  `-EBUSY`. No built-in code in this tree registers any restricted hook, but that does **not** mean the
  slots are free on a device: vendor modules load first. Registering is the only way to find out.
- Check the result with `if (ret)`. Do not assume the sign: the call returns `-EBUSY`, `-EINVAL` (non-NULL
  `data` on a hook that already has a probe), or `ENOMEM` as a **positive** value from the allocation
  path (`rvh_func_add()` in `kernel/tracepoint.c`).
- Return a **negative** errno from `module_init`: `ret > 0 ? -ret : ret`. `do_init_module()`
  (`kernel/module/main.c`) fails the load only for `ret < 0`. A positive return only prints
  "suspiciously returned ... loading module anyway", so the module would stay loaded, unloadable and
  without its hook. Plain `register_trace_*()` returns 0 or a negative errno.
- Pass `data = NULL`.
- Register restricted hooks **last** in `module_init`, after everything that can fail. If init failed
  after a successful registration, the module memory would be freed with the hook still pointing into it
  (inferred).
- Keep restricted hooks out of shipped templates. Use them only in modules designed never to unload.

```c
static void my_rvh_cb(void *data, struct cpufreq_policy *policy)
{
        /* caller's context: no sleeping, keep it short */
}

static int __init my_init(void)
{
        int ret;

        /* ... everything that can fail goes before this ... */
        ret = register_trace_android_rvh_cpufreq_transition(my_rvh_cb, NULL);
        if (ret) {                  /* -EBUSY, -EINVAL, or positive ENOMEM */
                pr_err("rvh register failed: %d\n", ret);
                /* a positive return would count as success in do_init_module() */
                return ret > 0 ? -ret : ret;
        }
        return 0;                   /* nothing after this may fail */
}
module_init(my_init);               /* no module_exit(): unloading is refused */
MODULE_LICENSE("GPL");
```

## OGKI has no OnePlus-private hooks

`include/trace/hooks/` was diffed file by file against upstream ACK tag `android15-6.6-2026-01_r22`
(verified). Both have the same 71 files and the same 747 names. Two files differ only in trailing
whitespace (`binder.h`) and declaration order (`mm.h`).

- `ogki_honor.h` is upstream: hooks contributed to ACK by Honor under the OGKI scheme. It has 37 hooks,
  36 exported, and **no call site in the kernel**. A module could fire them itself, since the
  tracepoints are exported.
- Later upstream snapshots add `rcu.h` and `sound.h`. That is a snapshot difference, not a removal.
- OnePlus changes live elsewhere. For example, `kernel/locking/oplus_locking.c` registers several
  `dtask.h` plain hooks. Plain hooks allow many probes, so these coexist with yours, but they may also
  write the same out-parameters.

## Verified vs inferred

Verified (source, macro expansion, `gki_defconfig` build artifacts): all counts above. The two unexported
hooks. The restricted-hook rules (no unregister, 2 slots, `-EBUSY`, `WARN_ON` + `-EINVAL` on `data`,
positive `ENOMEM`). `do_init_module()` accepting a positive init return. `rmmod` refusal without
`module_exit`. The `p->pi_lock` / IRQs-off context of `android_rvh_select_task_rq_fair`. No
`CONFIG_HAVE_STATIC_CALL` on arm64 6.6.
`TRIM_UNUSED_KSYMS` off. The symbol-list union covering all hook exports. Every signature in
[hook-catalog.md](hook-catalog.md).

Inferred, not verified on a device:

- Restricted hooks are meant for rq-lock / RCU-not-watching / IRQ-off paths. This is read from the macro
  (no `__DO_TRACE`, no RCU check). No comment states it.
- Unloading code that a restricted hook still points to crashes the kernel. Not tested.
- `android_rvh_alloc_pages_adjust_wmark` and `android_rvh_perform_reclaim` declare a condition of `3`
  and `4` instead of `1`. Any non-zero value means "always", so this looks harmless.

Could not confirm:

1. Whether the target device runs a kernel built from this tree and config. Its `Module.symvers` may
   differ, so re-check exports and CRCs against that kernel.
2. Which hooks the device's own vendor modules register. For plain hooks, they may overwrite your
   out-parameters. For restricted hooks, they use up slots.
3. Why `android_rvh_gic_v3_set_affinity` and `android_rvh_try_alloc_pages` are exported but never called.
