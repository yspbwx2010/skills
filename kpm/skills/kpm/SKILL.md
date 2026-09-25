---
name: kpm
description: Write, build and load KernelPatch Modules (KPM) — ELF objects that KernelPatch (and APatch) load and run inside the arm64 Linux kernel to inline-hook kernel functions, hook syscalls, or call arbitrary kernel functions without kernel source. Use when creating a .kpm, writing KPM_INIT / KPM_CTL0 / KPM_EXIT callbacks, using hook_wrap / fp_hook_syscalln / inline_hook_syscalln / kallsyms_lookup_name, setting up the aarch64-none-elf build, or loading a module with sc_kpm_load / the APatch KPM screen. Triggers on "KPM", "KernelPatch module", "kpm_init", "hook_wrap", "fp_hook_syscalln", "写一个 KPM", "内核模块 hook".
license: MIT
compatibility: Building a KPM needs the aarch64-none-elf GCC toolchain (or clang --target=aarch64-none-elf) and a checkout of the KernelPatch source for its headers. KPMs run only on arm64 kernels patched by KernelPatch/APatch (Linux 3.18–6.6, CONFIG_KALLSYMS=y).
metadata:
  kernelpatch-version: "0.13.9"
---

# KernelPatch Module (KPM)

A KPM is a **partially-linked arm64 ELF relocatable object** (`.kpm`) that KernelPatch loads
and executes **in kernel space**. It is not a normal Linux `.ko` — it depends on nothing but the
symbols KernelPatch exports, so the same `.kpm` runs on many kernels without their source or
`Module.symvers`. Use a KPM to inline-hook a kernel function, hook a syscall, or reach arbitrary
kernel functions found by name at runtime.

This skill is written against **KernelPatch 0.13.9**. Everything here is verified against that
source; APIs on `main` may differ.

## Before you write anything

1. **You need the KernelPatch source** for its headers (the build `-I`s into it). Clone the release
   tag, not `main`:
   ```sh
   git clone --depth 1 --branch 0.13.9 https://github.com/bmax121/KernelPatch
   ```
   Set `KP_DIR` to that checkout (the demo Makefiles default it to `../..`).
2. **You need an arm64 bare-metal toolchain.** The upstream, CI-blessed one is
   `aarch64-none-elf-` from ARM. `clang --target=aarch64-none-elf` also works. **Not**
   `aarch64-linux-gnu-` for the link step — a KPM is `-r` partially linked, freestanding.
3. **Decide what the module does** before choosing an API: react to load/unload only (init/exit),
   answer userspace control messages (ctl0), inline-hook a function (`hook_wrap`), or hook a syscall
   (`fp_hook_syscalln` / `inline_hook_syscalln`). Read `references/api.md` for the one you need.

## Anatomy of a KPM

Every KPM is one or more `.c` files with **metadata macros** and **lifecycle callbacks**, from
`<kpmodule.h>`. This is the whole contract — the loader rejects a module that is missing the
`.kpm.info`, `.kpm.init` or `.kpm.exit` sections these macros create.

```c
#include <compiler.h>
#include <kpmodule.h>
#include <linux/printk.h>

KPM_NAME("my-module");            // required, unique, ≤ 32 bytes — the id for load/control/unload
KPM_VERSION("1.0.0");             // required, ≤ 32 bytes
KPM_LICENSE("GPL v2");            // required, ≤ 32 bytes
KPM_AUTHOR("you");                // optional, ≤ 32 bytes
KPM_DESCRIPTION("what it does");  // optional, ≤ 512 bytes

static long my_init(const char *args, const char *event, void *__user reserved)
{
    pr_info("init, event=%s args=%s\n", event, args);
    return 0;                     // non-zero => load fails, exit() is then called
}

static long my_exit(void *__user reserved)
{
    // ALWAYS undo here whatever init installed (every hook), or the kernel jumps
    // into freed memory after unload and panics.
    return 0;
}

KPM_INIT(my_init);
KPM_EXIT(my_exit);                // init and exit are mandatory; ctl0/ctl1/event are optional
```

- **`KPM_NAME` must be unique among loaded modules.** The loader refuses a second module with a
  name already present (`-EEXIST`). It is also the handle for control and unload.
- **The size limits are enforced at compile time** by `_Static_assert`. An over-long string fails
  the build, not the load.
- The string macros are the metadata; the `KPM_*` callback macros register function pointers into
  dedicated ELF sections. See `references/lifecycle.md` for the full set (init, ctl0, ctl1, exit,
  event) and their exact signatures.

## The rule that bites everyone: unhook in exit

A KPM installs hooks that point into the module's own code. When the module is unloaded its memory
is freed. **Any hook still installed then points into freed memory** — the next call panics the
kernel. So:

