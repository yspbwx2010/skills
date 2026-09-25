#!/system/bin/sh
# Mount backend: runs at boot, after all post-fs-data scripts. BLOCKING — keep it fast and crash-free.
# Env: MODULE_DIR (the modules root), MODDIR (this metamodule's dir), plus KSU_*/APATCH_* vars.
MODDIR="${0%/*}"

for module in "$MODULE_DIR"/*; do
    [ -f "$module/disable" ] && continue
    [ -f "$module/skip_mount" ] && continue
    [ -d "$module/system" ] || continue
    # Every mount MUST use source/device name "KSU" so the kernel/zygisk umount can find it.
    mount -o bind,dev=KSU "$module/system" /system
done
