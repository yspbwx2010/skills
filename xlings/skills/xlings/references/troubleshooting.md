# Reference: xlings troubleshooting (indexed by symptom)

> Baseline xlings source `main @ 4ea4eac` / `2026.9.14.1`, dated 2026-09-16; A6-A8 and the B3 addendum were refreshed
> against `main @ 84572b0` / `2026.9.20.1` on 2026-09-23 (source and upstream issue threads, no binary run).
> Each entry gives: symptom -> evidence (how to confirm it is this one) -> fix.
> WARNING: no binary was executed this round beyond `--help` and `--version`. Only entries marked
> `[field-tested]` were actually run end to end.
> **If the symptom is "this used to behave differently", check `version-notes.md` first** — seven
> releases landed between the previous baseline and this one, and several entries below describe
> behaviour that changed rather than broke.

---

## A. "command does not exist / unknown"

### A1 `xlings help` -> `[error] unknown command: help`, exit 1
**Evidence**: `spec::root()` has no `help` among its children (`src/cli/spec.cpp:22-75`).
**Fix**: use `xlings --help` / `-h` / bare `xlings`.
WARNING: older quickstart material presents `xlings help` as the **first post-install verification
command**. It fails at step one, which is easily misread as "xlings is broken".

### A2 `xim` / `xvm` / `xself` / `xsubos` / `xinstall` -> `was removed in 0.4.8`, exit 2
**Evidence**: `LEGACY_ALIAS_NAMES` (`src/core/compact/xself.cppm:85`) plus `compact/xself.cpp:76-84`
(the message); the **exit code 2 is not in that file** — it is `src/main.cpp:45-46`.
**Fix**: switch everything to `xlings <subcommand>`. Leftover symlinks are actively cleaned by
`self init` / `self doctor --fix`, so the advice "re-source your profile and `xim` will be found
again" **points at a check that can never be satisfied**.

### A3 `xlings subos fork ...` rejected at parse level
**Evidence**: the complete subos subcommand set is `new/use/list(ls)/remove(rm)/info(i)/stop/runtime`.
**Fix**: `xlings subos new <new-name> --from <source>`. The source may be a bare local subos name, or
a pkg-spec containing `:` / `@` (e.g. `subos:py-ds@1.0.0`; the base xpkg is installed automatically
if missing).

### A4 `xlings use gcc --pick` -> unknown option
**Evidence**: `spec.cpp:38-39` only has `-a/--all` and `--strict`.
**Fix**: the picker is now **persistent configuration**, `xlings config --interactive true`, not a
flag; and it **does not fail loudly** (the `NobodyToAsk` branch is empty, it silently falls back to
listing).

### A5 `xlings self doctor --all` works but prints an extra warning line every run
**Evidence**: `--all now means --show-ok; --all is kept as an alias but will stop being documented`
(`src/core/xself.cpp:157-166`, since 2026.9.12.1).
**Fix**: spell it `--show-ok`. The old spelling keeps working — the warning exists so a flag's
meaning cannot drift out from under a script with nobody noticing — but it is one line of noise per
invocation, which matters for anything that diffs output.

