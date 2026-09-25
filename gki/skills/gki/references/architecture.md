# GKI architecture, KMI and the symbol lists

Facts below are for OGKI `android15-6.6` built with plain Kbuild from `gki_defconfig` (Linux 6.6.118,
`KMI_GENERATION=8`, arm64). Values marked "this build" depend on the config: re-check them on your own
tree with the command given. Paths are relative to the kernel source root (`$KERNEL_SRC`) or the build
output (`$KERNEL_OUT`).

## 1. Fact table

| Item | Value in this build | Check with |
|---|---|---|
| Kernel version | 6.6.118 | `head -4 Makefile` |
| Branch / KMI generation | `android15-6.6` / **8** | `grep -E '^(BRANCH|KMI_GENERATION)=' build.config.common` |
| Kernel toolchain | clang `r510928` (LLVM 18.0.0) | `grep CLANG_VERSION build.config.constants` |
| Release string of a plain `make` build | `6.6.118-4k-g<sha>[-dirty]`, **no** `android15-8` | `cat $KERNEL_OUT/include/config/kernel.release` |
| `CONFIG_TRIM_UNUSED_KSYMS` | **not set** | `grep TRIM_UNUSED_KSYMS $KERNEL_OUT/.config` |
| `CONFIG_UNUSED_KSYMS_WHITELIST` | absent (depends on TRIM) | same file, no entry |
| Exported symbols | 16923 (`Module.symvers`) / 16405 (`vmlinux.symvers`) | `wc -l $KERNEL_OUT/*.symvers` (one symbol per line) |
| KMI symbol-list union | 9197 | command in section 4.3 |
| `CONFIG_MODULE_SIG` / `_PROTECT` / `_FORCE` | y / y / **n** | `grep MODULE_SIG $KERNEL_OUT/.config` |
| Unprotected-symbol table | **empty** (gate allows everything) | [symbols-and-signing.md](symbols-and-signing.md) |
| `CONFIG_MODVERSIONS` | y | `.config` |
| `CONFIG_CFI_CLANG` / `CONFIG_CFI_PERMISSIVE` | y / **n** (violation = Oops) | `.config`; see [cfi.md](cfi.md) |
| `CONFIG_PANIC_ON_OOPS` | y (so a CFI Oops panics) | `.config` |
| `CONFIG_LTO_NONE` | y | `.config` |
| `CONFIG_SHADOW_CALL_STACK` / `CONFIG_DYNAMIC_SCS` | y / y | `.config` |
| `CONFIG_KPROBES` / `CONFIG_KRETPROBES` | y / y | `.config` |
| `CONFIG_FUNCTION_TRACER` | **not set** (no ftrace hooks, no fprobe, no livepatch) | `.config` |
| `CONFIG_KALLSYMS_ALL` | y | `.config` |
| `CONFIG_SECURITY_LOCKDOWN_LSM` | not set | `.config` |
| `CONFIG_ANDROID_VENDOR_OEM_DATA` | y | `.config` |

In one line: a kernel you build yourself from this `gki_defconfig` does not trim symbols and has an empty
GKI symbol gate, so an unsigned out-of-tree module can use all 16923 exports. That is a property of
**your** build, not of an OEM's shipped kernel.

## 2. GKI 2.0 split

- **GKI kernel** (`vmlinux` / `Image`): built by Google per ACK branch; scheduler, mm, VFS, networking and
  everything else device-independent. A vendor may not modify it; a modified kernel is no longer GKI and
  loses certification.
- **Device code** (SoC drivers, display, modem, sensors, vendor scheduling policy): loadable modules that
  talk to the kernel only through exported symbols and vendor hooks.
- `arch/arm64/configs/gki_defconfig` is the common config; `build.config.gki` sets `DEFCONFIG=gki_defconfig`.

### What each image carries

Android platform background; the kernel tree only proves the rows that cite evidence.

| Image / partition | Carries | Evidence in the tree |
|---|---|---|
| `boot` | GKI `Image` (+ generic ramdisk; moved to `init_boot` from Android 13) | `BUILD_GKI_BOOT_IMG_SIZE=67108864` in `build.config.gki.aarch64` |
| `system_dlkm` | Google's generic GKI `.ko` (virtio, zram, tls, PPP, USB net, ...) | `BUILD_SYSTEM_DLKM=1`; list in `modules.bzl` (74 common + 4 arm64-only) |
| `vendor_boot` | vendor modules needed by first-stage init (storage, clocks, pinctrl) | none (not verified) |
| `vendor_dlkm` | all other vendor modules; updatable without touching `vendor` | none (not verified) |

### What a third-party kernel replaces

