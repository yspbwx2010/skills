# Syscall hooks

From `<syscall.h>`. Built on the inline-hook framework, handles syscall-wrapper differences.
Verified against KernelPatch 0.13.9.

## Two strategies + one auto

| API | What it does |
| --- | --- |
| `inline_hook_syscalln(nr, narg, before, after, udata)` | inline-hook the syscall handler body |
| `fp_hook_syscalln(nr, narg, before, after, udata)` | replace the entry in the syscall table |
| `hook_syscalln(nr, narg, before, after, udata)` | auto-select the best method for this kernel |

`unhook`/removal counterparts: `inline_unhook_syscalln(nr, before, after)`,
`fp_unhook_syscalln(nr, before, after)`, `unhook_syscalln(nr, before, after)`. 32-bit compat
variants exist for each (`*_compat_syscalln`). All are static inlines over the exported
`inline_wrap_syscalln` / `fp_wrap_syscalln` and `hook_syscalln` symbols.

- `nr` — syscall number, e.g. `__NR_openat` (`#include <uapi/asm-generic/unistd.h>`).
- `narg` — number of syscall arguments.
- `before`/`after` — `void cb(hook_fargs{N}_t *args, void *udata)`, same as inline hooks; chains,
  so multiple modules can hook the same syscall.

### Prefer `hook_syscalln`

On kernels with syscall wrappers, `hook_syscalln` first installs a **single** inline hook on
`invoke_syscall` (the funnel every native and compat32 syscall passes through) and dispatches your
per-syscall registration from there — the syscall table is never modified and there is no
per-syscall timing fingerprint. If `invoke_syscall` isn't a symbol it falls back to
`el0_svc_common`, then to per-syscall `fp_`/`inline_hook_syscalln`. `syscall_hook_global_enabled()`
reports whether that global hook is active. `hook_syscalln_override` is `hook_syscalln` whose
callback may set `skip_origin` (honoured on the `invoke_syscall` path).

## Reading arguments: always use the helpers

Some kernels pass a single `pt_regs *` to syscall handlers. **Never read `args->argN` directly for
a syscall.** Use:

```c
uint64_t v = syscall_argn(args, n);        // read arg n (0-based)
set_syscall_argn(args, n, new_value);      // write arg n
```

## Overriding a syscall result

In an `after` callback: `args->ret = -EPERM;`. Or in `before`: set `args->skip_origin = 1` and set
`args->ret` (works with `hook_syscalln_override` / the fp/inline strategies).

## Minimal syscall-hook module (from demo-syscallhook, verified)

```c
#include <compiler.h>
#include <kpmodule.h>
#include <linux/printk.h>
#include <uapi/asm-generic/unistd.h>
#include <linux/uaccess.h>
#include <syscall.h>
#include <kputils.h>
#include <asm/current.h>

KPM_NAME("kpm-syscall-hook-demo");
KPM_VERSION("1.0.0");
KPM_LICENSE("GPL v2");
KPM_AUTHOR("bmax121");
KPM_DESCRIPTION("Syscall hook example");

void before_openat(hook_fargs4_t *args, void *udata)
{
    const char __user *filename = (typeof(filename))syscall_argn(args, 1);
    char buf[256];
    compat_strncpy_from_user(buf, filename, sizeof(buf));
    pr_info("openat: %s\n", buf);
}

static long init(const char *args, const char *event, void *__user reserved)
{
    // fp table hook:
    hook_err_t err = fp_hook_syscalln(__NR_openat, 4, before_openat, 0, 0);
    // or inline: inline_hook_syscalln(__NR_openat, 4, before_openat, 0, 0);
    // or auto:   hook_syscalln(__NR_openat, 4, before_openat, 0, 0);
    if (err) pr_err("hook err %d\n", err);
    return 0;
}

static long exit(void *__user reserved)
{
    fp_unhook_syscalln(__NR_openat, before_openat, 0);   // match the strategy + pointers used
    return 0;
}

KPM_INIT(init);
KPM_EXIT(exit);
```

Unhook with the **same strategy and the same before/after pointers** used to hook. Mixing them
(e.g. `inline_unhook_syscalln` for an `fp_hook_syscalln`) does not remove the hook and leaves the
kernel calling into freed memory after unload.
