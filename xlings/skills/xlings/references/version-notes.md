# Reference: what changed, release by release

> Baseline xlings source `main @ 84572b0` (`VERSION = "2026.9.20.1"`, `src/core/config.cppm:13`), dated
> 2026-09-23, read from source, docs and the merged PRs; **no 2026.9.20.1 binary was run**. Previous
> baselines of this skill: `4ea4eac` / `2026.9.14.1` (2026-09-16, binary-checked) and `f5a0775` /
> `2026.8.30.2`, 2026-08-31.
> **This file is the entry point for "there is a new flag / it behaves differently now".** The rest
> of the skill describes the current version only; the history lives here.
> Every CLI spelling up to 2026.9.14.1 was checked against `xlings <command> --help` on that binary;
> the two newer releases changed no CLI spelling (`src/cli/spec.cpp` and `src/cli.cpp` are untouched
> between `4ea4eac` and `84572b0`).

---

## 0. How to read upstream's own record

The repository has **no top-level CHANGELOG**. Two consequences:

- **GitHub Releases in this window all have empty bodies.** The narrative lives in the **merging
  pull request** and in `.agents/docs/*-release-*-notes.md` inside the repository (not published).
  Any advice of the form "read the release notes" should point at the PR number below.
- Release-to-release ordering is visible with `git log --oneline <old>..<new>`; the clone used for
  this pass is a full clone (721 commits, back to 2024-08-19), so history claims here are checkable
  rather than inherited.

**The release chain from the previous baseline**, in order:

| Version | Commit | PR | One line |
|---|---|---|---|
| 2026.8.30.2 | `f5a0775` | #576 | previous baseline of this skill |
| 2026.9.2.1 | `65b3434` | #577 | version keys are spelled by index identity, not by array order |
| 2026.9.3.1 | `ba51901` | #580 | a shim asserts routing, not state — one derived table, one writer |
| 2026.9.3.2 | `8dfc15b` | #581 | guards judge what the loader would do; every printed remedy runs |
| 2026.9.4.1 | `3c9089b` | #585 | a report says what happened; the library farm is not a blind spot |
| 2026.9.5.1 | `cc3e9e7` [^tag595] | #588 | a destructive repair asks about the payload, not about a path |
| 2026.9.12.1 | `b5bc9c4` | #591 | remove means removed; doctor walks every subos; `local` is an overlay |
| 2026.9.14.1 | `3cd8061` | #596 | a hookless package receives its own archive, not the download directory |
| 2026.9.16.1 | `c4ebafb` | #601 | a region declaration is a preference order, not a selection; one refresh is bounded |
| 2026.9.20.1 | `9f05b70` | #610 | one answerer per question: global scope, install outcome, and the loader |

[^tag595]: Every other row's commit is both the `VERSION` bump **and** where its tag points. This one is
not: `git rev-list -n1 v2026.9.5.1` -> `428e435` (`docs: record the regression surface for 2026.9.5.1`),
the docs commit right after. The bump itself really is in `cc3e9e7`, so the row is right about
provenance — but reverse-looking it up by tag lands you on a pure-documentation commit.

