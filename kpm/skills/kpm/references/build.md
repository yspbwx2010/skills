# Building a KPM

Verified against KernelPatch 0.13.9. A KPM is a **partially-linked arm64 ELF relocatable object**.

## Toolchain

- Upstream/CI standard: `aarch64-none-elf-` GCC (ARM GNU bare-metal toolchain, CI pins 12.2.rel1).
  Set `TARGET_COMPILE=aarch64-none-elf-`; the Makefile uses `CC=${TARGET_COMPILE}gcc`.
- `clang --target=aarch64-none-elf` also compiles a KPM (with LLVM `ld.lld`).
- **Do not** link with `aarch64-linux-gnu-` in hosted mode — a KPM is freestanding and `-r`
  partially linked.
- You also need the **KernelPatch source checkout** for headers. Clone the release tag:
  `git clone --depth 1 --branch 0.13.9 https://github.com/bmax121/KernelPatch`, and point
  `KP_DIR` at it.

## Makefile (canonical, from the demo modules)

```make
ifndef TARGET_COMPILE
    $(error TARGET_COMPILE not set)
endif
ifndef KP_DIR
    KP_DIR = ../..
endif

CC = $(TARGET_COMPILE)gcc

INCLUDE_DIRS := . include patch/include linux/include \
                linux/arch/arm64/include linux/tools/arch/arm64/include
INCLUDE_FLAGS := $(foreach dir,$(INCLUDE_DIRS),-I$(KP_DIR)/kernel/$(dir))

objs := mymod.o

all: mymod.kpm

mymod.kpm: ${objs}
	${CC} -r -o $@ $^                              # partial link => relocatable .kpm

%.o: %.c
	${CC} $(CFLAGS) $(INCLUDE_FLAGS) -c -O2 -o $@ $<

.PHONY: clean
clean:
	rm -rf *.kpm
	find . -name "*.o" | xargs rm -f
```

Build: `export TARGET_COMPILE=aarch64-none-elf- KP_DIR=/path/to/KernelPatch && make`.

## Flags that matter

- `-O2` and `-c` per object, then `${CC} -r -o out.kpm objs...` to partially link. The `.kpm` is
  the **relocatable** object, not a fully linked executable.
- **`-fno-common`.** The loader rejects LTO/common symbols; a symbol landing in `SHN_COMMON` named
  `__gnu_lto*` aborts the load (`Please compile with -fno-common`). Add `-fno-common` if your
  toolchain defaults otherwise.
- **Do not strip.** The loader requires a symbol table (`SHT_SYMTAB`); a stripped module fails with
  `module has no symbols (stripped?)`.
- Some links emit `.plt`, `.init.plt`, `.text.ftrace_trampoline`. `demo-hello` drops them with a
  linker script (`-T hello.lds`):
  ```
  SECTIONS {
      .plt (NOLOAD) : { BYTE(0) }
      .init.plt (NOLOAD) : { BYTE(0) }
      .text.ftrace_trampoline (NOLOAD) : { BYTE(0) }
  }
  ```
  Add it if `llvm-readelf -S out.kpm` shows those sections carrying content.

## What the loader checks (so build to satisfy it)

From `patch/module/module.c`:

1. ELF header: `ET_REL`, arm64 (`elf_check_arch`), `e_shentsize == sizeof(Elf_Shdr)`, valid section
   headers. → else "not a supported AArch64 relocatable module".
2. Sections `.kpm.info`, `.kpm.init`, `.kpm.exit` must exist (the metadata + init + exit macros).
3. `name` and `version` present in `.kpm.info`.
4. A `SHT_SYMTAB` present (not stripped).
5. Every undefined symbol must resolve to a **KernelPatch export** (`symbol_lookup_name`), not an
   arbitrary kernel symbol — an unknown one fails with `unknown symbol: <name>`. Reach non-exported
   kernel functions at runtime via `kallsyms_lookup_name` (see `references/api.md`).
6. Unique `KPM_NAME` among loaded modules (else `-EEXIST` at load).

Verify locally before shipping:

```sh
llvm-readelf -h out.kpm | grep -E 'Type|Machine'      # Type: REL (Relocatable), Machine: AArch64
llvm-readelf -S out.kpm | grep -E '\.kpm\.(info|init|exit)|SYMTAB'
```
