#!/system/bin/sh
# post-fs-data stage: BLOCKING, before zygote. APatch runs it after the metamodule mounts,
# KernelSU before (KernelSU waits up to 35 s, APatch has no timeout): keep it short.
# Only use this when you must act early. Never call `setprop` here — use `resetprop -n k v`.
MODDIR=${0%/*}