**There were no releases between 2026.9.6 and 2026.9.11** — 2026.9.12.1 is one large merge, which is
why it carries most of the new command surface.
`4ea4eac` (#597) is **not** a release: it only spells xlings' own build dependencies as
`compat.ftxui` / `compat.gtest`, with no user-visible xlings behaviour change. Neither are `5c52a16` (#603) and
`84572b0` (HEAD at this refresh): both are post-release verification notes under `.agents/docs/`.
Those notes (`.agents/docs/2026-09-16-release-2026.9.16.1-notes.md`, `…-2026-09-20-release-2026.9.20.1-notes.md`) are the
closest thing to release notes for the two newer versions; the GitHub Releases bodies are still empty.
**Which xlings an mcpp home runs**: mcpp pins its bundled copy separately (`kXlingsVersion`); at mcpp 2026.9.21.3 that pin is
**2026.9.16.1**. An mcpp-provisioned registry therefore has the region chain and network bounds but **not** the 2026.9.20.1
fixes (#582 shim table, `required` validation, empty-SubOS-name guard, `ldd`) until mcpp moves its pin.

---

## 1. User-visible changes, by version

### 2026.9.2.1 — version key spelling

- **New contract for how a version key is spelled** (`docs/spec/xlings-json-schema.md:70-85`). A
  package from the index **named `xim`** gets a bare key (`2.1.222`); anything else gets `ns:`.
  The decision reads the `index_repos` **entry's name and never its position**, so reordering the
  array — including via `xlings index use` or `config --index-repo` — no longer re-keys installed
  packages. A key's spelling is decided at first write and reused on reinstall or repair.
- **Reads are tolerant both ways**: `xim:2.1.222` finds a record stored as `2.1.222` and vice
  versa; `ns:v` never matches `other:v`.
- **New finding `duplicate version key`** for the damage older clients wrote: bare and prefixed
  keys for the same version with the same `path` are one registration written twice. Readers
  collapse to the owned one, `remove` takes both, and `--fix` merges them across every subos.
  ```bash
  xlings self doctor            # reports "duplicate version key"
  xlings self doctor --fix      # "merged N"; a second run merges 0
  ```
  Upstream measured on a real home: 767 targets that could not be removed, 240 versions registered
  twice, 10 packages both uninstallable and unremovable.
- New error kind `xvm-version-key-spelling`, replacing a misleading `xvm-group-conflict` that
  blamed the recipe.
- **If your first doctor run after upgrading reports duplicate version keys, that is old damage,
  not a new defect** — `--fix` merges it, no reinstall needed.

### 2026.9.3.1 — shims are routing, sub-OS counts split

- **A shim with nothing to say hands the name back to PATH** instead of failing. See SKILL §1.9 —
  this is the change with the largest blast radius for a hermetic toolchain.
- **`MissingShim` + `OrphanShim` merged into one `ShimTableDrift`** finding, levelled by direction
  (missing = Error, stale = Notice), plus a new `ForeignBinEntry` for a real binary in `bin/` that
  is not one of our shims (**reported, never touched**). The routing table is now **derived from
  the workspace** and written by exactly one writer, rather than audited file-by-file.
  The summary counters `missing shims` / `orphan shims` still exist; the per-finding names changed.
  ```bash
  xlings self doctor        # "• shim table  22 stale (brew, cl, lib, ...) — no active version here"
  xlings self doctor --fix  # "· stale shims removed  brew, cl, lib, ..."
  ```
- **Breaking rename in machine output**: `SubosInfo::toolCount` became `commandCount` and a new
  `packageCount` was added. The CLI, agent and NDJSON outputs now emit **`commands`** and
  **`packages`** instead of `pkgCount` [`src/capabilities.cpp:303-304`, `src/core/subos.cppm:60,64`].
  `commands` = routing-table size; `packages` = releases, de-duplicated through `bindingGroup`, so
  one llvm is 1 package and roughly 40 commands. The agent text went from `(N packages)` to
  `(N commands, M packages)`. The read side still falls back to an old `pkgCount`.
  ```bash
  xlings subos list
  xlings interface list_subos    # entries[].commands / entries[].packages
  ```
- `knownProjects` appears in the home config: project **roots** only, so a cached command list
  cannot go stale.

### 2026.9.3.2 — guards stopped answering a weaker question than the one they printed

- **musl toolchains stopped being rejected by a false "loader/libc split".** The family of a core
  soname was classified from the **resolved** name, and musl's `ld-musl-x86_64.so.1 -> libc.so`
  resolves to something with no family marker, which the old code compared against glibc.
  `elf_same_source::check` now applies loader semantics: for each core soname, the **first**
  RUNPATH directory that contains it is the one that answers, later directories do not count.
  Measured upstream (`src/core/elf_same_source.cppm:255-257`): the old rule produced 152 errors and, re-evaluated
  under the loader's rule, **0 of 151 were splits**; `xlings install xim:bun@1.3.11` had been refused outright. **If you are musl-first, this is the release that stops the false refusal.**
- **New `InterpRuntimeDrift` (Notice)**: "this subos declares glibc@X, but N executables in M
  packages start on glibc@Y" — they run, on a payload this subos does not own. No exit-code change,
  and `--fix` does not touch it. For a mixed home this is a useful signal rather than a problem.
- **A printed remedy is now a command you can paste.** Prose moved to a new `remedyNote` line
  [`src/core/xself/doctor.cppm:341-345`], and install suggestions resolve through
  `xvm::recorded_owner` into a real package coordinate, falling back to `xlings search <name>`
  when they cannot (on a real home 218 of 338 program names are not package names, so
  `xlings install g++` was never runnable). Pinned by an e2e contract.
  => An agent **may** now execute a `-> run` line verbatim. Note the corollary: an empty remedy no
  longer means "no package provides this" — read the wording, which now distinguishes "no index has
  it" from "no index was loaded, so nobody could be asked".
- A Rule-B install refusal now fails **one node and continues** instead of killing the whole plan
  with no summary; the exit code follows the failure count.

### 2026.9.4.1 — doctor stopped lying

- **No more `SIGABRT` on a read-only home.** `subos`, `self` and `profile` were dispatched *above*
  the top-level `try`, so the home-config version stamp threw straight out and the process died
  with exit 134 *after* printing a full report. Dispatch moved inside; the stamp returns its
  failure instead of throwing.
  ```bash
  xlings self doctor --fix   # read-only home: exit 0 + one failed "home stamp" line, no core dump
  xlings subos new probe     # read-only home: exit 1 naming the unwritable path, not exit 134
  ```
- **A permission error is reported as a permission error.** `filesystem_error` hints now split:
  `permission_denied` / `read_only_file_system` say "this path is not writable — check permissions
  or point `XLINGS_HOME` somewhere writable"; only the rest suggest filing a bug.
- **A run that pruned registrations no longer prints `OK`.** Exit code deliberately unchanged,
  because it answers "does this home still need a human". See §2 for the verdict line.
- **The dangling-link scan reaches the library farm.** The subdirectory set went from
  `{usr, etc, share}` to **`{usr, etc, share, lib, lib64}`** in both the detection and repair paths
  [`src/core/xself/doctor.cpp:2263,4183`]. On a never-moved home upstream found 3042 links under
  `subos/*/lib*`, six of them dangling and none reported. Repair order also changed: ask the
  versions DB where a link belongs and **re-point** it, delete only when nothing can place it.
  => **After upgrading, expect a batch of new dangling/missing link findings.** That is detection
  surface widening, not fresh damage — particularly on musl-first subos where `lib/` is almost
  entirely links into payloads.
- `SysrootEntry::linkTarget` is now a canonical path, which removed a class of false
  `xvm-sysroot-drift` findings caused by reaching one home through two different paths.
- **`broken payloads N` stopped counting subos-level kinds**; they get their own `subos issues`
  label, so the counter and the list finally agree.

### 2026.9.5.1 — a moved home is diagnosed, not destroyed

- **New `HomeRelocated` finding.** One line replaces hundreds of symptoms. The two destructive
  repair steps (deleting a sysroot link, dropping a registration) now ask **"is this payload present
  under the current root"** instead of "does the recorded path exist"
  [`src/core/xvm/relocation.cppm`]. Detection takes the **modal** store prefix, never the longest
  common prefix. An old root that is still a live independent home does not count as a move.
  ```bash
  xlings self doctor                    # "home relocated  this home is at <new>, but its records were written for <old>"
  xlings self doctor --fix --dry-run    # now plans the local repairs too, instead of skipping them
  xlings self doctor --fix              # re-points records, index caches, subos manifests, every subos's sysroot links
  xlings install <pkg>@<version>        # recover one dropped registration: ~1s, payload already on disk
  ```
- **New `SysrootMissing`**: a link the current selection declares but that is not on disk (deleted
  by an older client) is put back by `--fix`.
- WARNING, version floor: **2026.9.4.1 is strictly worse than 2026.8.30.2 on a moved home** — it
  deletes the dangling links the old symlink workaround could recover. Upstream measured on a 152 GB
  moved home: 1173 sysroot links deleted and 367 registrations dropped while all 234 package
  directories were present. On 2026.9.4.1 specifically: keep a symlink at the old path and **do not
  run `--fix`**. 2026.9.5.1 on the same home deletes exactly what the un-moved home would (24).
- **What this does not change**: relocating a home stays unsupported. `PT_INTERP` is read literally
  by the kernel, linker scripts name absolute paths, and payload contents are never touched; the
  supported answer for a registry-shaped home remains dropping it and re-provisioning. What is
  repairable is the bookkeeping xlings owns.
- **Sandbox detection erratum, recorded in the release verification**: `XLINGS_SUBOS` is **not**
  exported inside `subos use --sandbox`; **`XLINGS_SUBOS_LIB` is**. A check keyed on `XLINGS_SUBOS`
  silently never fires. A GL / direct-rendering check inside the sandbox needs `--gpu` (bwrap only).
- **Release/index ordering lag, pre-existing and worth knowing**: the index snapshot a release
  publishes is cut **before** the index bump it triggers lands, so immediately after a release
  `latest` does not yet resolve to the new version. Settle it with
  `xlings index use xim latest && xlings update` before concluding the release is missing.

### 2026.9.12.1 — the big one

**`remove` gained scope flags** [`src/cli/spec.cpp:24-29`, `src/cli.cpp:1702-1735`]:
```bash
xlings remove <pkg> --all            # every installed version, not just the active one
xlings remove <pkg> --all-subos      # every subos that has it installed
xlings remove <pkg> --subos <NAME>   # that subos only, whether or not it is the current one
xlings remove <pkg> --force -y       # tolerate a missing recipe or a throwing uninstall hook
```
`--subos` wins if both scope flags are given; neither means the current subos, as before. Note the
spelling is `--subos <NAME>`, not `-s`.

**`remove` means removed.** The target now resolves from the *installed* record rather than the
index's latest; hooks are skipped when the recipe is gone; state is rolled back **before** a hook
failure is reported. Without `--force` a hook failure emits `xim.uninstall_hook_failed` and returns
**1**; with `--force` it returns 0 — either way the version record, workspace binding, shim and
payload are already undone [`src/core/xim/commands.cpp:1181-1223`]. Removing a package this subos
does not have is still exit 0 with a Warn (`xim.remove_absent`).
`--force` still does **not** override the detach-only decision: if another subos references the
payload you get a detach, never a delete [`src/core/xim/installer.cppm:568-596`]. Do not sell it as
"delete it for real".

**`self doctor` flags**:
```bash
xlings self doctor --subos <NAME>     # anchor the whole run to one subos (unknown name -> exit 2)
xlings self doctor --show-ok          # new name; --all still works but warns once per run
xlings self doctor --fix              # implies --deep AND walks every subos that owns a finding
XLINGS_DOCTOR_CHILD_TIMEOUT=600 xlings self doctor --fix
```
`--fix` spawns `<client> self doctor --fix --subos <name>` per affected subos; a child carrying
`--subos` does not recurse. Default child timeout **1800s**, `0` disables the bound
[`src/core/xself/doctor.cpp:3220-3237`]; the mechanism is `timeout(1)`, and the bound applies **only
when that binary is on PATH** (`:3249-3255`) — on Windows, stock macOS and minimal containers there is
no bound and a stuck child hangs the parent. A failed child
counts as outstanding, suppresses the `verifiedBy` stamp, and makes the parent exit non-zero.
The **default** (non-`--deep`) report now runs index probes too, so its remedies match `--deep`'s.
An unreferenced broken payload is pruned rather than re-downloaded.
=> Any guidance of the form "enter each subos and run doctor there" is now wrong. Upstream's
numbers on a real home: remedies demanding `subos use X` went 38 -> 0, bogus "no package in any
index provides" 100 -> 3, planned downloads 99 -> ~34 plus 65 prunes.
=> **This is also the most expensive command in the tool.** Run `--fix --dry-run` first and keep
your machine's CPU/IO throttle on the whole invocation; children inherit `nice`, not per-command
variables aimed at a build tool.

**The local recipe overlay became a lifecycle** — SKILL §5.4 has the full story. New verbs
`--list-xpkg` / `--remove-xpkg <NAME>` / `--clear-xpkg <all|stale>`; `--add-xpkg` refuses a copy
byte-identical to the synced index; **`xlings update` now deletes** overlay recipes that have become
byte-identical to it. Upstream's own home went from 159 of 167 overlay recipes down to 2 of 5.

**Hints are said once.** `use` / `install` / `list` / `self update` stopped printing
"run xlings self doctor --fix" on every invocation. The new `xlings.core.notice` module keys a memo
on `(id, fingerprint)` and persists it in `.xlings.json["hintsSeen"]`
[`src/core/notice.cppm`]; upgrading to a newer version announces again, the same state does not.
TTY only, and `self` / `interface` subcommands are excluded. After a clean `--fix` writes
`verifiedBy`, the nag stops entirely.
=> If any of your tooling keys off the presence of that nag to decide health, switch to
`verifiedBy` or the doctor exit code. If it worked around the nag, that workaround is obsolete.

**Home-config writes got safer.** `verifiedBy` was added, and the three near-every-command writers
(`record_client_version` / `record_verified_version` / `mark_hint_seen`) now do their
read-modify-write under the home state lock with a **2-second timeout and a silent skip**
[`src/core/config.cpp:1320,1370-1426`]; `record_client_version` / `record_verified_version` return
`std::expected` instead of throwing (that throw was the read-only-home `SIGABRT`). `save_workspace`
refuses to overwrite a `.xlings.json` it cannot parse instead of treating it as empty.

**New `SubosUnreadable` (Warning).** A `subos/<name>/.xlings.json` that fails to parse used to be
swallowed by `catch(...){}`, which made that subos vanish from every cross-subos question —
reference counting included, so a payload still in use could be deleted. Now:
`xlings list --all` prints a Note naming the subos it could not show, `remove` lists it as
`<name> (unreadable)` when deciding whether a payload is still referenced (i.e. "cannot confirm",
not "confirmed unused"), and doctor reports it with its own counter.

**Failure domain is one package.** A new broken-home fixture pins that five kinds of damage
coexisting leave `list` / `install` / `use` / shim / `doctor` results for *other* packages
unchanged. => Troubleshooting advice of the form "move the broken subos aside first" is no longer
needed. The repair ladder now uses `remove --force`, and "removed but cannot be reinstalled" makes
`--fix` exit 1 without stamping, listing the direct dependants it may have broken.

**semver accepts build metadata.** `25.0.4+7` parses; range resolution selects only among concrete
versions; an alias key is always dereferenced, chained aliases to the end
[`src/core/semver.cppm:116-121` — the `.cpp` is 16 lines of out-of-line member definitions; the parser is in the module interface]. => The old workaround for range constraints against an aliased
publisher (pin the exact non-alias version plus a glob fallback over the payload store) is no longer
required. The `dep_install_dir` half of that report is **still open** — see §3.

**Install-side sysroot refresh reaches every subos pinning that version.** Library placement used to
write into the current subos only and return early for a non-active version, stranding every other
subos on the old value. Partial fix; see §3.

### 2026.9.14.1 — a hookless package receives its own archive

- **What was wrong**: every download landed in the shared `<data>/runtimedir` and was extracted
  there. A package with **no `install()` hook** ends with an empty install dir after hooks, and
  staging then moved that **whole shared directory** into it — other packages' archives,
  `.lock` / `.meta` / `.part.*` sidecars, trees someone else had extracted. Upstream reported (in PR #596; the figure is not
  reproduced in a source comment, so treat it as their measurement rather than something you can
  re-derive from the tree): **221 of 401 version directories carried swept sidecars, 5.2 GiB of
  foreign archives.**
- **What it is now** (`docs/spec/xpkg-manifest-v1.md:158`, spec text, not just behaviour): a package
  that is neither `type = "subos"` nor defines `install()` receives **exactly the entries of its own
  archive, laid out the way the archive lays them out — the top-level directory is KEPT, never
  stripped — and nothing else**; the archive stays in the download cache and is never moved in.
  Staging happens in a private `<runtimedir>/.stage/<sanitized plan key>-<pid>/`
  [`src/core/xim/installer.cppm:405-433`]. A package **with** a hook still extracts beside its
  archive; that is the hook's contract. A hook that leaves the install dir empty also gets a private
  extraction.
- **New `SweptPayload` finding (Error)**, recognised through `xim::swept_payload_marker`
  (a zero-length `<name>.lock` with a same-named sibling, a `<name>.meta` sidecar, or a top-level
  entry ending in a download/archive extension). `--fix` **skips the cheap "install alone" rung and
  goes straight to remove-then-install**, because a swept payload already reads as correctly
  installed [`src/core/xself/doctor.cppm:263-273`].
  ```bash
  xlings self doctor --deep     # look for swept payloads
  xlings self doctor --fix      # repairs via remove + install (downloads; throttle it)
  ```
- **Two consequences for anyone with a home built on 2026.9.12.1 or earlier**:
  1. Run `self doctor --deep` once after upgrading. Contamination is invisible to normal use and
     costs real disk.
  2. **The disk model changed**: archives now live permanently in the download cache. On btrfs with
     snapshots, freeing them will not show up in `df` until snapshots rotate.
- Descriptors that reach into an extracted tree by path (`"*/…/mcpp.toml"` and similar) depend on
  the kept top-level directory. That is now written down, so it can be relied on.

### 2026.9.16.1 — a region is an order, and a refresh has a budget (#601; closes #598, #599, #600)

- **Region objects are ordered candidate chains** (`parse_region_chain`, `src/core/config.cpp:30`).
  `index_repos[].artifact`, `xim.index-base` and a sub-index's `["artifact"]` all read as: the `mirror`
  region first, then GLOBAL, then the rest in declaration order. A pointer or asset fetch that fails
  (403, 429, offline) moves to the next base; git comes only after the whole chain. Before, the object
  collapsed to one base, so `mirror = CN` plus one GitCode 403 became a GitHub `git clone`.
  `xim.mirrors.index-repo` and sub-index git URLs still take only the first entry (a git remote).
  An exhausted `xim.index-base` chain never falls back to the official server.
- **Pointer file names are derived per base** (`<last segment>-pointers.json`); a region object now
  round-trips through `xim-indexrepos.json` instead of being written back as the one region used.
- **Sub-indexes can declare their own artifact source** in the default index's `xim-indexrepos.lua`:
  ```lua
  ["awesome"] = {
      ["GLOBAL"]   = "https://github.com/openxlings/xim-pkgindex-awesome.git",
      ["CN"]       = "https://gitee.com/d2learn/xim-pkgindex-awesome.git",
      ["artifact"] = { ["GLOBAL"] = "https://github.com/xlings-res/awesome-index",
                       ["CN"]     = "https://gitcode.com/xlings-res/awesome-index" },
      ["source"]   = "auto",
  }
  ```
- **Visible order**: `xlings index list` prints `artifact: <url> [CN]` then `then: <url> [GLOBAL]`;
  `index list --json` and interface `list_repos` carry `artifact_bases[]{region,url}`.
- **Bounded refresh** (#599, an 11.5-minute stall behind a completed handshake):
  ```bash
  XLINGS_UPDATE_TIMEOUT=900 xlings update          # whole-update budget, default 300 s, `off` = none
  XLINGS_INDEX_HTTP_TIMEOUT=20:300 xlings update   # index HTTP <connect>:<per attempt>, default 10:120
  XLINGS_GIT_NETWORK_TIMEOUT=120 xlings update     # git low-speed window, default 60 s
  ```
  git also gets `GIT_TERMINAL_PROMPT=0`; operator-set `GIT_*` values are never overwritten. Past the
  budget, remaining sources are skipped with
  `[index] 300s refresh budget reached: N source(s) were not refreshed and keep their local copy`.
- #600 was answered, not "fixed": registered sub-indexes under `mirror = CN` were already served from
  GitCode artifacts; the GitHub URL in the json is the declared source (and git fallback), not the path
  taken. The two real gaps it exposed (sub-index artifact declaration, invisible order) are the two
  bullets above.
- Known after release, fixed in 2026.9.20.1: `self update` printed "still resolves to <old>" one line
  before switching (#602).

### 2026.9.20.1 — one answerer per question (#610; closes #582, #604, #606, #602, #464, #376, #608, #611)

- **Global shim table no longer emptied from project scope** (#582, #604). `load_global_workspace_()`
  used "the SubOS this command acts on" (the project's, inside a project) to answer "which SubOS is
  global", read an absent or foreign workspace, and the derived shim table then removed every global
  entry. Now `Config::global_subos_name_()` is the one answer, and "could not read" is distinct from
  "empty": absent SubOS directory = not observed; directory without a workspace file = observed and empty
  (a fresh SubOS); unreadable file = not observed. `sync_shim_tables` refuses to rebuild from an
  unobserved scope. `self init` now rebuilds the whole derived table and reports
  `routing table: +N -M shim(s)` when it changed something; `install`/`use` in global scope and
  `self update` repair it too. Upstream's real home went from 149 to 321 shims in `subos/default/bin`.
- **Install outcome is one record** (#606, #376): the "installed, but 'X' still resolves to Y" notice,
  the structured error, the summary and the exit code all read the per-node record. Extraction errors
  keep their kind on the wire (`E_INVALID_INPUT` for a corrupt archive, `E_DISK_FULL` for a write
  failure). `N package(s) installed` counts `Installed` only, not `AlreadyPresent`.
- **`self update` passes `--use`** (#602), so the child owns the switch and never prints the stale
  notice. The hop *into* 2026.9.20.1 is executed by the previous binary and prints it once more.
- **`interface` validates params** (#464, #611): invalid JSON / non-object `--args` refused for every
  capability; missing or `null` `required` fields refused where declared (12 of 20); `E_INVALID_INPUT`,
  exit 1, capability not executed. `--args ""` = `{}`; unknown fields still accepted.
  `subos::create` / `subos::remove` refuse an empty name on their own (the `{"name":""}` path).
  ```bash
  xlings interface plan_install --args '{"packages":["cpp"]}'
  # {"kind":"error","code":"E_INVALID_INPUT","message":"missing required field(s): targets",...}
  # {"kind":"result","exitCode":1}
  ```
- **`ldd` in a SubOS runs the file's own `PT_INTERP`** (#608, refs #522) with `LD_TRACE_LOADED_OBJECTS=1`
  and ldd's flags mapped to loader environment; no-`PT_INTERP` inputs fall through to the packaged
  script. See SKILL §1.10.
- Withdrawn before release, worth knowing so nobody re-proposes it: an install-time "every registered
  shell script must parse" gate. It rejected `pip`/`pip3`, which are deliberate sh/python polyglots
  that `exec` away on line 2, and would have broken `xlings install python` everywhere.
- Upstream's own release lesson: `verify-release.sh` read git `main` and was green while the published
  index pointer still resolved `latest` to 2026.9.16.1, so the first `self update` attempts were
  no-ops. After a release, resolve `latest` the way a client does (`xlings update`, then read
  `data/xim-pkgindex/pkgs/x/xlings.lua`) before declaring it available.

---

## 2. Short "changed in `<ver>`" history

One line per behaviour that genuinely flipped since 2026.8.30.2. Everything in the body of this
skill describes the **current** version; this list is what to say when someone reports the old one.

- **changed in 2026.9.2.1**: whether a version key carries `ns:` is decided by the index entry's
  *name*; before that it was decided by `index_repos` position, so reordering the array re-keyed
  installed packages and produced unremovable targets.
- **changed in 2026.9.3.1**: a shim whose scope makes no claim on the name execs the host's copy and
  exits 0; before that it printed "`<name>` is not installed in this subos" and exited 1.
- **changed in 2026.9.3.1**: subos counts are `commands` + `packages`; the JSON key `pkgCount` is
  gone from the write side (still accepted on read).
- **changed in 2026.9.3.2**: `Finding::remedy` holds a command only; prose moved to `remedyNote`.
  Before that, remedies could carry placeholders and prose and were not safe to execute.
- **changed in 2026.9.3.2**: a Rule-B install refusal fails one node; before that it aborted the
  whole plan with no summary.
- **changed in 2026.9.4.1**: the dangling-link scan covers `lib/` and `lib64/`; before that
  `{usr, etc, share}` only, so the library farm was a blind spot.
- **changed in 2026.9.4.1**: a `--fix` that pruned registrations prints a `status` line instead of
  `OK`. The exit code deliberately did not change, so **reading `$?` alone is not enough.**
- **changed in 2026.9.5.1**: the destructive repairs ask whether the payload is present under the
  current root; before that they asked whether the recorded path existed, which is why 2026.9.4.1
  was destructive on a moved home.
- **changed in 2026.9.12.1**: `remove` acts on the installed record with explicit scope flags, and
  rolls state back even when the uninstall hook throws; before that a failing hook wedged the
  package and removal was per-subos, active-version only.
- **changed in 2026.9.12.1**: `self doctor --fix` walks every subos itself; before that it told the
  user to enter each subos and run it there.
- **changed in 2026.9.12.1**: `--all` on `self doctor` means `--show-ok` and warns; it used to be
  the flag's only name.
- **changed in 2026.9.12.1**: `xlings update` deletes local overlay recipes that match the synced
  index byte for byte; before that it was a read-only sync and the overlay only grew.
- **changed in 2026.9.12.1**: the "run `self doctor --fix`" hint is printed once per
  (id, version) and persisted in `hintsSeen`; before that it printed on nearly every command.
- **changed in 2026.9.14.1**: a package without `install()` receives only its own archive's entries
  with the top-level directory kept; before that it received the whole shared download directory.
- **changed in 2026.9.16.1**: a `{GLOBAL, CN}` region object is an ordered chain tried base by base
  before git; before that it resolved to one base and a failure went straight to git.
- **changed in 2026.9.16.1**: `xlings update` has a 300 s total budget and bounded git/HTTP steps;
  before that one stalled connection could block it indefinitely.
- **changed in 2026.9.20.1**: a project-scope install no longer empties the global shim table; before
  that it could remove every global command name (#582).
- **changed in 2026.9.20.1**: `interface` refuses malformed params and missing `required` fields with
  `E_INVALID_INPUT` / exit 1; before that such a request ran with defaults and usually exited 0.
- **changed in 2026.9.20.1**: `self update` = `install xlings@latest -y --use`; a failed install no
  longer prints the "still resolves to" notice.
- **changed in 2026.9.20.1**: SubOS `ldd` follows the file's `PT_INTERP`; before that it used the
  packaged loader list for every file, host binaries included.

---

## 3. Still open on 2026-09-23 — do not document these as fixed

Checked with `gh issue view` / `gh issue list` on 2026-09-23. Upstream ran a full triage of its open
issues on 2026-09-20 (openxlings/xlings#609, against 2026.9.16.1); the 2026.9.20.1 merge closed eight
more the same day.

**Closed since the previous baseline, with upstream's stated reason** (the ones this file used to list as open):

| Issue | Closed | Upstream's basis |
|---|---|---|
| #582 | 2026-09-20, fixed in 2026.9.20.1 | global SubOS answered once; unreadable != empty (§1, 2026.9.20.1) |
| #586 | 2026-09-20, triage #609 | install-side refresh reaches every SubOS pinning the version, doctor walks every SubOS (2026.9.12.1). The previous baseline held it "not yet impossible"; upstream judged it fixed without a new reproduction either way |
| #590 | 2026-09-20, triage #609 | build metadata parsed, alias chains dereferenced (8 hops, cycle-guarded), range resolution picks concrete versions only (2026.9.12.1). The previous baseline kept a `dep_install_dir` half open; upstream closed the whole issue - re-measure before relying on either reading |
| #579 | 2026-09-20, triage #609 | namespace stripped before the entry-binary comparison; `local` alone treated as non-index (2026.9.3.2) |
| #602, #604, #606, #464, #376, #608, #611 | 2026-09-20, fixed in 2026.9.20.1 | see §1 |

**Still open:**

| Issue | What still happens | Practical note |
|---|---|---|
| **#584** | A `subos.env{}` declaration made in `config()` is logged as recorded but never lands in `subos_info.envs` | Graphics discovery variables (`LIBGL_DRIVERS_PATH`, `XDG_DATA_DIRS`, `__EGL_VENDOR_LIBRARY_DIRS`, `OCL_ICD_FILENAMES`) never reach a consumer. Upstream's triage: the write path reads correctly, needs a reproduction first |
| **#593** | The 2026.9.12.1 verbs are **CLI-only** — no `interface`/capabilities parity | If you drive xlings through the agent/NDJSON protocol, `remove --all/--all-subos/--subos`, `config --list/remove/clear-xpkg` and `doctor --subos/--show-ok` are unreachable. 2026.9.20.1 added validation to the channel, not these verbs |
| **#592** | The 2026.9.12.1 e2e contracts have no PowerShell port, and the doctor child timeout only applies where `timeout(1)` is on PATH | Windows behaviour of `--fix`'s child walk is correspondingly less pinned — and so is **stock macOS / any minimal container**, which ship no `timeout` either and therefore get no bound at all |
| **#594** | `XLINGS_LOCK_TIMEOUT` is restored as empty rather than unset after the doctor helper clears it | No observable effect today |
| **#607** | `subos runtime`: after a rebind to a version line the declaration and the view disagree; a successful rebind prints `[error]` + `failed to activate`; `self init` declares a runtime without installing it | Read `subos info` after a rebind instead of trusting the message |
| **#522** | historic `glibc@2.39` payloads carry a corrupted `ldd` script | Reinstall the package; 2026.9.20.1 takes that script off the path for files with a `PT_INTERP` |
| #532, #534, #540 | graphics stack: RUNPATH of SubOS-built artifacts covers only glibc/gcc payloads; surfaceless EGL offscreen rendering; build-side consumption by label | Matter only for GPU/graphics work inside a SubOS |
| #564, #566, #571, #153, #417, #458, #425 | entry binary silently falling back to a `local:` build (seen once); four hand-built `ExecutionContext`s; Windows archive names round-tripped through the ANSI code page; macOS fail-open without `install_name_tool`; HEAD freshness probe always 401 on GitCode; doctor blind to SubOS paths baked into payloads; no "newer xlings available" notice | Upstream's residual list in #609 |

Two things **upstream itself recorded as unfinished**, so do not report them as defects you found:

- The per-finding remedy for `ForeignPayload` still prints
  `xlings subos use X && xlings self doctor --fix` [`src/core/xself/doctor.cpp:1365`] rather than
  the shorter `--fix --subos X` that now exists. The printed line works.
- #593 above is upstream's own note about the parity gap.

---

## 4. Cross-repository note

`xlings`' own `mcpp.toml` used to write `ftxui` / `gtest` without a namespace, which means
`mcpplibs`, while both are published under `compat`. mcpp reached them only through its deprecated
bare-name search, and mcpp's index-refresh decision does not walk that search — so it judged the
dependency missing locally and ran a network `xlings update` on nearly every plan or build starting
more than two minutes after the last successful refresh. Fixed in `4ea4eac` (#597) on the xlings
side; the engine-side half was fixed in **mcpp 2026.9.16.1** (#648: the refresh decision now walks the same
deprecated bare-name rung the resolver does, and a refresh is bounded by `[index] refresh_timeout`).
=> **Worth grepping your own manifests**: an unqualified dependency name that actually lives in
`compat` turns into a network `xlings update` on nearly every build, which an editor planning in the
background meets as an unbounded wait. Verify with `MCPP_OFFLINE=1 mcpp emit build-database
--format json -v` — no refresh decision and no bare-name warning.
