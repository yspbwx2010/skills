# Loading, controlling, unloading a KPM

Verified against KernelPatch 0.13.9 (`user/supercall.h`, `patch/`, and APatch 11224).

## 1. Runtime load via SuperCall (needs the superkey)

From `user/supercall.h`. All calls take the superkey string as the first argument.

```c
#include "supercall.h"

long sc_kpm_load(const char *key, const char *path, const char *args, void *reserved);
long sc_kpm_control(const char *key, const char *name, const char *ctl_args,
                    char *out_msg, long outlen);
long sc_kpm_unload(const char *key, const char *name, void *reserved);
long sc_kpm_nums(const char *key);
long sc_kpm_list(const char *key, char *names_buf, int buf_len);
long sc_kpm_info(const char *key, const char *name, char *buf, int buf_len);
```

- `sc_kpm_load` passes `path` and `args` to the module's `init(args, "load-file", NULL)`.
- `sc_kpm_control(name, ctl_args, ...)` invokes the module's `ctl0`; the module writes its reply
  into `out_msg` with `compat_copy_to_user`.
- `sc_kpm_unload(name, ...)` calls the module's `exit` and frees it.
- `name` is the module's `KPM_NAME`.

The `kpatch` CLI (KernelPatch `user/`, or `apd` on Android) wraps these; e.g.
`kpatch <superkey> kpm load /path/my.kpm "args"`.

## 2. Embed at patch time via kptools

`kptools` bakes a `.kpm` into the patched kernel image so it loads automatically at boot. Flags
(as APatch's patch flow builds them):

| Flag | Meaning |
| --- | --- |
| `-M <file.kpm>` | the module to embed |
| `-A <args>` | args string passed to `init` |
| `-V <event>` | boot event that triggers the load |
| `-T <type>` | extra type; `kpm` for a KPM |

`kptools -l -k kpimg` prints image info (version, superkey, embedded extras).

### Boot events (from `preset.h`)

`init(args, event, NULL)` receives one of these. The default when none is set is
`pre-kernel-init`:

`paging-init`, `pre-kernel-init` (= KPM default), `post-kernel-init`, `pre-init-first-stage`,
`post-init-first-stage`, `pre-exec-init`, `post-exec-init`, `pre-init-second-stage`,
`post-init-second-stage`, `early-init`, `init`, `late-init`, `post-fs-data`, `boot-completed`.

A module can also register `KPM_EVENT` to be notified of **later** events after it's loaded
(`notify_modules_event`).

## 3. APatch auto-load directory

APatch scans a directory at the `post-fs-data` event and loads each KPM found:

```
/data/adb/ap/kpm/<name>/<name>.kpm      # loaded on post-fs-data
/data/adb/ap/kpm/<name>/disable         # if present, this KPM is skipped
```

`<name>` must be a valid name (no `/`, `\`, `.` or `..`; < 128 bytes). APatch's **KPM screen**
(the manager app) drives load/unload/control and the embed-at-patch flow through the same JNI
`nativeLoadKernelPatchModule` / `nativeUnloadKernelPatchModule` / `nativeControlKernelPatchModule`
calls, all of which pass the superkey.

## Load-failure behaviour

- `init` returning non-zero ⇒ load fails; the loader then calls your `exit` and frees the module.
  So `exit` must tolerate being called after a partial `init`.
- Duplicate `KPM_NAME` ⇒ `-EEXIST`.
- Unknown undefined symbol ⇒ load fails, message `unknown symbol: <name>`.
- No `.kpm.init`/`.kpm.exit`, or stripped ⇒ `-ENOEXEC` with a specific message
  (see `references/build.md`).
