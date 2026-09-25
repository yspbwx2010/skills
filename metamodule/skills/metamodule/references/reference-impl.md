# Reference implementation: meta-overlayfs

`meta-overlayfs` is KernelSU's official metamodule — traditional overlayfs mounting with ext4-image
storage. Study it as the model for a real metamodule. (Facts from the official metamodule guide;
the mount binary lives in the separate `meta-overlayfs` repo.)

## Dual-directory architecture

`meta-overlayfs` splits metadata from content:

1. **Metadata** — `/data/adb/modules/<id>/`: `module.prop`, `disable`, `skip_mount` markers only.
   Small and fast to scan at boot.
2. **Content** — `/data/adb/metamodule/mnt/`: the actual `system/` (and `vendor`, `product`,
   `system_ext`, `odm`, `oem`) trees, stored inside an ext4 image (`modules.img`) mounted at boot.

This keeps `/data/adb/modules` tiny while the bulky files live in a space-efficient image. It moves
the files there in `metainstall.sh` (via `install_module` + a relocation) and removes them in
`metauninstall.sh` (keyed by `$MODULE_ID`).

## metamount.sh shape

```sh
#!/system/bin/sh
MODDIR="${0%/*}"
IMG_FILE="$MODDIR/modules.img"
MNT_DIR="$MODDIR/mnt"

if ! mountpoint -q "$MNT_DIR"; then
    mkdir -p "$MNT_DIR"
    mount -t ext4 -o loop,rw,noatime "$IMG_FILE" "$MNT_DIR"
fi

export MODULE_METADATA_DIR="/data/adb/modules"
export MODULE_CONTENT_DIR="$MNT_DIR"

"$MODDIR/meta-overlayfs"        # native binary does the overlay mounts
```

The native binary overlays each partition and sets the overlay source to `KSU`
(`fsconfig_set_string(fs, "source", "KSU")`) — the required tag (see `references/hooks.md`). It
supports a read-write layer via `/data/adb/modules/.rw/`.

## A minimal metamodule (no native binary)

If you don't need overlayfs, a bind-mount `metamount.sh` alone is a complete metamodule — plus
`module.prop` with `metamodule=1`:

```sh
#!/system/bin/sh
MODDIR="${0%/*}"
for m in "$MODULE_DIR"/*; do
    [ -f "$m/disable" ] || [ -f "$m/skip_mount" ] && continue
    [ -d "$m/system" ] && mount -o bind,dev=KSU "$m/system" /system
done
```

(bind mounts don't merge directories the way overlayfs does — fine for whole-file overrides, not for
adding files into an existing system dir. For real systemless behaviour, overlay or magic mount.)

## Checklist before releasing a metamodule

- `module.prop` has `metamodule=1` and an id starting `meta-`.
- Every mount uses source `"KSU"`.
- `metamount.sh` honors `disable` and `skip_mount`, and never aborts the whole boot on one module.
- `metauninstall.sh` reads `$MODULE_ID` (not `$1`).
- Tested: clean install, mounting several module types, uninstall/cleanup, and boot performance
  (`metamount.sh` is blocking). A mount error must not bootloop the device.
