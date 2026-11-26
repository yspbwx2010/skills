# Boot scripts, stages and environment

Verified against APatch 11224 (`apd/src/event.rs`, `module.rs`) and KernelSU v3.3.1
(`userspace/ksud/src/init_event.rs`, `module.rs`).

## Module scripts vs general scripts

- **Module scripts** live in the module dir and run only when the module is enabled:
  `post-fs-data.sh`, `post-mount.sh`, `service.sh`, `boot-completed.sh`.
- **General scripts** live in `/data/adb/{post-fs-data,post-mount,service,boot-completed}.d/` and
  run regardless of any module — **only if executable** (`chmod +x`). A module must **not** install
  general scripts during its own install.

Every script begins with `MODDIR=${0%/*}` to locate its module dir. All run in the manager's BusyBox
`ash` **standalone mode** (each command resolves to a busybox applet unless a full path is used).

## Stages and blocking

| Stage | Script | Blocking |
| --- | --- | --- |
| post-fs-data | `post-fs-data.sh` | **yes** — boot pauses until done (KernelSU: `BOOT_STAGE_TIMEOUT` 35 s; APatch: no timeout, `TODO: Add timeout`); before zygote. APatch: after the metamodule mounts; KernelSU: before it mounts |
| post-mount | `post-mount.sh` | yes — after the metamodule's `metamount.sh` (both managers) |
| late_start service | `service.sh` | **no** — parallel with boot; **use this by default** |
| boot-completed | `boot-completed.sh` | no — after Android boot completes |

Rules:

- In **post-fs-data** never call `setprop` — it deadlocks boot. Use `resetprop -n <name> <value>`.
- Only run in post-fs-data when you must act before zygote; otherwise use `service.sh`. Do not
  depend on mounted files there: whether they are mounted yet differs between the two managers.

## Actual apd ordering in post-fs-data (from event.rs)

1. safe-mode check (if safe mode: disable all modules, still promote pending updates, then return before
   any mount or module script)
2. general `post-fs-data.d` scripts
3. handle module updates (promote `modules_update/`)
4. prune / restorecon
5. load `sepolicy.rule`
6. metamodule `metamount.sh` (if a metamodule is active)
7. module `post-fs-data.sh`, then per-module `<id>.lua` post-fs-data
8. load `system.prop` (via resetprop)
9. run the **post-mount** stage (metamodule → modules → lua)

## Actual ksud ordering in post-fs-data (KernelSU v3.3.1, init_event.rs)

1. safe-mode check, then general `post-fs-data.d` scripts
2. handle module updates, prune modules, regenerate the preinit rc
3. restorecon, load `sepolicy.rule`, apply root-profile sepolicy, init features
4. the **metamodule's** `post-fs-data.sh` first, then every module's `post-fs-data.sh`
5. load `system.prop`
6. metamodule `metamount.sh` — **modules are mounted only here**
7. run the **post-mount** stage (metamodule first, then modules)

KernelSU has no Lua stage scripts.

Then `service` and `boot-completed` stages fire at their points in boot.

## Environment variables in scripts

`apd` sets for module/general scripts (from `get_common_script_envs`):

| Var | Value |
| --- | --- |
| `ASH_STANDALONE` | `1` |
| `APATCH` | `true` — use this to detect you're under APatch |
| `APATCH_VER` | manager version name |
| `APATCH_VER_CODE` | manager version code |
| `AP_MODULE` | the module id (when run for a specific module) |
| `PATH` | includes `/data/adb/ap/bin` (busybox) |

KernelSU's `ksud` sets instead: `ASH_STANDALONE=1`, `KSU=true`, `KSU_VER`, `KSU_VER_CODE`,
`KSU_KERNEL_VER_CODE`, `KSU_UAPI_VER`, `KSU_RUNTIME_MODE`, `KSU_MODULE` (module id), and `PATH` with
`/data/adb/ksu/bin`.

On APatch, boot-flow scripts may also see `KERNELPATCH_VERSION` and `KERNEL_VERSION` when the event
runner inherited them (it handles their absence); KernelSU does not set them. Do not assume Magisk's full env in a boot script — that larger set
(`MAGISK_VER`, `MODPATH`, `ARCH`, …) is the **install** environment (see `references/installer.md`).

## Lua stage scripts (APatch addition)

Alongside the shell stage scripts, `apd` runs a module's `<id>.lua` for the same stages
(`exec_stage_lua`) and for the Action button. Optional; use it if you prefer Lua to shell. Shell
scripts are the portable choice, especially for Magisk/KernelSU compatibility.