- For every `hook_wrap*` / `fp_hook*` / `*_hook_syscalln` in init (or ctl0), there is a matching
  `unhook*` / `fp_unhook*` / `*_unhook_syscalln` in exit.
- Remove them with the **same `before`/`after` function pointers** you registered — that pair is
  the identity of a chain entry.
- If init fails partway, it must undo what it already did before returning non-zero (the loader
  calls `exit` after a failed init, but a half-installed state is still yours to reason about).

## Build

The demo Makefiles are the canonical build. A KPM compiles each `.c` with the KernelPatch include
tree, then **partially links** (`ld -r` / `gcc -r`) the objects into `name.kpm`:

```sh
export TARGET_COMPILE=aarch64-none-elf-      # prefix; CC=${TARGET_COMPILE}gcc
export KP_DIR=/path/to/KernelPatch           # defaults to ../.. inside the repo's kpms/
make                                         # -> name.kpm
```

The include flags every KPM needs (from the demo Makefile):

```
-I$(KP_DIR)/kernel/.  -I$(KP_DIR)/kernel/include  -I$(KP_DIR)/kernel/patch/include
-I$(KP_DIR)/kernel/linux/include  -I$(KP_DIR)/kernel/linux/arch/arm64/include
-I$(KP_DIR)/kernel/linux/tools/arch/arm64/include
```

- Compile with `-O2 -fno-common`. `-fno-common` is not optional: the loader rejects LTO/common
  symbols (`__gnu_lto*`) and this is the usual cause.
- The `demo-hello` module additionally links a tiny `hello.lds` that drops `.plt`,
  `.init.plt` and `.text.ftrace_trampoline` (NOLOAD). Copy it if your link emits those sections.
- Output must stay a **relocatable ELF** (`ET_REL`), arm64, with a symbol table (not stripped).
  `references/build.md` has a ready-to-copy Makefile and the checks the loader runs on the ELF.

Use `scripts/new_kpm.py <dir> --name my-module --kp-dir /path/to/KernelPatch` to generate a
buildable skeleton (source + Makefile + lds) in an empty directory.

## Calling kernel functions (no kernel source needed)

KernelPatch exports ~113 symbols to KPMs (core, hooks, syscalls, userspace copy, su/access
control, storage, task-local, kconfig, and a large slice of `<linux/string.h>`). Anything **not**
exported you reach by address at runtime:

```c
static int (*__task_pid_nr_ns)(void *task, int type, void *ns) = 0;
static long my_init(const char *args, const char *event, void *reserved)
{
    __task_pid_nr_ns = (typeof(__task_pid_nr_ns))kallsyms_lookup_name("__task_pid_nr_ns");
    if (!__task_pid_nr_ns) return -1;   // symbol not found — bail, don't call NULL
    ...
}
```

`references/api.md` lists every exported symbol with its verified signature, grouped by header.
Do not invent an export — if it is not in that list, look it up with `kallsyms_lookup_name`.

## Loading, controlling, unloading

A `.kpm` reaches the kernel two ways:

- **Embedded at patch time** — `kptools -M module.kpm -A args -V event -T kpm` bakes it into the
  patched kernel image so it loads at boot on a chosen event (`pre-kernel-init` is the default).
  In APatch this is the "Patches" flow; the boot events are `paging-init`, `pre-kernel-init`,
  `post-kernel-init` and the init-stage events.
- **At runtime** — from userspace with the SuperCall API and the superkey:
  ```c
  #include "supercall.h"                 // from KernelPatch user/
  sc_kpm_load(key, "/data/local/tmp/my.kpm", "args", NULL);
  sc_kpm_control(key, "my-module", "ping", resp, sizeof(resp));
  sc_kpm_unload(key, "my-module", NULL);
  ```
  APatch also auto-loads any `.kpm` placed at `/data/adb/ap/kpm/<name>/<name>.kpm` (unless a
  `disable` file sits beside it) on the `post-fs-data` event, and exposes load/unload/control in
  its KPM screen.

`references/loading.md` covers the SuperCall calls, the embed flags and the APatch paths in full.

## References

Read on demand; do not load all at once.

- `references/lifecycle.md` — the five callbacks, exact signatures, `hook_fargs*_t`, `args`/`event`.
- `references/api.md` — every exported symbol and its signature, by header.
- `references/hooks.md` — inline hook (`hook_wrap`), function-pointer hook, chains, `hook_err_t`.
- `references/syscall-hook.md` — `hook_syscalln` family, `syscall_argn`, overriding return values.
- `references/build.md` — Makefile, toolchain, `.lds`, and the ELF checks the loader enforces.
- `references/loading.md` — SuperCall load/control/unload, kptools embed flags, APatch paths.
