# Systemless /system changes

Verified against APatch 11224 (`apd/src/event.rs`, `apd/src/metamodule.rs`, `apd/assets/installer.sh`),
KernelSU v3.3.1 (`userspace/ksud/src/init_event.rs`, `metamodule.rs`, `installer.sh`) and
`meta-overlayfs` 1.3.1 (`metamodule/metainstall.sh`, `metamount.sh`).

## Who mounts `system/`

Neither manager mounts modules itself any more. KernelSU removed its built-in overlayfs mount in
v3.0.0 (PR #2929, "support metamodule, remove built-in overlayfs mount"); APatch removed its built-in
mount and magic-mount code in PR #1356 ("After this commit, APatch will NOT process module mount"),
which 11224 includes. At boot the manager runs the active **metamodule**'s `metamount.sh` with
`MODULE_DIR` set; that script mounts the enabled modules (or doesn't).

- **No metamodule → nothing is mounted.** KernelSU's own guide says so: "Without a metamodule
  installed, modules will NOT be mounted."
- The semantics below (override, merge, whiteout, opaque) are **overlayfs** semantics, which is what
  `meta-overlayfs` (KernelSU's reference metamodule) gives. Another metamodule (magic mount, FUSE,
  none) may treat whiteouts and opaque dirs differently; check the one your users run.
- `meta-overlayfs` copies each module's `system/ vendor/ product/ system_ext/ odm/ oem/` into its ext4
  image `/data/adb/metamodule/modules.img` at install (skipped for modules with `skip_mount` or no
  `system/`), and mounts from there. The copy under `/data/adb/modules/<id>/` stays, but editing it at
  runtime does not change what is mounted; reinstall the module instead.
- Mount order relative to scripts differs: APatch mounts **before** module `post-fs-data.sh`;
  KernelSU mounts **after** it (and after `system.prop`). See [scripts.md](scripts.md).

## Adding / overriding files

Put files under your module's `system/` mirroring the target path. At boot an overlayfs-style
metamodule overlays it on `/system`:

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
  Both installers run `mknod $MODPATH/system/app/YouTube c 0 0` etc. (`mark_remove`). Under an
  overlayfs metamodule those paths then appear deleted while the real `/system` is untouched.

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
  APatch's installer defines `mark_replace` and creates `$MODPATH/system/app/YouTube` with the
  opaque attr; the system's version is replaced by your (possibly empty) dir when the module is active.

  **KernelSU v3.x:** `installer.sh` still loops over `REPLACE` and calls `mark_replace`, but the
  function definition was removed with the built-in mount in v3.0.0. It exists only if the active
  metamodule's `metainstall.sh` defines it before calling `install_module` (`meta-overlayfs` does,
  with the same `setfattr`). With no such metamodule the call fails (`mark_replace: not found`,
  inferred from the shell; not run on a device). If REPLACE matters, set the opaque attr yourself in
  `customize.sh` (`mkdir -p "$MODPATH/system/app/YouTube" && setfattr -n trusted.overlay.opaque -v y "$MODPATH/system/app/YouTube"`), which
  works under either manager with an overlayfs metamodule.

## system.prop

Same format as `build.prop`, one `key=value` per line. Applied at boot via `resetprop`.

```
ro.example.flag=1
```

## sepolicy.rule

Extra SELinux policy statements, one per line, loaded at boot by the manager itself (not by the
metamodule), before `metamount.sh` runs (APatch uses Magisk's `magiskpolicy`). Add rules here when your module's daemon/binary needs permissions the base policy
denies. Example:

```
allow untrusted_app_all system_file file { read open getattr }
```

Keep rules minimal — every added allow widens the attack surface of a rooted device.