### A6 `mcpp: command not found` (or `gcc`, `cmake`, `ldd` …) right after an `xlings install`
**Evidence**: `ls <home>/subos/default/bin` is missing many names that `xlings list` shows as
active; the install ran inside a **project** scope. Upstream openxlings/xlings#582 / #604, **fixed in
2026.9.20.1**: in project scope the global workspace was read from the wrong SubOS, came back empty,
and the derived shim table removed every global entry (172 on upstream's own home).
**Fix**: on 2026.9.20.1 or newer, any global-scope `xlings install` / `xlings use`, or
`xlings self init` (prints `routing table: +N -M shim(s)`), or `xlings self update` rebuilds the table.
On an older client - including the 2026.9.16.1 that mcpp 2026.9.21.3 bundles - the damage can recur;
`xlings install xim:mcpp@<version>` restores the names, and upgrading the standalone xlings stops it.
It is a side effect of the install, not a broken mcpp installation.

### A7 `ldd` inside a SubOS says every host library is `not found` (exit 0), or rejects host binaries with a `DT_RELR` error
**Evidence**: `command -v ldd` resolves into `<home>/subos/<name>/bin`; the same binary under
`/usr/bin/ldd` resolves fine. #608: the packaged glibc `ldd` used its own loader list for every file.
**Fix**: 2026.9.20.1 makes the SubOS `ldd` run the file's own `PT_INTERP` (SKILL §1.10). On older
clients call `/usr/bin/ldd` by path for host binaries, and do not let a script trust `ldd`'s exit code
for completeness. A `glibc@2.39` payload installed by a pre-libxpkg-0.0.51 client can also carry a
corrupted `ldd` script (#522); upstream states that reinstalling that package repairs it (a fresh install from
the current index produces a correct script).

### A8 `xlings interface <capability>` answers `E_INVALID_INPUT` / exit 1 where it used to succeed
**Evidence**: 2026.9.20.1 validates `--args` before dispatch: invalid JSON or a non-object for any
capability, a missing or `null` `required` field where one is declared. The capability did **not**
run. **Fix**: send the fields `xlings interface --list` names under `inputSchema.required`. What used to
"succeed" ran with defaults - a whole-index update, an unfiltered list, or, for `create_subos` /
`remove_subos` with `{}`, the deletion of every SubOS in the home (#611).

---

## B. Install / index

### B1 `xlings install <any official package>` all report ambiguous (`scode:` vs `xim:`), and `self update` also wedges
**Evidence**: check whether `~/.xlings/data/<your third-party index name>/pkgs` contains **packages
from the official index** (real case: `data/scode/pkgs` held 185 `.lua` files while scode itself has
only 15; the marker is xim's version number).
**Root cause** (#575, before 2026.8.30.1): `main_repo_dir()` picks the default index by **array index
0**, the pointer key for the main index path is hardcoded empty, and the artifact authorization gate
is a **URL substring match compiled into the C++** (official sub-index URLs all carry that prefix, so
they pass the gate too). The trigger is `xlings index use xim <ver>` appending the default entry with
`push_back` while Config uses `insert(begin())` — two writers give opposite answers for "where does
the default entry belong".
**Fix (two escape hatches for when `self update` is itself blocked)**:
```bash
xlings install xim:xlings@latest -y && xlings use xlings <version>   # explicit namespace (recommended)
rm -rf ~/.xlings/data/<name> && xlings self update                    # or delete the polluted directory
```
On >= 2026.8.30.1 **a single `xlings update` self-heals** (the polluted directory now satisfies "take
your own artifact", and `fetch_index_artifact` atomically replaces the whole tree).

### B2 A self-hosted index "never gets artifact acceleration, always falls back to git clone"
**Evidence**: `artifact_is_declared_for(repo)` = the entry declares `artifact` itself **or** its `url`
equals the declaration source for that name (`xim` -> `xim.index-repo`; sub-index ->
`xim-indexrepos.lua` of the default index). URL comparison is normalized (strip trailing `/`, strip
trailing `.git`) but **deliberately does not touch scheme/host** — a gitee mirror does not count as
the same repo as github.
**Fix**: write `"artifact": "<base url>"` explicitly in the entry. **Local sources (`file://` or a
path) never use artifacts**; that is by design.

### B3 On CN networks `fetching package index` hangs for tens of seconds to minutes
**Root cause, two parts**: (1) git clone had **no connect timeout**, so a blocked github stalls ~127s
(a 3000ms TCP pre-probe is now done first); (2) github proxies are frequently TCP reachable but **do
not actually serve the assets**, and one fake-alive proxy sorted first costs about 30s per dead host
— **which is why the index fetch path deliberately adds no github proxy**
(`docs/design/index-distribution.md:111-113`).
**Fix**: verify `mirror` really is uppercase `"CN"` (see C1). The index path **unconditionally
appending the GLOBAL server is by design**, not a bug. To self-host, use `XLINGS_INDEX_BASE_URL` or
`xim.index-base` in `.xlings.json` (self-hosting only requires serving `xim-index-pointers.json` +
`xim-index[-sub]-<ver>.tar.gz` as static files under that base).
**Since 2026.9.16.1** a third part is closed: a git connection that completed its handshake and then
went silent could hold `xlings update` for minutes (#599 measured 11.5); git now aborts below
1000 B/s for 60 s and the whole update has a 300 s budget. A slow link therefore shows
`[index] 300s refresh budget reached: N source(s) were not refreshed and keep their local copy` -
raise `XLINGS_UPDATE_TIMEOUT` (or `XLINGS_GIT_NETWORK_TIMEOUT`) rather than retrying. A CN user whose
GitCode artifact returns 403 now falls to the GLOBAL artifact before git (region chain, SKILL §5.1);
`xlings index list` shows the order.

### B4 "It is installed but `xlings list` says no" / "It is not installed but it says installed"
**Evidence**: three sources (the `versions` ledger / each subos's `workspace` / the payload stamp
`.xpkg-install.json`) have historically disagreed. The only arbiter is `installation_state()`, with
three states `Absent`/`Installed`/`Incomplete`.
WARNING: **"payload present, ledger absent" was 115 of 340 cases on a real machine**, and the vast
majority are **leftovers** superseded by a newer version, not broken installs — so the arbiter
**deliberately requires positive evidence** and does not report them all as problems.
**Fix**: do not stat directories yourself; ask `xlings list` or `interface list_packages`. If you
suspect inconsistency, run `xlings self doctor` (read-only).

### B5 A same-named package in a different namespace is judged "already installed", `install()` never runs, and an unrelated link-time error appears
**Evidence**: before #576 the fallback judgment keyed on `node.name` (the **bare short name**). Real
case (mcpp#533): a source-built `compat:libdrm` and the `xim:libdrm` pulled in by Mesa had the same
upstream version, so Mesa's payload made it "installed" and the tree that should have been built did
not exist.
**Fix**: upgrade to >= 2026.8.30.2 (`payload_path_names_another_package` derives package identity
back from the payload path).
WARNING: the commit is explicit about what this is **not** — publishing conflicting
`<name>@<version>` to an index **remains unsafe until this version is the floor**; clients below it
keep silently skipping the install. The fix only addresses accidental collisions.

### B6 An install directory contains other packages' archives, `.lock` / `.meta` sidecars, or trees nobody installed
**Evidence**: `xlings self doctor --deep` reports **`SweptPayload`** (Error). Before 2026.9.14.1
every download landed in the shared `<data>/runtimedir` and was extracted there; a package with
**no `install()` hook** ends with an empty install dir after hooks, and staging then moved the whole
shared directory into it. Upstream measured 221 of 401 version directories carrying swept sidecars
and 5.2 GiB of foreign archives on one machine. The marker `xim::swept_payload_marker` looks for a
zero-length `<name>.lock` with a same-named sibling, a `<name>.meta` sidecar, or a top-level entry
ending in a download/archive extension.
**Fix**: `xlings self doctor --fix`. It goes straight to **remove-then-install** rather than the
cheap "install alone" rung, because a swept payload already reads as correctly installed
(`src/core/xself/doctor.cppm:263-273`). That means downloads — throttle the command on a small
machine.
=> **Worth one deliberate pass on any home built on 2026.9.12.1 or earlier.** The contamination is
invisible in normal use and costs real disk. Note also that archives now stay in the download cache
permanently, so the disk model changed; on btrfs with snapshots, freeing them will not show in `df`
until snapshots rotate.

### B7 `xlings update` deleted a local recipe you added with `--add-xpkg`
**Evidence**: since 2026.9.12.1, after syncing and rebuilding, `update` scans the local overlay and
**deletes entries byte-identical to the freshly synced index**, printing
`N local recipe(s) identical to the synced index were removed: ...`
(`src/core/xim/commands.cpp:2477-2490`). `--add-xpkg` likewise refuses to store such a copy in the
first place (Note `xim.overlay_identical`, exit 0, nothing written, `:2259`).
**Fix**: none needed if the recipe matched upstream — that is the point. A recipe whose content
genuinely diverges (`modified`) is untouched. **Do not use the overlay as version control** for a
recipe you maintain: the moment it converges with upstream it disappears.
Inspect and clean up with `xlings config --list-xpkg` then `--clear-xpkg stale`.

---

## C. Mirror / network config "set but not in effect"

### C1 `"mirror": "cn"` is set but it still connects to github
**Evidence**: matching is **exact and case-sensitive at runtime**. `Config` reads without normalizing
(`config.cpp:545-546,653-654`); only `self install` trims and uppercases before writing
(`normalize_mirror_`, `xself/install.cpp:34-41`). Lookup of
`"cn"` -> the built-in table only has `"CN"` -> miss -> lookup `"DEFAULT"` -> miss -> fall through to
GLOBAL, **silently back to github**.
WARNING: **the upstream schema doc's own example is lowercase**
(`docs/spec/xlings-json-schema.md:518`). That example is self-consistent (it also lowercases
the `XLINGS_RES` keys), but **copying half of it walks into this**.
**Fix**: write uppercase `"CN"`. `xlings config --mirror` performs **zero validation**; whatever you
type is stored, so a typo raises no error.

### C2 `XLINGS_MIRROR=CN xlings install ...` has no effect at all
**Evidence**: `XLINGS_MIRROR`/`XLINGS_INSTALL_MIRROR`/`XLINGS_RELEASE_MIRROR` are **never read at
runtime**; they are only used by `xlings self install` to **write into** `.xlings.json`
(`env_install_mirror_`, `xself/install.cpp:57-64`).
**Fix**: **"set an env var to switch mirrors temporarily" is not possible.** Change the config file or
run `xlings config --mirror CN`.

### C3 `mirror_fallback` is set but gitcode/gitee URLs still have no fallback
**Evidence**: **non-github domains are never proxied** (`mirror/expand.cpp:132-136` returns them
unchanged).
**Fix**: by design, not a bug. gitcode/gitee URLs handed to CN users carry no ghfast/kkgithub
fallback. Also note that `mirror` (region) and `mirror_fallback` (github proxy) are **two unrelated
mechanisms**; the directory `src/core/mirror/` is the latter.

### C4 The project sets `"mirror"`, but the project root also sets `"projectScope": false`
**Evidence**: `load_project_config_from_dir_` returns at `:641-645`, while `mirror` is read at `:653`
— **unreachable**. Meanwhile `workspace` goes through `xlings install`'s own cwd walk-up
(`src/cli.cpp:536-599`), which **never checks `projectScope`**, so **it still takes effect**.
**Fix**: if you want a project-level mirror, do not write `projectScope: false`. The xlings repository
root itself is configured that way; do not copy it as a "project config example".

---

## D. SubOS / relocation

### D1 After copying or moving a home, first use reports "SubOS not self-describing" plus "glibc version mismatch"
**Evidence**: doctor's `FindingKind::SubosManifest` (Error) — the `subos_info` block is missing or
unreadable; `host_glibc` is missing or is **the stale value recorded on the source machine**, which
`closure_check` rule A compares against the glibc payload owning the interpreter.
**Fix**: one `xlings self doctor --fix` is enough [field-tested 2026-08-30]. Mechanism: `--fix` calls
`describe_block` (`src/core/subos/manifest.cpp:381`), and `runtime` takes **level 4** of the
five-level ladder — it actually reads which payload the `lib/libc.so.6` symlink points at and derives
the binding from that (using `symlink_status`, not `exists`, so **a dangling link still tells us
which payload was originally wired**, `:415-420`), and `host_glibc` is re-stamped from the current
host via `platform::host_glibc_version()`.
WARNING: **it repairs self-description and the glibc stamp, not the ELF** (see D2).
WARNING: if `.xlings.json` is itself **not valid JSON**, `--fix` **refuses to touch it** (rewriting
would drop a workspace nobody can parse) and the remedy becomes `inspect <path>`. Since 2026.9.12.1
an unreadable subos state file is also a finding in its own right (`SubosUnreadable`, Warning) rather
than being silently skipped — see D7.

### D1b `home relocated  this home is at <new>, but its records were written for <old>`
**Evidence**: `FindingKind::HomeRelocated` (`src/core/xself/doctor.cppm:174`, since 2026.9.5.1). The
detector compares the **modal** store prefix in the version records against the current root, and
requires that at least one record's payload actually exists under the current root. An old root that
is still a live independent home (another home, a project-scope `.xlings`) does not count.
**Fix**: `xlings self doctor --fix` re-points the version DB, the index caches, the subos manifests
and **every subos's sysroot links** to the current root. A registration an older client dropped comes
back with `xlings install <pkg>@<version>` in about a second, with no download, because the payload
is still on disk.
WARNING, version floor: **on 2026.9.4.1 specifically, do not run `--fix` on a moved home** — that
release deletes the dangling links the old symlink workaround could recover (measured upstream: 1173
links deleted and 367 registrations dropped on a 152 GB moved home whose 234 package directories were
all present). Keep a symlink at the old path until you are on 2026.9.5.1 or newer.
WARNING: detecting the move does **not** make the home relocatable. `PT_INTERP` is read literally by
the kernel and payload contents are never touched; see D2. Upstream's position is unchanged —
relocation is won't-do, and a registry-shaped home is a rebuildable cache you drop and re-provision.

### D2 After relocation `ls` shows the file but `exec` reports it does not exist
**Evidence**: ELF files in the payload embed **install-time absolute paths** (`PT_INTERP` and
`DT_RPATH`; RPATH rather than RUNPATH since libxpkg 0.0.57). The embedding happens when the **xlings
installer** uniformly calls `executor.apply_elfpatch_auto()` (`installer.cpp:3246`), not in the
package script.
**Fix**: `doctor --fix` does **not** re-patch ELF (`grep -c patchelf src/core/xself/doctor.cpp`
returns 0, and since 2026.9.5.1 the report says so in a note alongside the relocation finding). The
only remedy is **reinstalling with `xlings install <coordinate>`** (`doctor.cpp:1811`, merged by
owning package, so 9 broken llvm targets reinstall once), which re-runs elfpatch. **A home can only
be installed fresh in place; do not `mv` it.** [field-tested: ls shows the file, exec reports it does
not exist]
WARNING: subtle variant — while **the original path still exists** the binary still runs, but it uses
**the loader of the old home**: no error, only latent breakage.

### D3 alias/env records a concrete subos path (`SubosPathBaked` Warning)
**Evidence**: the criterion is "will this **value** be rewritten by `pin_subos_paths`", **not** "does
it contain `--sysroot` syntax" (`doctor.cpp:1261-1306`). Measured on a real machine: of 184 `xvm.add`
calls in the index, **exactly one** (gcc.lua) puts a subos path into an alias. The rule is "no
concrete **SUBOS** path", not "no absolute path" — the absolute path in musl-gcc.lua points at a
**payload**, which is correct as seen from any subos.
**Fix**: `doctor --fix` rewrites it back to a placeholder via `pin_subos_paths`.

### D4 `--sysroot=` expands to an empty string, the compiler reads the host root, and the symptom is a `cannot find crt1.o` three layers away
**Evidence**: `EntryBinaryDrift` (`doctor.cppm:230-243`) — an old entry binary does not recognize
`${XLINGS_DYNAMIC_SUBOS_DIR}`, passes it through to the shell, and it expands to empty.
Self-containment was **silently lost for 5 days**.
**Fix**: upgrade. Detection uses `vanishing_xlings_reference()` (`db.cppm:227-262`), which does not
consult a list but asks "if we exec right now, will this reference disappear".

### D5 After `subos use <name>` nothing feels isolated
**Evidence**: **the shell profile does not isolate the filesystem by default**; it only swaps PATH and
injects env (`src/core/subos.cpp:1226-1245`). Storage mode (shared/tmpfs/image) **only applies on the
`--sandbox` path**; the **shell-level entry never mounts** (a hard V4 rule at `:1264-1276`; an earlier
V6 merged the two axes, which made `subos use <image-subos>` silently require root + bwrap + mount
namespace, and was reverted).
**Fix**: add `--sandbox` if you want filesystem isolation. Note: **`--sandbox` on macOS/Windows is not
a security boundary** — it only redirects HOME/USERPROFILE. **For untrusted code use an OS sandbox or
a VM.**

### D6 `--gpu` has no effect
**Evidence**: **bwrap only**; missing devices are silently skipped; **ignored under the proot backend**
(proot already passes `/dev` and `/sys` through wholesale). `--gpu` also requires `--sandbox`.
**Fix**: confirm the backend is not proot (bwrap first -> userns probe -> proot fallback; the system
`/usr/bin/bwrap` is skipped). A GL / direct-rendering check inside a sandbox needs `--gpu`; the
sandbox says so on entry when it has no GPU devices.
WARNING: a probe that detects "am I inside a sandbox" via `XLINGS_SUBOS` **never fires** — that
variable is not exported. `XLINGS_SUBOS_LIB` is (`src/core/subos/sandbox.cpp:735`), and the variable
xlings itself reads to refuse nested entry is `XLINGS_SUBOS_MODE=sandbox` (`:678`, written `:730`).
Upstream recorded the same mistake in its own 2026.9.5.1 verification pass, noting that "the probe
was written wrong" and "the product is broken" look identical in the output.

### D7 A subos silently disappeared from `list --all`, reference counts, and doctor
**Evidence**: `subos/<name>/.xlings.json` failed to parse (bad JSON, not an object, missing
`workspace`). Before 2026.9.12.1 this was swallowed by `catch(...){}`, so the subos vanished from
every cross-subos question — **including reference counting, so a payload still in use could be
deleted**. Now `xlings list --all` prints a Note (`xim.subos_unreadable`) naming what it could not
show, `remove` lists it as `<name> (unreadable)` when deciding whether a payload is still referenced
(i.e. "cannot confirm", not "confirmed unused"), and doctor reports `SubosUnreadable` (Warning) with
its own counter rather than folding it into `broken payloads`.
**Fix**: repair or delete the state file. If you hand-edit subos state files for probes, this is the
finding that tells you which one you broke.
**Note for output parsers**: `list --all` gained that extra Note line.

### D8 Doctor reports a pile of dangling or missing sysroot links right after upgrading
**Evidence**: the dangling-link scan covered only `{usr, etc, share}` until 2026.9.4.1 and now
covers `{usr, etc, share, lib, lib64}` in both detection and repair
(`src/core/xself/doctor.cpp:2263,4183`). On a never-moved home upstream found 3042 links under
`subos/*/lib*`, six dangling, none previously reported. `SysrootMissing` (2026.9.5.1) additionally
reports links the current selection declares that are simply not there.
**Fix**: this is detection surface widening, **not fresh damage** — expect it, especially on
musl-first subos where `lib/` is almost entirely links into payloads. Repair now asks the versions DB
where a link belongs and **re-points** it (note `link repointed`), deleting only when nothing can
place it (`dangling link removed`). For a single package, `xlings install <pkg>@<version>` is much
cheaper than a whole-home `--fix`: with the payload present it does not download, it just
re-registers and replays the links.

### D9 `self doctor --fix` exited 0 but something is missing afterwards
**Evidence**: since 2026.9.4.1 a run that converged **but lost information** prints
`status  N registration(s) dropped and M sysroot link(s) removed — nothing here could restore them;
the rest of the home is consistent` instead of `OK — workspace, shims, and payloads are all
consistent` (`doctor.cpp:4949-4985`). The exit code deliberately does not move, because it answers
"does this home still need a human", and a completed lossy repair does not.
**Fix**: **read the verdict line, not only `$?`.** Any non-zero `pruned` / `sysroot link(s) removed`
count is unrecoverable loss worth a look. Gating scripts that only check the exit code will miss it.

---

## E. Multi-version / `use`

### E1 After `xlings use gcc`, `gcc --version` is unchanged and the exit code is 0
**Evidence**: **without a version, no candidate count switches** — the implementation says
`// NO single-candidate auto-switch.` (`src/core/xvm/commands.cpp:1079`), `cmd_use_by_name`
(`:1075`) unconditionally does `return cmd_list_versions(...)` (`:1140`), and that returns a fixed
`0` (`:1072`). **The `>1` case also exits 0, not 2.**
WARNING: upstream text states the opposite in two places — the header comment in `commands.cppm`
and `docs/quick-start/multi-version.md:52-56` — as does documentation derived from them, all claiming
"1 candidate -> switches directly". **Trust the implementation.**
**Fix**: pass a version (`xlings use gcc 14.2.0` or `xlings use gcc@14.2.0`). In scripts, **always
pass a version**.

### E2 `xlings use <tool> <ver>` says "not installed in this subos" but I did install it elsewhere
**Evidence**: **`use` only switches among versions already installed in this subos.** Reason: **the
version database does not record dependency relationships**, so activating directly could activate gcc
itself but not the glibc it depends on, yielding a toolchain that runs, reports the right
`-print-sysroot`, and **simply cannot compile**, with no warning anywhere.
**Fix**: run `xlings install` inside this subos. `--all` only widens the **candidate list** to all
subos (view, not switch).

### E3 After switching releases some program still points at the old version
**Evidence**: switching happens **per release, as a group**; programs absent from the new release
**keep pointing at the release you just left**, and `use` **warns about each by name**.
**Fix**: by design. To reject such mixes, add `--strict` (refuse to switch, zero changes).
WARNING: historical trap — `switch_plan.cppm:36-42`. The planner used to read `VData::libdir`, and
**not one of 372 real records ever wrote that field**, so `xlings use` was **a complete no-op for
library files**. It now uses `path` + `sourceName` + `destinationName`. "The libraries did not follow
the switch" on older versions is this bug.

---

## F. mcpp-side integration

### F1 `[xlings] deps` declares a package but the build still reports `fatal error: <header>: No such file or directory`
**Two cases**:
- **Old versions (before #531)**: deps were **written to a file and nothing more** — "the declaration
  looks accepted but does nothing". Upgrading fixes it.
- **New version, looking in the wrong place**: provision is **GLOBAL scope**, landing in
  `$MCPP_HOME/registry/data/xpkgs/...` plus the activation view `$MCPP_HOME/registry/subos/default`
  (= mcpp's `--sysroot`). **Even if the project declares `subos = "tools"`, deps still install into
  `registry/subos/default`**; the two are not the same place. An upstream comment records the
  measurement: calling `install_packages` on a project env puts headers under
  `<owner root>/.mcpp/.xlings/subos/_/usr/include` while `--sysroot` points elsewhere, so "the
  dependency is installed and declared, yet `#include <gbm.h>` still fails".
**Fix**: look for the payload under `registry/subos/default`. After changing the list the stamp is
invalidated and provision re-runs.
WARNING: **the stamp has moved out of the project.** It now lives at
`$MCPP_HOME/provisioned/xlings-deps-<16 hex FNV-1a of the dep list>`
(`mcpp/src/build/prepare.cppm:1469-1484`), keyed by the **list** rather than by the project, because
the installation is shared. The old `<project>/.mcpp/.xlings-deps.stamp` is still **read** as a
legacy fallback but never written (`:1517`). Deleting the old path therefore does nothing; the reason
for the move is that a stamp inside the project made that project keep claiming the packages were
installed after `MCPP_HOME` was wiped, and `mcpp clean` (which removes `target/`, never `.mcpp/`)
could not clear it.
WARNING: **`--offline` now DOES block this provision** — stale advice to the contrary predates mcpp
**2026.9.1.1** (`3da6b0c1`, #540). When the dep list is not provisioned and either `--offline` /
`MCPP_OFFLINE` or `MCPP_NO_AUTO_INSTALL` is set, the build **fails hard** rather than downloading:
`<label> are declared but not provisioned, and auto-install is off.` followed by the declared list and
the `xlings install <deps>` command to run yourself (`mcpp/src/build/prepare.cppm:1541-1571`).
The **one** exception is a matching **pre-2026.9.1.1 legacy project stamp** (`:1558`, `:1572-1578`):
that lets the build proceed silently, and deliberately does **not** write the registry stamp, because
nothing was verified. => Under either knob, an unprovisioned list is an error you must resolve, not a
silent download.

### F2 mcpp reports `error: selected SubOS '<name>' does not exist at ...`
**Evidence**: **mcpp reads SubOS but never creates one** — a name that does not resolve is a **hard
error**, and it deliberately does not fall back to default/active (falling back would substitute a
different environment for the one the manifest named, which is exactly how "one mcpp.toml means two
different builds" happens).
**Fix**: create it with **xlings**: `xlings subos new <name>` (creating and populating a SubOS is
xlings' layer).

### F3 mcpp emits a note that the runtime binding is `inconclusive`, but the build continues
**Evidence**: the SubOS exists but has **no `subos_info` block** -> **degrade rather than fail**.
WARNING: **an mcpp-managed sandbox subos was measured in exactly this state — 356 workspace records,
zero self-description** (`mcpp/src/xlings/subos_info.cppm:32`).
**Fix**: `xlings self doctor --fix` (it takes the D1 path and fills in `subos_info`).

### F4 A leftover `MCPP_VENDORED_XLINGS` makes mcpp use "some other" xlings
**Evidence**: it is **first in priority** in mcpp's xlings acquisition chain; if present, mcpp
`copy_file`s it to `destBin` and adds the execute bit (`mcpp/src/fallback/xlings_binary.cppm:107`),
printing `Bundled xlings (from MCPP_VENDORED_XLINGS)`.
**Fix**: strip it with `env -u` when isolating. WARNING: some reproduction recipes set it
deliberately — check before removing it.

---

## G. Isolation / cross-contamination

### G1 `XLINGS_HOME` was stripped but the user's real `~/.xlings` was still touched
**Two known paths**:
- **`$HOME` fallback wholesale copy**: mcpp's `copy_xpkg_from_global()` derives
  `~/.xlings/data/xpkgs/...` from `$HOME`/`$USERPROFILE` and, on a hit, recursively copies it into the
  sandbox. The trigger is narrow (`xlings install` exits 0 but verdir does not exist), but **`env -u
  XLINGS_HOME` is completely ineffective here — it reads `HOME`**.
- **`.xlings.json` cwd walk-up**: see G2.
**Fix**: for a hard guarantee you must change `HOME` (or confirm that fallback cannot trigger).

### G2 Running xlings under some directory suddenly behaves differently (different mirror / installs elsewhere)
**Evidence**: project mode was silently activated. The walk-up has three brakes: `projectScope:false`
**skips but keeps walking up**; a level that has both `.xlings.json` **and** a `subos/` subdirectory is
treated as an xlings home and **stops the walk**; only if neither hits does it fall back to
`XLINGS_PROJECT_DIR`.
**Fix**: use a clean cwd (something like `/tmp`), or pass `-g` explicitly (`forceGlobalScope_`), or
`-u XLINGS_PROJECT_DIR`. [field-tested 2026-08-31: four directory levels above a working directory had
no `.xlings.json`, but an `<mcpp source checkout>` had one of its own.]

### G3 After `env -u XLINGS_HOME` the home becomes a strange directory
**Two possibilities**: (1) **the self-contained probe hit** — the parent of the binary's directory has
both `.xlings.json` and `bin/xlings`, so home **silently becomes that root**; (2) `HOME` was stripped
too — on Linux home becomes **`./.xlings` (relative to cwd)**.
**Fix**: pass `XLINGS_HOME=<what you want>` explicitly instead of only using `-u`.

### G4 After install the same directory appears twice in PATH
**Evidence**: the profile's PATH dedup check is `case ":$PATH:" in *":$XLINGS_BIN:"*)`; when
`XLINGS_BIN` is empty it degenerates into matching `"::"`, so the entry is **prepended again**.
**Fix**: harmless. To avoid it, do not re-source the profile immediately after stripping `XLINGS_BIN`.

### G5 A tool "works" inside the isolated home but is actually the host's copy
**Evidence**: since 2026.9.3.1, when the resolved scope makes **no claim at all** on a command name
(not active, not even present in `installed[]`), the shim `exec`s the first same-named executable
that belongs to no xlings home and exits 0, instead of erroring. On a tty it prints
`name: no version in subos 'X'; running /usr/bin/name` **to stderr**; in a non-tty gate it prints
nothing (`src/core/xvm/shim.cpp:596-625`). The other two states — "in `installed[]` but nothing
active" and "pinned but not installed" — are claims this scope makes and cannot meet, and remain
errors on purpose.
**Fix**: do not treat exit 0 as proof of provenance. In a gate, assert where the tool resolves — e.g.
that `command -v <tool>` lands under the home you meant — rather than only checking `$?`. A shim
invoked by explicit path (`<project>/.xlings/subos/_/bin/node`) never passes through, so calling by
full path is another way to make the failure loud.
=> This matters most for a hermetic toolchain: a tool missing from your home used to fail loudly and
now quietly runs the host's build of it, which is how a gate goes green against the wrong libc.

---

## H. Scripts / agents

### H1 `xlings remove foo --agent` without `-y` removes nothing (historically it faked success)
**Current shape on 2026.9.14.1**: `--agent` sets `canConfirm = false` [`src/core/uimode.cpp:83`], so the
prompt is never asked and returns `NobodyToAsk` [`src/runtime/event_stream.cpp:75-77`]; remove's `Refuse`
policy then emits `cli.needs_confirmation` and **exits 2** with nothing changed
[`src/core/xim/commands.cpp:109-118`]. So the observable symptom is **exit 2 + a diagnostic**, not a
silent success.
**Historical symptom (pre-`Refuse`-policy clients, do not match on it today)**: `--agent` answered every
prompt with `defaultValue` and the two confirmations have opposite defaults, so the command printed
`cancelled`, exited **0**, and left the package installed — which the calling agent read as "removal
succeeded". Cross-check SKILL §1.6 and `machine-output.md §1`, which date it the same way.
**Fix (unchanged)**: pass **`-y` explicitly**. This applies to install/remove/update alike.

### H2 A failing `xlings install` is treated as success in CI
**Evidence**: `cmdline::App` dropped the action's int return value into a `std::function<void(...)>`
and swallowed it; it is now recovered through a shared `action_rc`
(`src/cli.cpp:1629-1635,1886-1900`).
**Fix**: upgrade. Also, under zsh `${PIPESTATUS[0]}` is always empty (zsh spells it `$pipestatus[1]`,
1-indexed), so **do not read exit codes through a pipe**.

### H3 A bare `xlings interface` call returns no capability table
**Evidence**: it returns
`{"kind":"result","exitCode":1,"error":"capability name required. Use --list…"}` and **exits 1**
(`interface.cpp:90-92`).
**Fix**: `xlings interface --list`; and the key is **`protocol_version`**, not `protocol`.

### H4 You want to dry-run an install
**Evidence**: `xlings install` **has no `--dry-run`** (the ones that do are `self uninstall` /
`self clean` / `self doctor`).
**Fix**: use the NDJSON **`plan_install`** capability; it has no CLI counterpart.

### H5 A script that read `pkgCount` from `list_subos` now gets nothing
**Evidence**: field rename in 2026.9.3.1. The entries carry **`commands`** and **`packages`**
(`src/capabilities.cpp:303-304`), backed by `SubosInfo::commandCount` / `packageCount`
(`src/core/subos.cppm:60,64`). `commands` = routing-table size; `packages` = releases de-duplicated
through `bindingGroup`, so one llvm is 1 package and roughly 40 commands. The agent text changed the
same way, from `(N packages)` to `(N commands, M packages)`.
**Fix**: read the new keys. The read side still tolerates an old `pkgCount` on input, but nothing
emits it. Upside: `packages` is finally a real package count, so "this subos should contain N
packages" is now an assertion you can make in a gate.

### H6 The new `remove` / `config --*-xpkg` / `doctor --subos` verbs are missing from `interface`
**Evidence**: the 2026.9.12.1 surface is **CLI-only**; the NDJSON/capabilities channel received only
the `list_subos` field rename. Upstream openxlings/xlings#593, **open on 2026.9.14.1**.
**Fix**: there is none through `interface` — shell out to the CLI for those operations, or wait.
Worth knowing before designing an agent integration around the NDJSON channel exclusively.

### H7 The "run `xlings self doctor --fix`" nag stopped appearing (or your workaround for it broke)
**Evidence**: since 2026.9.12.1 that hint, and the namespace-priority warning, are emitted **once per
(id, fingerprint)** and persisted in `.xlings.json["hintsSeen"]` via `xlings.core.notice`
(`src/core/notice.cppm`). Upgrading to a newer client announces again; the same state does not. It is
TTY-gated, and `self` / `interface` subcommands are excluded entirely.
**Fix**: if anything of yours keyed off the nag's presence to judge health, switch to the
`verifiedBy` field or the doctor exit code. If anything worked around the repetition, that workaround
is obsolete. Note `hintsSeen` is a **write** — on a read-only home it fails silently and the note
reappears next time, rather than failing the command.