A third-party kernel normally replaces only the `Image` in `boot`. Every module in `system_dlkm`,
`vendor_boot` and `vendor_dlkm` stays as shipped and must still load against your kernel. That is the whole
compatibility problem of section 3.4.

(Inferred, not verified on device) Modules signed by the official build do not verify against the
throwaway key of your build, so your kernel treats them as unsigned; with the empty gate of this build that
changes nothing about which symbols they may use.

## 3. KMI and `KMI_GENERATION`

### 3.1 What the KMI is

The Kernel Module Interface is the stable binary interface the GKI kernel gives modules:

1. **Symbol set**: which functions/variables are exported, each with a CRC (`CONFIG_MODVERSIONS=y`).
2. **Type layouts**: size and member offsets of every type reachable from those symbols.

Part 2 is the one people forget. Two headers exist for it:

- `include/linux/android_kabi.h`: `ANDROID_KABI_RESERVE(n)` pads structs with reserved `u64` fields so a
  later member can take a slot without changing `sizeof`; `ANDROID_KABI_USE` enforces with `_Static_assert`
  that the new member is not larger or more strictly aligned than the slot.
- `include/linux/android_vendor.h`: `ANDROID_VENDOR_DATA_ARRAY` / `ANDROID_OEM_DATA_ARRAY`. With
  `CONFIG_ANDROID_VENDOR_OEM_DATA=y`, `task_struct` really contains `android_vendor_data1[64]` and
  `android_oem_data1[6]`. These are a **shared vendor/OEM convention space, not free slots for a third
  party**: stock vendor modules may already use them even if no in-tree user is visible. See
  [extending-safely.md](extending-safely.md).

### 3.2 What generation 8 means

`build.config.common` sets `KMI_GENERATION=8` and `BRANCH=android15-6.6`. The generation is the KMI's
major version inside one ACK branch:

- Within a generation Google only adds to the KMI; it does not remove or change symbols or layouts. A
  module built for the generation loads on later official kernels of the same generation.
- A breaking change bumps the generation; across generations vendors must rebuild every module.

Official GKI release strings look like `6.6.<sub>-android15-8-<build>`; the `android15-8` part is added by
Google's Kleaf release flow. A plain `make` build never produces it: you get `6.6.118` +
`CONFIG_LOCALVERSION` (`-4k` in `gki_defconfig`) + `scripts/setlocalversion` output (`-g<sha>[-dirty]`).

### 3.3 vermagic and CRCs

The loader compares vermagic (`kernel/module/main.c`; string built in `include/linux/vermagic.h`), e.g.
`6.6.118-4k-g<sha> SMP preempt mod_unload modversions aarch64`. With MODVERSIONS the release part is
skipped (`kernel/module/version.c`):

```c
int same_magic(const char *amagic, const char *bmagic, bool has_crcs)
{
	if (has_crcs) {
		amagic += strcspn(amagic, " ");   /* skip UTS_RELEASE */
		bmagic += strcspn(bmagic, " ");
	}
	return strcmp(amagic, bmagic) == 0;
}
```

So the release string does not stop a module; the **per-symbol CRC check** (`check_version()` in the same
file) does: `disagrees about version of symbol <name>`.

### 3.4 Consequence for your modules and the stock vendor modules

- Build your module against the **exact** tree, `.config` and `Module.symvers` of the kernel it will run
  on. Another config can change type layouts, hence CRCs, hence the load fails.
- Stock vendor `.ko` files were built against the OEM kernel. On your kernel each one loads only if every
  symbol it imports exists with the same CRC in your build. A changed CRC blocks exactly the modules that
  import that symbol; which modules fail must be judged per symbol, type, config and runtime semantics, not
  assumed to be "all of them".
- An equal CRC is necessary, not sufficient: it does not prove the same semantics, config-dependent
  behaviour or vendor-data slot usage. CRC and symbol checks are not a full ABI or certification gate.
- If a boot-critical vendor module fails to load, the device will likely not boot (inferred, not verified
  on device). After any kernel change run
  `dmesg | grep -iE 'disagrees about version|Unknown symbol|Protected symbol|version magic|struct module size|CFI failure'`
  on the device.

## 4. The `android/abi_gki_aarch64*` files

### 4.1 Inventory

Sizes of symbol lists in this skill are **unique symbols**, not lines:
`awk '!/^\[/ && !/^[[:space:]]*#/ && NF {print $1}' FILE | LC_ALL=C sort -u | wc -l`. A file's
`wc -l` is larger by its `[abi_symbol_list]` header, comments and duplicates: `_oplus` has 604 lines,
603 entries and 602 unique symbols (`iov_iter_advance` is listed twice).

