#!/system/bin/sh
# post-fs-data stage: BLOCKING (~10s budget), before modules mount and before zygote.
# Only use this when you must act early. Never call `setprop` here — use `resetprop -n k v`.
MODDIR=${0%/*}
