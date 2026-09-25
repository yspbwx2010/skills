#!/system/bin/sh
# Runs when a regular module is uninstalled, before its dir is removed.
# The module id arrives as the env var MODULE_ID (NOT $1).
[ -n "$MODULE_ID" ] || exit 0
# Example: drop this module's files from your store
# rm -rf "/data/adb/metamodule/mnt/$MODULE_ID"
