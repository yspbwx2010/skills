# Systemless /system changes

Verified against APatch 11224 (`docs/cn/ap_module.md`, `apd/assets/installer.sh`).

APatch's systemless mechanism is the kernel's **overlayfs** — different from Magisk's magic
(bind) mount, same goal: change `/system` without writing the real partition.

## Adding / overriding files

Put files under your module's `system/` mirroring the target path. At boot APatch overlays it on
`/system`:

- A same-path **file** in your `system/` overrides the system file.
- A same-path **directory** merges with the system directory.

```
system/
└── etc/
    └── hosts            # overrides /system/etc/hosts
```

## Deleting a system file (whiteout)

You cannot delete by omission. Create a character-device whiteout so overlayfs hides the file:

- Manually: `mknod <path> c 0 0` inside your module tree at the target path.
- Or declare in `customize.sh`:
  ```sh
  REMOVE="
  /system/app/YouTube
  /system/app/Bloatware
  "
  ```
  APatch runs `mknod $MODPATH/system/app/YouTube c 0 0` etc. Those paths then appear deleted while
  the real `/system` is untouched.

## Replacing (not merging) a directory

To make a system directory appear **replaced** by yours (empty or with only your files), set the
overlay opaque attribute:

- Manually: `setfattr -n trusted.overlay.opaque -v y <dir>`.
- Or declare in `customize.sh`:
  ```sh
  REPLACE="
  /system/app/YouTube
  "
  ```
  APatch creates `$MODPATH/system/app/YouTube` and sets the opaque attr; the system's version is
  replaced by your (possibly empty) dir when the module is active.

## system.prop

Same format as `build.prop`, one `key=value` per line. Applied at boot via `resetprop`.

```
ro.example.flag=1
```

## sepolicy.rule

Extra SELinux policy statements, one per line, loaded at boot (APatch uses Magisk's
`magiskpolicy`). Add rules here when your module's daemon/binary needs permissions the base policy
denies. Example:

```
allow untrusted_app_all system_file file { read open getattr }
```

Keep rules minimal — every added allow widens the attack surface of a rooted device.
