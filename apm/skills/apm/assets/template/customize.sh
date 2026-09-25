#!/system/bin/sh
# Sourced by the APatch installer after the zip is extracted to $MODPATH.
# APATCH="true" here; ARCH is always "arm64". Use ui_print / abort, not echo / exit.

ui_print "- Installing __NAME__"

# Require a minimum Android API if needed:
# [ "$API" -lt 29 ] && abort "! Android 10+ required"

# Systemless deletes/replaces (APatch performs the mknod/setfattr for you):
# REMOVE="
# /system/app/Bloatware
# "
# REPLACE="
# /system/app/SomeDir
# "

set_perm_recursive "$MODPATH" 0 0 0755 0644
