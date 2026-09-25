# Module zip and install-time customization

Verified against APatch 11224 (`apd/assets/installer.sh`, `apd/src/module.rs`).

## Zip format

```
module.zip
├── module.prop      # required
├── customize.sh     # optional — sourced by the installer after extraction
├── system/...       # optional overlay tree
├── *.sh             # optional boot scripts (service.sh, post-fs-data.sh, ...)
└── ...              # any other module files
```

Flashed from the APatch manager. **Cannot be installed from recovery.**

## Install order (default installer)

1. Extract `module.prop`; abort if missing.
2. Read `id` (validated against `^[a-zA-Z][a-zA-Z0-9._-]+$`), `name`, `author`.
3. Extract `customize.sh`. If it does **not** contain a line `SKIPUNZIP=1`, extract the whole zip
   (minus `META-INF/`) into `$MODPATH`.
4. Source `customize.sh` (if present).
5. Apply `REPLACE` and `REMOVE` lists (see `references/systemless.md`).
6. Set default permissions and finalize into `/data/adb/modules/<id>/`.

`SKIPUNZIP=1` in `customize.sh` skips step 3's extraction — you then unpack and set permissions
yourself.

## customize.sh variables

Bool values are the strings `true`/`false`.

| Variable | Meaning |
| --- | --- |
| `MODPATH` | the module's install dir |
| `TMPDIR` | scratch dir |
| `ZIPFILE` | path to the flashed zip |
| `ARCH` | CPU arch — **always `arm64`** on APatch |
| `IS64BIT` | 64-bit device? |
| `API` | Android API level (e.g. `33`) |
| `BOOTMODE` | `true` when flashed from the running system (always the case in the manager) |
| `OUTFD` | fd for `ui_print` output |
| `APATCH` | `true` |
| `APATCH_VER` / `APATCH_VER_CODE` | manager version name / code |
| `KERNELPATCH` | `true` |
| `KERNELPATCH_VERSION` | KernelPatch version (hex, e.g. `a05` = 0.10.5) |
| `KERNEL_VERSION` | kernel version (hex, e.g. `50a01` = 5.10.1) |
| `SUPERKEY` | the superkey (needed to call `kpatch`/supercall) — treat as a secret |
| `MAGISK_VER` / `MAGISK_VER_CODE` | compatibility shim; **read, don't hardcode** (30.0 / 30000 in 11224, was 27.0 / 27000 in older docs) |

## customize.sh functions

```
ui_print <msg>                 # print to the manager console (not `echo`)
abort <msg>                    # print and abort the install (not `exit`)
set_perm <target> <owner> <group> <perm> [context]
set_perm_recursive <dir> <owner> <group> <dirperm> <fileperm> [context]
```

Default SELinux context when omitted is `u:object_r:system_file:s0`.

## Skeleton customize.sh

```sh
#!/system/bin/sh
# APATCH is "true" here; ARCH is always arm64.
ui_print "- Installing My Module for API $API"
[ "$API" -lt 29 ] && abort "! Android 10+ required"

# Systemless deletes/replaces (APatch runs the mknod/setfattr for you):
REMOVE="
/system/app/Bloatware
"
REPLACE="
/system/app/SomeDir
"

set_perm_recursive "$MODPATH" 0 0 0755 0644
```

Keep it POSIX `ash`-compatible (busybox standalone mode). For a Magisk/KernelSU module, the same
`customize.sh` contract mostly applies — the differences are `ARCH` (arm64 only), the `APATCH`
env var, and no Zygisk.
