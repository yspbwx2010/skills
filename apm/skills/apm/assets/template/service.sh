#!/system/bin/sh
# late_start service stage: non-blocking, runs in parallel with boot. Preferred for most work.
MODDIR=${0%/*}

# Example: wait for boot to complete, then act.
# until [ "$(getprop sys.boot_completed)" = "1" ]; do sleep 1; done
