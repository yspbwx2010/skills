# Boot order, environment, and the install-block state

Verified against KernelSU `ksud` (`src/init_event.rs`, `src/module.rs`, `src/metamodule.rs`).

## Boot execution order

```
post-fs-data stage (blocking):
  1. common /data/adb/post-fs-data.d/*        (executable only)
  2. prune modules, restorecon, load sepolicy.rule
  3. metamodule post-fs-data.sh
  4. regular modules' post-fs-data.sh
  5. load system.prop  (resetprop)
  6. metamodule metamount.sh                  ← the mount backend, after ALL post-fs-data
  7. post-mount stage:
       common /data/adb/post-mount.d/*
       metamodule post-mount.sh
       regular modules' post-mount.sh

service stage (non-blocking):
  common /data/adb/service.d/*  →  metamodule service.sh  →  regular modules' service.sh

boot-completed stage (non-blocking):
  common /data/adb/boot-completed.d/*  →  metamodule boot-completed.sh  →  regular modules' boot-completed.sh
```

Rules that follow from this:

- **`metamount.sh` runs after every post-fs-data script.** State those scripts need (e.g. a mounted
  image) can be prepared in the metamodule's `post-fs-data.sh` (step 3), which runs before mount.
- **The metamodule's lifecycle scripts run before regular modules' at every stage** — it is
  infrastructure the regular modules depend on.
- **post-fs-data (and metamount) are blocking**: keep them fast and crash-free or you bootloop.
  service / boot-completed are non-blocking.

## Environment variables

From `get_common_script_envs` (KernelSU). Present in the hook and lifecycle scripts:

| Var | Value |
| --- | --- |
| `ASH_STANDALONE` | `1` |
| `KSU` | `true` — detect KernelSU |
| `KSU_VER` / `KSU_VER_CODE` | manager version name / code |
| `KSU_KERNEL_VER_CODE` | kernel-side version |
| `KSU_UAPI_VER` | UAPI version |
| `KSU_RUNTIME_MODE` | runtime mode |
| `KSU_MODULE` | the module id, when a script runs for a specific module |
| `KSU_LATE_LOAD` | `1` during late load |
| `PATH` | includes the KSU busybox dir |

Plus the per-hook extras: `metamount.sh` gets `MODULE_DIR`; `metauninstall.sh` gets `MODULE_ID`;
`metainstall.sh` (sourced) gets the full installer variable/function set (see `references/hooks.md`).

APatch sets the same shape with `APATCH*` / `AP_MODULE` names instead of `KSU*`.

## The install-block state machine

`ksud` refuses to install a **regular** module when **all** of these hold (see
`metamodule::check_install_safety`):

1. a metamodule is active, and
2. it has a `metainstall.sh` (i.e. it customizes installs), and
3. it is in an **unstable** state — it has an `update`, `remove`, or `disable` marker (a pending
   change, or disabled).

In that case the install is blocked until you **reboot** to settle the pending change (or re-enable
the metamodule). A metamodule with no `metainstall.sh`, or in a clean state, does not block.
Installing the **metamodule itself** is never blocked and always uses the default installer.

Consequence for users: after installing/updating/disabling a metamodule, **reboot before installing
regular modules**. If installs are being refused, this state is why.
