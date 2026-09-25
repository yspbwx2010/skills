# Exported KPM API

Symbols KernelPatch exports to KPMs with `KP_EXPORT_SYMBOL`, plus the header-provided helpers.
A KPM links only against these; anything else must be found with `kallsyms_lookup_name`.
Verified against KernelPatch 0.13.9 — this is the actual `KP_EXPORT_SYMBOL` set, not the doc's
table (see the trap at the bottom).

## Headers

KernelPatch core — `kernel/include/`:

| Header | Purpose |
| --- | --- |
| `<kpmodule.h>` | lifecycle macros |
| `<hook.h>` | inline + function-pointer hook API, `hook_fargs*_t`, `hook_err_t` |
| `<hotpatch.h>` | live instruction patching |
| `<kpmalloc.h>` | KP allocator |
| `<log.h>` | `logkd/logki/logkw/logke` (+ `logkf*` variants that prepend `__func__`) |
| `<compiler.h>` | `__noinline`, `__must_check`, … |
| `<ktypes.h>`, `<common.h>` | types, `kver`, `kpver` |
| `<symbol.h>`, `<kallsyms.h>` | symbol lookup |

KernelPatch patch layer — `kernel/patch/include/`:

| Header | Purpose |
| --- | --- |
| `<syscall.h>` | syscall hooks, `syscall_argn` |
| `<kputils.h>` | userspace copy helpers |
| `<kstorage.h>` | kernel storage |
| `<sucompat.h>`, `<accctl.h>` | su allow-list / credential switching |
| `<taskext.h>` | per-task local storage |
| `<kconfig.h>` | query the kernel's build config |
| `<ksyms.h>` | struct-offset tables |
| `<uapi/scdefs.h>` | SuperCall codes |

Linux stubs (backed by kfunc exports): `<linux/printk.h>` (`pr_info/err/warn/debug`),
`<linux/string.h>`, `<linux/sched.h>`, `<linux/cred.h>`, `<linux/uaccess.h>`, `<asm/current.h>`
(`current`), `<uapi/asm-generic/unistd.h>` (`__NR_*`).

## Core

| Symbol | Signature / meaning |
| --- | --- |
| `kver` | `uint32_t` kernel version, `major<<16 \| minor<<8 \| patch` |
| `kpver` | `uint32_t` KernelPatch version |
| `kallsyms_lookup_name(name)` | `unsigned long (*)(const char*)` — kernel symbol by name |
| `kallsyms_lookup_name_by_suffix(suffix)` | match on a name suffix |
| `kallsyms_on_each_symbol(fn,data)`, `kallsyms_on_each_match_symbol(...)` | iterate symbols |
| `symbol_lookup_name(name)` | look up a KernelPatch-exported symbol by name |
| `printk(fmt, ...)` | kernel log; prefer the `pr_*` / `logk*` macros |

## Inline hook — `<hook.h>`  (details in `references/hooks.md`)

`hook`, `unhook`, `hook_wrap`, `hook_unwrap_remove` (+ inline `hook_unwrap`), `hook_chain_add`,
`hook_chain_remove`, `hook_prepare`, `hook_install`, `hook_uninstall`, `fp_hook`, `fp_unhook`,
`fp_hook_wrap`, `fp_hook_unwrap`. Typed wrappers `hook_wrap0..12` / `fp_hook_wrap0..12` are static
inlines.

## Syscall hook — `<syscall.h>`  (details in `references/syscall-hook.md`)

`hook_syscalln`, `unhook_syscalln`, `hook_compat_syscalln`, `unhook_compat_syscalln`,
`hook_syscalln_override`, `hook_syscalln_legacy`, `fp_wrap_syscalln`, `fp_unwrap_syscalln`,
`inline_wrap_syscalln`, `inline_unwrap_syscalln`, `syscall_hook_global_enabled`,
`syscall_dispatch_init`, `syscall_hook_set_gate`, `raw_syscall0..6`, `sys_call_table`,
`compat_sys_call_table`, `has_syscall_wrapper`, `has_config_compat`. `syscall_argn` /
`set_syscall_argn` / `fp_hook_syscalln` / `inline_hook_syscalln` and the `_unhook_` forms are
static inlines over the `*_wrap_syscalln` exports.

## Userspace access — `<kputils.h>`

| Signature | Meaning |
| --- | --- |
| `int __must_check compat_copy_to_user(void __user *to, const void *from, int n)` | copy to user |
| `long compat_strncpy_from_user(char *dest, const char __user *src, long count)` | string from user |
| `void __user *copy_to_user_stack(const void *data, int len)` | push onto the user stack |
| `uid_t current_uid(void)` | current task UID |
| `get_random_u64()` | random 64-bit |

## Kernel storage — `<kstorage.h>`

`write_kstorage(gid,did,data,offset,len,is_user)`, `read_kstorage(...)`, `get_kstorage(gid,did)`
(hold the RCU read lock), `on_each_kstorage_elem(gid,cb,udata)`, `list_kstorage_ids(...)`,
`remove_kstorage(gid,did)`, `kstorage_generation`.

## SU / access control — `<sucompat.h>`, `<accctl.h>`

Exported: `is_su_allow_uid(uid)`, `su_add_allow_uid(uid,to_uid,scontext)`,
`su_remove_allow_uid(uid)`, `su_allow_uid_nums()`, `su_allow_uids(is_user,out,num)`,
`su_allow_uid_profile(is_user,uid,profile)`, `su_reset_path(path)`, `su_get_path()`,
`set_ap_mod_exclude(uid,exclude)`, `get_ap_mod_exclude(uid)`, `list_ap_mod_exclude(uids,len)`.

## Task extension — `<taskext.h>`

`task_ext_size` is exported. `reg_task_local(size)`, `has_task_local(ext,offset)`,
`task_local_ptr(ext,offset)` are **static inlines** in the header (usable, not symbols).

## Kernel struct offsets — `<ksyms.h>`

`task_struct_offset`, `cred_offset`, `mm_struct_offset`, `thread_size`, `thread_info_in_task`,
`stack_in_task_offset`, `stack_end_offset`, and related layout values.

## Kernel config — `<kconfig.h>`

`kp_kconfig_available()`, `kp_kconfig_enabled(name)`, `kp_kconfig_value(name)`,
`kp_kconfig_data()`, `kp_kconfig_size()`. `name` works with or without the `CONFIG_` prefix.

## String / memory — `<linux/string.h>`

`strcpy strncpy strlcpy strscpy strcat strncat strcmp strncmp strchr strrchr strlen strnlen strstr
strnstr strspn strcspn memset memcpy memmove memcmp memchr sprintf snprintf vsnprintf kasprintf
sscanf …` — all kfunc-backed exports, called through the `<linux/string.h>` inline wrappers.

## Trap: the doc's symbol table is not the export set

`doc/en/module.md` claims "all functions … below are exported by `KP_EXPORT_SYMBOL`" and lists
`commit_su(uid, sctx)` and `task_su(pid, to_uid, sctx)`. **They are not exported** (defined in
`patch/common/accctl.c`, no `KP_EXPORT_SYMBOL`). A KPM that calls `commit_su`/`task_su` directly
fails to load with `unknown symbol: commit_su`. If you need them, resolve at runtime with
`kallsyms_lookup_name` is **not** enough either (they are KernelPatch functions, not kernel
symbols) — use the su allow-list API (`su_add_allow_uid`) which *is* exported, or invoke the
credential switch through the SuperCall/su path instead. When in doubt, trust this export list
(extracted from the source), not the prose table.
