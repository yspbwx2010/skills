# The three metamodule hooks

Verified against KernelSU `ksud` (`src/metamodule.rs`, `src/module.rs`) and the official metamodule
guide. All three are optional and live in the metamodule's directory; each runs in the manager's
BusyBox `ash`. Begin each with `MODDIR="${0%/*}"`.

## metamount.sh — mount backend

Runs at boot to mount all enabled modules systemlessly. The heart of a metamodule.

- **Env**: `MODULE_DIR` = the modules root (`/data/adb/modules`); `MODDIR` = the metamodule's own
  dir; plus the common env (`KSU=true`, `KSU_VER`, `KSU_VER_CODE`, `KSU_MODULE`, `ASH_STANDALONE=1`,
  a `PATH` that includes busybox). On APatch: `APATCH=true`, `APATCH_VER`, … instead.
- **Honor markers**: skip a module dir that has a `disable` or `skip_mount` file.
- 🔴 **Set the mount source to `"KSU"`** on every mount. Shell:
  `mount -t overlay -o lowerdir=…,upperdir=…,workdir=… KSU /target` or `mount -o bind,dev=KSU src dst`.
  New mount API: `fsconfig_set_string(fs, "source", "KSU")`. KernelSU's kernel umount and zygisk
  umount locate KernelSU mounts by this source; a wrong/missing source leaks mounts.
- **Blocking at boot** — a failure or hang here can bootloop. Don't abort the whole script on one
  module; log and continue.

```sh
#!/system/bin/sh
MODDIR="${0%/*}"
for module in "$MODULE_DIR"/*; do
    [ -f "$module/disable" ] && continue
    [ -f "$module/skip_mount" ] && continue
    [ -d "$module/system" ] || continue
    mount -o bind,dev=KSU "$module/system" /system   # source MUST be KSU
done
```

## metainstall.sh — customize regular-module installation

**Sourced** (not executed) by the built-in installer during a *regular* module's install, after the
zip is extracted — same mechanism as `customize.sh`. **Not** run when installing the metamodule
itself, and skipped while the metamodule is `disable`d (the default installer is used then).

- Inherits the installer's variables: `MODPATH`, `TMPDIR`, `ZIPFILE`, `ARCH`, `API`, `IS64BIT`,
  `BOOTMODE`, `KSU`, `KSU_VER`, `KSU_VER_CODE`, `KSU_UAPI_VER`, `KSU_RUNTIME_MODE`, `KSU_LATE_LOAD`, …
- Inherits the installer's functions: `ui_print <msg>`, `abort <msg>`, `set_perm …`,
  `set_perm_recursive …`, and **`install_module`** — run the built-in install step. Call it when
  ready (e.g. after relocating files into your own store).

```sh
# metainstall.sh — sourced during a regular module install
ui_print "- Installing via meta-example"
install_module            # run the built-in installer
# then move $MODPATH/system into your store, set up your mount metadata, etc.
```

## metauninstall.sh — clean up on regular-module removal

Runs when a *regular* module is uninstalled, before its directory is deleted.

- **Env**: `MODULE_ID` — the id of the module being removed. **Read `$MODULE_ID`, not `$1`.** `ksud`
  (and APatch's `apd`) pass the id as the `MODULE_ID` environment variable with no positional
  argument, so `MODULE_ID="$1"` — which one version of the official example shows — sets it empty.

```sh
#!/system/bin/sh
# MODULE_ID is an env var, not $1
IMG_MNT="/data/adb/metamodule/mnt"
[ -n "$MODULE_ID" ] && rm -rf "$IMG_MNT/$MODULE_ID"
```

## Which hook for what

| Goal | Hook |
| --- | --- |
| Mount modules a different way (overlayfs / magic mount / FUSE / none) | `metamount.sh` |
| Store module files somewhere custom, or gate what installs | `metainstall.sh` (call `install_module`) |
| Tear down what `metainstall.sh` set up, per module | `metauninstall.sh` |

A metamodule may also ship the ordinary lifecycle scripts (`post-fs-data.sh`, `post-mount.sh`,
`service.sh`, `boot-completed.sh`, `customize.sh`); they run at their normal stages, before regular
modules' (see `references/execution.md`).