| File | Size | Purpose |
|---|---|---|
| `abi_gki_aarch64` | 3 symbols | Main KMI list (`module_layout`, `__put_task_struct`, `utf8_data_table`). The volume is in the vendor lists. |
| `abi_gki_aarch64.stg` | 449893 lines | Full ABI description in STG format (type graph + symbol signatures); baseline for ABI diffs |
| `abi_gki_aarch64.stg.allowed_breaks` | 277 lines | Approved ABI breaks |
| `abi_gki_aarch64_type_visibility` | 4 symbols | Dummy symbols (`ANDROID_GKI_struct_dwc3`, ...) that pin types into the ABI; real `EXPORT_SYMBOL_GPL` dummies, e.g. in `drivers/usb/dwc3/core.c` |
| `abi_gki_protected_exports_aarch64` | 507 symbols | A different mechanism: symbols unsigned modules may not re-export (see [symbols-and-signing.md](symbols-and-signing.md)) |

The `aarch64_additional_kmi_symbol_lists` filegroup in `BUILD.bazel` holds 32 files: the 31
vendor/project lists below plus `_type_visibility`. Unique symbols per list: `_asus` 9, `_tcl` 10,
`_paragon` 14, `_kunit` 34, `_asr` 49, `_tuxera` 53, `_transsion` 86, `_sunxi` 100, `_fips140` 144,
`_nothing` 175, `_galaxy` 257, `_honor` 307, `_vivo` 396, `_xiaomi_wear` 415, `_nvidia` 426,
`_xiaomi` 501, `_oplus` 602, `_unisoc` 698, `_lenovo` 1362, `_exynosauto` 1472, `_virtual_device` 1490,
`_mtktv` 1853, `_db845c` 1944, `_exynos` 2365, `_pixel_watch` 2463, `_qcom` 2478, `_amlogic` 2733,
`_xiaomi_xring` 2832, `_imx` 2909, `_pixel` 3357, `_mtk` 3816.

Format: first line `[abi_symbol_list]` (`_tuxera` has none), then one indented symbol per line; `#`
starts a comment. Trap:
`abi_gki_aarch64_asus` has no trailing newline, so `cat` of several lists glues its last symbol to the
next file's header. Parse per file (the `awk` below does).

### 4.2 What they are for

In Google's Kleaf build (`BUILD.bazel`, target `kernel_aarch64`):

```
"kmi_symbol_list": "android/abi_gki_aarch64",
"additional_kmi_symbol_lists": [":aarch64_additional_kmi_symbol_lists"],
"trim_nonlisted_kmi": True,
"kmi_symbol_list_strict_mode": True,
"protected_exports_list": "android/abi_gki_protected_exports_aarch64",
```

- Union of the main list and all additional lists = every KMI symbol of the generation; it is fed to
  `CONFIG_UNUSED_KSYMS_WHITELIST`.
- `trim_nonlisted_kmi` drops exports not in the union (mechanism: [symbols-and-signing.md](symbols-and-signing.md)).
- `kmi_symbol_list_strict_mode` fails the build if the exported set and the lists disagree.

A vendor needing a new symbol edits its list, submits it to ACK, and gets it in a later GKI release. List
size is a rough measure of a vendor's dependence on the GKI.

### 4.3 Measured counts (this build, including in-tree modules)

| Set | Count |
|---|---|
| KMI list union (main list + the 32 filegroup files) | 9197 |
| Exported, `Module.symvers` (vmlinux + in-tree modules) | 16923 |
| Exported, `vmlinux.symvers` (vmlinux only) | 16405 |
| Union ∩ `Module.symvers` | 9197 (every listed symbol is exported) |
| `Module.symvers` − union | 7726 |
| Union − `vmlinux.symvers` | 217 (exported by in-tree modules, not by vmlinux) |

- The union is a property of the list files. It is the same number whichever symvers file you compare it
  with; a different union count means a parsing difference, not a symvers choice.
- "Exported − union" is **not** the number an official build trims. Trimming also keeps symbols used by
  in-tree modules, and the official build's config and module set can differ. Read 7726 only as "about
  7.7k exports here are outside the KMI lists".

Recompute:

```sh
awk '!/^\[/ && !/^[[:space:]]*#/ && NF {print $1}' \
    "$KERNEL_SRC"/android/abi_gki_aarch64 "$KERNEL_SRC"/android/abi_gki_aarch64_* \
  | LC_ALL=C sort -u > kmi.txt                       # 9197 here
awk '{print $2}' "$KERNEL_OUT"/Module.symvers | LC_ALL=C sort -u > exported.txt
LC_ALL=C comm -23 exported.txt kmi.txt | wc -l       # exported but not in the KMI lists
```

The glob `abi_gki_aarch64_*` matches exactly the 32 filegroup files in this tree; on another tree, compare
it with the `aarch64_additional_kmi_symbol_lists` filegroup in `BUILD.bazel`.
