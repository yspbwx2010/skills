# CFI (KCFI) and callback function pointers

Facts are for OGKI `android15-6.6` (Linux 6.6.118, `gki_defconfig`, clang r510928 / LLVM 18). Re-check the
config lines on your build: `grep -E 'CFI|PANIC_ON_OOPS|LTO_NONE|SHADOW_CALL|DYNAMIC_SCS' "$KERNEL_OUT"/.config`.

## 1. Config and what a violation does

```
CONFIG_CFI_CLANG=y
# CONFIG_CFI_PERMISSIVE is not set
CONFIG_LTO_NONE=y
CONFIG_PANIC_ON_OOPS=y
```

The top-level `Makefile` adds `-fsanitize=kcfi` to `KBUILD_CFLAGS` when `CONFIG_CFI_CLANG=y`. That
variable also applies to `M=` external module builds: your module is KCFI-instrumented automatically. Do
not add the flag by hand, and do not remove it.

Without `CFI_PERMISSIVE` a violation is fatal:

1. clang compiles a failed check into a `BRK`; `arch/arm64/kernel/traps.c` (`cfi_handler`) catches it;
2. `report_cfi_failure()` (`kernel/cfi.c`) logs and, permissive being off, returns `BUG_TRAP_TYPE_BUG`;
3. `traps.c` calls `die("Oops - CFI", ...)`; with `CONFIG_PANIC_ON_OOPS=y` the Oops panics the kernel.

Log line: `CFI failure at <caller> (target: <callee>; expected type: 0x........)`.

## 2. How KCFI works

- The compiler places a 32-bit type hash in the 4 bytes before the entry of each function that may be
  called indirectly (`cfi_get_offset()` returns 4 in `include/linux/cfi.h`).
- Every indirect call site loads those 4 bytes from the target and compares them with the hash of the
  pointer type it calls through. Mismatch: `BRK`.
- The hash is derived from the **full C function type**: return type and every parameter type.
  `int (*)(void *, int)` and `int (*)(void *, long)` hash differently even though arm64 passes both the
  same way. `struct pt_regs *` vs `void *` differ; so do `const char *` vs `char *`.
- KCFI needs no LTO (this build is `CONFIG_LTO_NONE=y`): calls across translation units **and across the
  module boundary** are checked.

The check sits at the **call site**. When the kernel calls your callback, the kernel's call site does the
check; nothing you put on your own function can switch it off.

## 3. Four hard rules

### Rule 1: a callback's prototype matches the caller's declared type exactly

Vendor hooks are called in `include/linux/tracepoint.h` (`__traceiter_##_name`), restricted hooks in the
same shape in `include/trace/hooks/vendor_hooks.h`:

```c
((void(*)(void *, proto))(it_func))(__data, args);
```

The target must hash as `void (*)(void *, <TP_PROTO expanded>)`. `register_trace_<name>()` takes a
strongly typed `void (*probe)(data_proto)`, so a wrong prototype is a compile error, not a runtime panic.
Without casts, vendor hooks are CFI-safe. Hook details: [vendor-hooks.md](vendor-hooks.md).

### Rule 2: never cast a function pointer to silence the compiler

```c
/* WRONG: builds, then die("Oops - CFI") on the first call */
static void my_cb(void *data, struct cpufreq_policy *p, unsigned int *f)   /* one parameter short */
{
}
register_trace_android_vh_cpufreq_target(
	(void (*)(void *, struct cpufreq_policy *, unsigned int *, unsigned int))my_cb, NULL);

/* RIGHT: copy the prototype from the hook declaration; no cast */
static void my_cb(void *data, struct cpufreq_policy *p, unsigned int *f, unsigned int old)
{
}
register_trace_android_vh_cpufreq_target(my_cb, NULL);
```

The cast only silences the compiler; `my_cb`'s hash is still computed from its own prototype. If a
function pointer seems to need a cast, the prototype is wrong: fix the prototype. The same applies to any
detour through `void *` or `unsigned long` and back.

### Rule 3: copy the declared type when filling a struct's function-pointer field

`struct notifier_block.notifier_call` is `notifier_fn_t` (`include/linux/notifier.h`):

```c
typedef int (*notifier_fn_t)(struct notifier_block *nb, unsigned long action, void *data);

static int wrong_cb(struct notifier_block *nb, int action, void *data);            /* int != unsigned long */
static int right_cb(struct notifier_block *nb, unsigned long action, void *data);
```

In this build `wrong_cb` in `.notifier_call = wrong_cb` fails to compile: Kbuild passes
`-Werror=incompatible-pointer-types` (`scripts/Makefile.extrawarn`) and `CONFIG_WERROR=y` adds `-Werror`
(clang 16+ also makes incompatible function-pointer types an error by default). The runtime panic only
happens when a cast or a `void *` hop hides the mismatch. Treat any function-pointer diagnostic as a
prototype bug; never add `-Wno-...` for it.

### Rule 4: there is no per-callback opt-out

- `__nocfi` is **not** an empty macro when CFI is on: with a KCFI-capable clang,
  `include/linux/compiler-clang.h` defines it as `__attribute__((__no_sanitize__("kcfi")))`. It disables
  checks only on indirect calls **made inside** the annotated function. The empty fallback in
  `include/linux/compiler_types.h` applies only to compilers without KCFI.
- It cannot rescue a mismatched callback: the failing check is in the kernel's caller, not in your
  function. Do not use it to call arbitrary addresses either; it removes the check, not the mismatch.
- `CFI_NOSEAL()` is empty on arm64 (`include/linux/cfi.h`); only x86 implements it.

The only fix is a correct prototype.

(Inferred, not verified) A `static` function whose address is never taken may be emitted without a type
hash. Calling it through an address found with kallsyms would then trap however exact the prototype is.
Safe practice: use kallsyms-derived addresses only to **read data**; to run code at a function, attach a
kprobe to it ([choosing-a-path.md](choosing-a-path.md)).

## 4. Shadow call stack

`CONFIG_SHADOW_CALL_STACK=y` with `CONFIG_DYNAMIC_SCS=y` (selected by `CONFIG_UNWIND_PATCH_PAC_INTO_SCS=y`)
in this build:

- `arch/arm64/Makefile` adds `-ffixed-x18` to all C, `M=` modules included. x18 holds the shadow stack
  pointer: **never touch x18 in inline assembly**, or you corrupt return addresses.
- With dynamic SCS the top-level `Makefile` does **not** add `-fsanitize=shadow-call-stack`. Code is built
  with `-mbranch-protection=pac-ret` and unwind tables, and on CPUs without pointer authentication the
  kernel rewrites the PAC instructions into shadow-stack push/pop at boot, and for modules at load time
  (`scs_patch()` over `.init.eh_frame` in `arch/arm64/kernel/module.c`). Let Kbuild choose these flags.

## 5. Checklist for every callback

1. Find the typedef or field type the kernel calls through; copy its prototype character for character.
2. No casts on function pointers, and no `void *` / integer detours.
3. The build is `-Werror`: any function-pointer diagnostic means the prototype is wrong.
4. Exercise every callback path at least once on the target. The panic happens only when the kernel
   actually calls the callback, not at load time.
