# Inline and function-pointer hooks

From `<hook.h>`. Verified against KernelPatch 0.13.9.

## Which hook to use

- **`hook_wrap` (chain, recommended).** Wrap a function with a `before` and/or `after` callback.
  Multiple modules can wrap the same function safely; removable independently. Use this by default.
- **`hook` (simple).** One replacement function + backup pointer. **Not chain-safe** — if two
  modules `hook` the same function, unloading one corrupts the other. The header itself says: use
  `hook_wrap` instead. Only use `hook` when you truly need to replace, not observe.
- **`fp_hook_wrap` / `fp_hook`.** Same idea but you hook a **function-pointer slot** (e.g. an entry
  in an ops table) by its address, rather than a function body.

## `hook_err_t`

```c
HOOK_NO_ERR = 0
HOOK_BAD_ADDRESS   = 4095   // func addr rejected (NULL / unmapped / bad)
HOOK_DUPLICATED    = 4094   // this before/after pair is already registered on the func
HOOK_NO_MEM        = 4093
HOOK_BAD_RELO      = 4092
HOOK_TRANSIT_NO_MEM= 4091
HOOK_CHAIN_FULL    = 4090   // 16 items already on this function (HOOK_CHAIN_NUM = 0x10)
```

Always check the return of a hook-install call; `0` means installed.

## `hook_wrap` — chain hook

```c
hook_err_t hook_wrap(void *func, int32_t argno, void *before, void *after, void *udata);
void       hook_unwrap(void *func, void *before, void *after);   // inline over hook_unwrap_remove

// Typed convenience wrappers, argno baked in (recommended — they type the callbacks):
hook_err_t hook_wrap2(void *func, hook_chain2_callback before,
                      hook_chain2_callback after, void *udata);
// hook_wrap0 .. hook_wrap12 exist; callback type is hook_chain{N}_callback.
```

Callback: `void cb(hook_fargs{N}_t *args, void *udata)`. Field layout is in
`references/lifecycle.md`. In a `before` you may modify `args->argN`, set `args->skip_origin = 1`
to skip the original (then set `args->ret`), or stash state in `args->local.dataN` for the `after`.
In an `after` you read/override `args->ret`.

### Chain semantics (multiple wrappers on one function)

```
before[0] → before[1] → … → before[N-1]
    → original  (skipped if any before set skip_origin = 1)
        → after[N-1] → … → after[0]
```

- `before` runs in insertion order, `after` in reverse.
- `args` is shared across all items on the call; `args->local` is shared too — use **`udata`** for
  per-item private state, not `local`.
- Same `(before, after)` pair twice ⇒ `HOOK_DUPLICATED`. Max 16 items ⇒ `HOOK_CHAIN_FULL`.
- No cross-module ordering guarantee.

## Minimal inline-hook module (from demo-inlinehook, verified)

```c
#include <log.h>
#include <compiler.h>
#include <kpmodule.h>
#include <hook.h>
#include <linux/printk.h>

KPM_NAME("kpm-inline-hook-demo");
KPM_VERSION("1.0.0");
KPM_LICENSE("GPL v2");
KPM_AUTHOR("bmax121");
KPM_DESCRIPTION("Inline hook example");

int __noinline add(int a, int b) { return a + b; }   // __noinline: a hook needs a real body

void before_add(hook_fargs2_t *args, void *udata) {
    logkd("before add: %d + %d\n", (int)args->arg0, (int)args->arg1);
}
void after_add(hook_fargs2_t *args, void *udata) {
    args->ret = 100;                                  // override return value
}

static long init(const char *args, const char *event, void *__user reserved) {
    hook_err_t err = hook_wrap2((void *)add, before_add, after_add, 0);
    logkd("hook err: %d\n", err);
    return 0;
}
static long exit(void *__user reserved) {
    unhook((void *)add);                              // or hook_unwrap for a wrap; see note
    return 0;
}
KPM_INIT(init);
KPM_EXIT(exit);
```

Note: the demo uses `unhook()` in exit; for a `hook_wrap` the precise inverse is
`hook_unwrap((void *)add, before_add, after_add)`. Use `unhook` only for the simple `hook`.

## Hooking a function you don't have the address of

For a kernel function, get its address first:

```c
void *fp = (void *)kallsyms_lookup_name("do_something");
if (!fp) return -1;                       // not found — do not hook NULL
hook_err_t err = hook_wrap4(fp, before, after, 0);
```

## `fp_hook_wrap` — function-pointer slot hook

```c
hook_err_t fp_hook_wrap(uintptr_t fp_addr, int32_t argno, void *before, void *after, void *udata);
void       fp_hook_unwrap(uintptr_t fp_addr, void *before, void *after);
```

`fp_addr` is the **address of the pointer variable** (e.g. `&some_ops->read`), not the function.
Same callback types and chain semantics as `hook_wrap`.

## Undo, always

Every install in init/ctl0 has a matching removal in exit, with the **same before/after pointers**.
A hook left installed at unload points into freed module memory and panics the kernel.
