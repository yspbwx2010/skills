#!/system/bin/sh
# Sourced by the APatch / KernelSU installer after the zip is extracted to $MODPATH.
# APATCH="true" or KSU="true" tells you which; ARCH is "arm64" on these devices. Use ui_print / abort, not echo / exit.

ui_print "- Installing __NAME__"

# Require a minimum Android API if needed:
# [ "$API" -lt 29 ] && abort "! Android 10+ required"

# Systemless deletes/replaces. These only take effect if a mounting metamodule is installed;
# on KernelSU, REPLACE also needs a metamodule that defines mark_replace (meta-overlayfs does):
# REMOVE="
# /system/app/Bloatware
# "
# REPLACE="
# /system/app/SomeDir
# "

set_perm_recursive "$MODPATH" 0 0 0755 0644
