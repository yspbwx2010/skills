# Lifecycle callbacks and metadata

All from `<kpmodule.h>`. Verified against KernelPatch 0.13.9.

## Metadata macros

| Macro | Required | Limit (enforced at compile time) |
| --- | --- | --- |
| `KPM_NAME(x)` | yes | 32 bytes, must be unique among loaded modules |
| `KPM_VERSION(x)` | yes | 32 bytes |
| `KPM_LICENSE(x)` | yes | 32 bytes |
| `KPM_AUTHOR(x)` | no | 32 bytes |
| `KPM_DESCRIPTION(x)` | no | 512 bytes |

Each expands to a `KPM_INFO(...)` string placed in the `.kpm.info` ELF section, guarded by a
`_Static_assert` on length — an over-long value is a **build error**, not a load error. The loader
requires `name` and `version` to be present, or it rejects the module (`no .kpm.info section` /
`module name not found`).

## Callback macros and exact signatures

```c
typedef long (*mod_initcall_t)(const char *args, const char *event, void *reserved);
typedef long (*mod_ctl0call_t)(const char *ctl_args, char *__user out_msg, int outlen);
typedef long (*mod_ctl1call_t)(void *a1, void *a2, void *a3);
typedef long (*mod_exitcall_t)(void *reserved);
typedef long (*mod_eventcall_t)(const char *event, const char *args, void *reserved);

KPM_INIT(fn);    // required  -> .kpm.init
KPM_CTL0(fn);    // optional  -> .kpm.ctl0
KPM_CTL1(fn);    // optional  -> .kpm.ctl1
KPM_EXIT(fn);    // required  -> .kpm.exit
KPM_EVENT(fn);   // optional  -> .kpm.event  (undocumented in module.md, present in the header)
```

`.kpm.init` **and** `.kpm.exit` are mandatory; the loader returns `-ENOEXEC`
(`no .kpm.init or .kpm.exit section`) without them.

### init — `long init(const char *args, const char *event, void *reserved)`

Called once at load. Return `0` on success; **non-zero fails the load**, and the loader then calls
your `exit` and frees the module. `args` is the load argument string (from `sc_kpm_load` or the
embed `-A` flag; may be empty, never assume non-NULL content — check it). `event` is the trigger:
`"load"`/`"load-file"` for runtime loads, or a boot-event string (e.g. `"pre-kernel-init"`) when
embedded. `reserved` is `NULL`.

### ctl0 — `long ctl0(const char *ctl_args, char *__user out_msg, int outlen)`

Called on each `sc_kpm_control()`. `ctl_args` is the userspace-supplied control string. `out_msg`
is a **userspace** buffer of `outlen` bytes — write your reply with `compat_copy_to_user(out_msg,
buf, len)`, never a plain `memcpy`/`strcpy` (it is `__user` memory). Optional; a control call to a
module without ctl0 returns `-ENOSYS`.

### ctl1 — `long ctl1(void *a1, void *a2, void *a3)`

Alternate control entry for in-kernel callers (`module_control1`); three opaque pointers, no
userspace copy semantics. Rarely needed.

### exit — `long exit(void *reserved)`

Called on unload (and after a failed init). **Undo everything init/ctl0 installed here** — every
hook, every timer, every allocation. A hook left installed points into the module's freed memory
and panics the kernel on the next call. `reserved` is `NULL`.

### event — `long event(const char *event, const char *args, void *reserved)`

Optional. Broadcast to every loaded module (that registered one) when KernelPatch fires a boot/init
event via `notify_modules_event`. Distinct from init's `event` parameter: this fires on **later**
events for an already-loaded module.

## `hook_fargs*_t` — the callback argument block

Hook callbacks (`before`/`after`) receive a pointer to a `hook_fargs{N}_t` for a function of N
args. Field layout (verified):

```c
typedef struct {
    void *chain;
    int skip_origin;      // set non-zero in a `before` cb to skip the original function
    hook_local_t local;   // 8 uint64 scratch slots (data0..data7) shared between before/after
    uint64_t ret;         // the return value: readable in `after`, writable to override
    uint64_t arg0, arg1, ...;   // and args[] as a union alias
} hook_fargsN_t;
```

- `argN` count matches the wrap arity: `hook_fargs2_t` … `hook_fargs12_t` (0/1/3 alias `fargs4`,
  5–7 alias `fargs8`, 9–11 alias `fargs12`).
- For **syscall** hooks do **not** read `args->argN` directly — some kernels wrap syscalls in a
  `pt_regs`. Use `syscall_argn(args, n)` / `set_syscall_argn(args, n, v)` (see
  `references/syscall-hook.md`).
- `local.data0..data7` carry state from a `before` callback to its `after` callback on the same
  call — do not use module globals for per-call state (hooks are concurrent).
- Set `args->skip_origin = 1` in `before` to skip the original and (usually) set `args->ret`
  yourself.
