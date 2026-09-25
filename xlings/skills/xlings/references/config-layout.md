# Reference: xlings configuration, directory layout, and installation state

> Baseline xlings source `main @ 4ea4eac` / `2026.9.14.1`, dated 2026-09-16; the region-chain, sub-index artifact and
> workspace-observation passages were refreshed against `main @ 84572b0` / `2026.9.20.1` on 2026-09-23 (source only).
> The authority for the project/global schema is the **parser implementation** (`src/core/config.cpp`),
> not `docs/spec/xlings-json-schema.md` (which has omissions; see §2 and `upstream-doc-gaps.md`).
> **Exception, and a real one**: the version-key spelling contract added in 2026.9.2.1 lives in
> `docs/spec/xlings-json-schema.md:70-85` and is written as a contract, not a description — §5 quotes
> it. New keys and behaviour since the previous baseline are listed in `version-notes.md`.

## 1. Global config file

**Path derivation** (`Config::Config()`, `src/core/config.cpp:488-531`), four levels:

| Level | Source | Evidence |
|---|---|---|
| 1 | `home_override_()` injection (shim owner-anchoring, called **before** construction; shims take this path and **ignore the environment**) | `:492-495`; `src/main.cpp:54-59` |
| 2 | Environment variable `XLINGS_HOME` | `:491,496-497` |
| 3 | **Self-contained probe**: the **parent of the executable's own directory** (the `<root>` of `<root>/bin/xlings`) holds both `.xlings.json` and `bin/xlings` | `:499-528` (on Windows the json must additionally carry both `version` and `activeSubos`, `:515-523`) |
| 4 | `<system home>/.xlings` | `:531` |

The filename is fixed at `<homeDir>/.xlings.json` (a separate implementation `home_config_path()` lives at
`src/core/home_config.cpp:10-12`).
WARNING: the extra Windows requirement is explained in the source. Shims are hard links/copies rather than symlinks,
`get_executable_path()` returns the shim path inside the subos directory, and that directory holds **both**
`.xlings.json` and `bin/xlings.exe`, so it would falsely match self-contained mode.

**This one file carries three different things at once**: user preferences + the installed version database
(`versions`) + the subos registry.

| Field | Type | Default | Semantics | Read at |
|---|---|---|---|---|
| `activeSubos` | string | `"default"` | globally active subos name | `config.cpp:541-543` |
| `mirror` | string | `""` (empty is handled as GLOBAL) | region; `"CN"` switches the default index URL. **Read without normalization, case-sensitive** | `:545-546` |
| `lang` | string | `""` | UI language | `:547-548` |
| `uiMode` | string | `""`=auto | `cli`/`tui`/`auto` | `:896-897` |
| `theme` | string | `""`=built-in | bare name -> `<home>/config/themes/<name>.json`; contains `/`, `\`, `.json`, or starts with `.` -> treated as a path | `:898-899` |
| `tui.interactive` | bool | `nullopt` | only meaningful for the tui frontend; **defaults to false, interaction is opt-in** | `:903-907` |
| `versions` | object | `{}` | **global version database**, see §5 | `:804-805`, write `:1269` |
| `index_repos` | array | built-in default | see §4 | parsing `:33-61` |
| `xim.index-repo` | string | built-in constant fallback | default index git address (**only actually read since #575**) | `:140-164` |
| `xim.mirrors.index-repo.<REGION>` | object | — | per region, **takes precedence over the flat `index-repo`** | `:150-160` |
| `xim.index-base` | string \| `{GLOBAL,CN}` | `""` | artifact pointer / asset base | `:126-138` |
| `XLINGS_RES` | object\|string\|array | `{GLOBAL:github/xlings-res, CN:gitcode/xlings-res}` | resource servers; keys `default/DEFAULT/_default` normalize to `DEFAULT` | `:219-223`; defaults `:119-124`; normalization `:199-203` |
| `resource_server(s)` / `res_servers` / `xim.mirrors.res-server` | same as above | — | compatibility path used **only when `XLINGS_RES` is absent** | `:227-257` |
| `mirror_fallback` | string | `auto` | GitHub proxy fallback mode (**deliberately bypasses Config**) | `src/core/mirror/expand.cpp:49` |
| `hintsSeen` | array\<string\> | `[]` | cross-run memo of one-time notices; **key = `<id>\x1f<fingerprint>`** since 2026.9.12.1, so an upgrade to a newer version says its piece again | read `:929`, write `:1414-1430` |
| `version` | string | `""` | the xlings version that **created or last wrote** this home — moves on every `self install`/upgrade whether or not anything was checked | read `:1363`, write `:1370-1380` |
| `verifiedBy` | string | absent | **(new in 2026.9.12.1)** the client version of the last `self doctor --fix` that converged with **nothing outstanding**. The migration hint at the end of a doctor report is gated on `verifiedBy != current version`, so this is the field to read when deciding "has this home been checked by this client" | read `:1391`, write `:1398-1409`; stamped only when `outstanding == 0` |
| `knownProjects` | object | `{}` | **(new in 2026.9.3.1)** absolute project path -> `{lastSeen}` for every project that has installed in project scope. **Paths only, deliberately** — command names are recomputed from each project's own state file whenever the shim table is rebuilt, so a cached list cannot go stale | read `:1452`, write `:1487` |
| `subos` | object | `{"default":{"dir":""}}` | subos registry (existence check) | `xself/init.cpp:364-369` |
| `repo` / `need_update` | string / bool | — | WARNING: **written, never read** (`xself/install.cpp:114,118` and `tools/linux_release.sh:113` write it; zero readers inside `src/`) | — |

WARNING: `knownProjects` records **absolute** paths. Move a project directory and its old entry
becomes junk; it retires on its own at the next rebuild, because a project state file that cannot be
read contributes no command names.

**Writes fall into three classes** (it was two at the previous baseline):

- **Locked read-modify-write** via `update_home_config()` (`home_config.cpp:30-46`, lock files `<home>/.xlings.lock`
  + `.xlings.lock.owner`, `xvm/lock.cpp:16-22`): `xlings config --*`, repo add/remove, `index use`,
  subos add/remove/modify, `self migrate`.
  **collect-then-replay**: edits are collected first, then replayed onto a document **re-read** under the state lock
  — replaying onto the copy taken at read time would write every other key back the way it looked
  before some concurrent install.
- **Locked, but best-effort** (new in 2026.9.12.1, `rmw_home_config_locked_`, `config.cpp:1320`): the three
  near-every-command writers `record_client_version` (`:1370`), `record_verified_version` (`:1398`) and
  `mark_hint_seen` (`:1414`). They take the same home state lock with a **2-second timeout** and, if they cannot get
  it, **skip the write silently**. The reasoning in the source is worth keeping: `list` and `use` now call
  `notice::notice_once` on nearly every invocation, and a `list` racing an `install`'s own read-modify-write of this
  file was a plain lost update over the **versions DB**, not just over the field the writer meant to touch — so the
  lock is mandatory, but a lost hint is an inconvenience while a lost `versions` entry is not.
  `XLINGS_LOCK_TIMEOUT` is temporarily cleared for that one acquisition and restored immediately, so a machine that
  legitimately waits ten minutes for a long install does not inherit that wait here.
  These two also changed shape: `record_client_version` / `record_verified_version` return `std::expected` instead of
  throwing, which is what used to abort the process on a read-only home (`config.cppm:607-613`).
- **Unlocked direct writes** (comments say legacy, or they rely on the caller holding the lock): `save_versions()`
  (`config.cpp:1246`), `ensure_home_config_defaults_()` (`xself/init.cpp:348-372`),
  `set_mirror_fields_` (`xself/install.cpp:100-119`).

`save_workspace` (`config.cpp:1503`) now **refuses to overwrite** a subos `.xlings.json` it cannot
parse, instead of treating it as an empty document — blanking it would discard `subos_info`, envs and
everything else that write does not own (`:1561-1577`).
`home_config.cppm:8-51` carries a full explanation of why locking is mandatory (lost updates +
`versions`/`workspace` tearing).
=> **Practical consequence**: a command that only reads can still touch this file (version stamp,
`verifiedBy`, `hintsSeen`, `knownProjects`). If a home sits next to a working tree you check for
cleanliness, expect that.

## 2. Project `.xlings.json`

**The parser recognizes only 12 keys** (`load_project_config_from_dir_`, `config.cpp:601-709`).
**No `deps`, no `toolchain`, no `index`.**

| Field | Default | Semantics | Line |
|---|---|---|---|
| `projectScope` | `true` | **returns immediately when `false`**: does not set `hasProjectConfig_`, does not export `XLINGS_PROJECT_DIR`, does not activate the project subos | `:641-645` |
| `mirror` | inherits global | **overrides** global | `:653-654` |
| `lang` | inherits global | overrides | `:655-656` |
| `uiMode` / `theme` / `tui.interactive` | inherits global | overrides; **a relative theme path resolves against the project root** | `:659-661` |
| `workspace` | `{}` | tool versions declared by the project (the target of a bare `xlings install`) | `:662-663` |
| `index_repos` | `[]` | project-level index repos, **replaces** the global list | `:665` |
| `XLINGS_RES` (+3 legacy names) | inherits global | project-level resource servers | `:666` |
| `xim.index-base` | inherits global | **project overrides global** | `:667` |
| `subos` | `""` | named project subos (legacy name `projectSubos` still recognized) | `:668`, `:273-283` |
| `versions` | `{}` | project-level version DB, read **only when `.xlings/.xlings.json` has no `versions`** | `:682-686` |

WARNING: the project field table at `docs/spec/xlings-json-schema.md:240-251` **omits `versions` and `xim.index-base`**.
The global table (`:21-33`) is worse: it omits `subos`, `repo`, `need_update`, `mirror_fallback`, every `xim.*` key,
and both keys added since — `verifiedBy` and `knownProjects` — **and it attributes the `--fix` stamp to `version`**,
which is now `verifiedBy`'s job. Treat both tables as samples, not inventories.

**How project mode is triggered** (`load_project_config_()`, `config.cpp:711-800`):
1. Search **upward level by level** from `fs::current_path()` for `.xlings.json` (`:765-779`).
2. If the matched level has `is_directory(dir/"subos")`, treat it as an xlings home and **break out of the upward walk**
   (`:760-763,768-770`; full reasoning in the comment above: a nested home would mistake an outer
   `<xlings home>/.xlings.json` for a project root and route every install/shim/workspace path into a phantom
   `<xlings home>/.xlings/{subos,data}` tree).
3. A match with `projectScope != false` sets `hasProjectConfig_`, `projectDir_`, and
   `set_env_variable("XLINGS_PROJECT_DIR", dir)` (`:646-651`). `projectScope:false` -> **keep walking up** (`:774`).
4. Nothing matched -> fall back to the `XLINGS_PROJECT_DIR` environment variable (**with the same `subos/` boundary
   detection**), `:782-798`.

**Paths derived in project mode** (`config.cpp:330-353`):
```
<projectDir>/.xlings.json               project manifest (user-authored)
<projectDir>/.xlings/                   project_home_dir_
<projectDir>/.xlings/.xlings.json       project_state_path_ (where the anonymous subos lands workspace/versions)
<projectDir>/.xlings/data/              project_data_dir_
<projectDir>/.xlings/subos/<name>/      named project subos
<projectDir>/.xlings/subos/_/           anonymous project subos
```
`effective_data_dir()` switches to the project data directory **only when the project declares `index_repos`**
(`:1015-1021`; `index_repos()` behaves the same, `:1031-1037`).

**`workspace` merge order** (`merged_workspace`, `:846-864`): Named = project manifest <- project subos file;
Anonymous = global <- project manifest <- project subos file. But the **write target** returned by
`workspace()`/`workspace_mut()` is not the merged result: both modes point at `projectSubosWorkspace_`
(`:1154-1168`; the two function bodies are deliberately identical, reasoning at `config.cppm:484-494`).

**Two questions, two answerers (2026.9.20.1, #582 / #604; `docs/design/xvm-version-management.md`)**: "which SubOS does
this command act on" is `resolve_subos_scope_()` -> `paths_.activeSubos` (inside a project: the project's `_` or named
SubOS); "which SubOS **is the global one**" is `Config::global_subos_name_()` (override > `XLINGS_ACTIVE_SUBOS` > the
home's `activeSubos`, **never** a project SubOS). Up to 2026.9.16.1 `load_global_workspace_()` used the first to answer
the second, so inside a project the global workspace read as empty. And reading a workspace is now **three-state**:
SubOS directory absent = not observed; directory present without a workspace file = observed and empty (a fresh SubOS);
file present but unreadable = not observed (`read_workspace_file_()` returns `std::optional`,
`global_workspace_observed()` carries it). The derived shim table refuses to rebuild from an unobserved scope, because
a derived table fed "nothing" derives "remove everything" - which is exactly how 172 global command names disappeared on
one home.

## 3. `$XLINGS_HOME` directory layout

Authoritative source `ensure_home_layout()`, `src/core/xself/init.cpp:392-440`:

```
$XLINGS_HOME/
├── .xlings.json                        global config + versions + subos registry
├── .xlings.lock / .xlings.lock.owner   home-level state lock + owner sidecar        xvm/lock.cpp:16-22
├── bin/                                where shim hard links land                   init.cpp:400
├── config/
│   ├── shell/xlings-profile.{sh,fish,ps1}                                           init.cpp:401, 439-440+
│   └── themes/<name>.json              on demand, not created by init
├── data/
│   ├── xpkgs/                          package payload store                        init.cpp:402
│   ├── trash/                          staging for files that cannot be moved on uninstall (**sibling of xpkgs**) payload.cpp:333
│   ├── runtimedir/                     download cache; **archives now stay here permanently** (2026.9.14.1)  init.cpp:403
│   │   └── .stage/<plan key>-<pid>/    private per-install staging for a hookless package (2026.9.14.1)  installer.cppm:405
│   ├── xim-pkgindex/                   default index (constant directory name)      config.cppm:108
│   ├── <name>/                         other index_repos entries                    config.cpp:1039-1044
│   ├── xim-index-repos/                sub-index root                               init.cpp:404
│   │   ├── xim-indexrepos.json         manifest of synced sub-indexes               init.cpp:434
│   │   └── <url_to_dirname>/           one directory per sub-index                  repo.cpp:416-418
│   ├── xim-pkgindex-local/             local recipe overlay for `config --add-xpkg`; since 2026.9.12.1 also
│   │   ├── pkgs/<letter>/*.lua           listable/clearable and GC'd by `update`    commands.cpp:2187, overlay.cpp:100
│   │   └── .overlay.json               provenance; an entry without a record reads as `source = untracked`
│   ├── local-indexrepo/                created by init, no other reader/writer in src/ (**probably legacy**) init.cpp:405
│   └── github-mirrors.json             user override of the proxy mirror table (optional, whole-table replace) mirror/registry.cpp:138
└── subos/
    ├── current -> subos/default        directory link                               init.cpp:421-422
    └── <name>/{.xlings.json, bin/, lib/, usr/, generations/, tmp/, home.img}        init.cpp:406-409
```
WARNING, **the disk model changed in 2026.9.14.1**: an archive is no longer moved into the install
directory, so `runtimedir` keeps a copy of everything ever downloaded. Budget for it. On btrfs with
snapshots, deleting from it will not move `df` until snapshots rotate.
Temporary forms under `data/`: `<destIndexDir>.artifact.<pid>` (`indexfetch.cpp:557-559`), `.old.<pid>` (`:600`),
`.tmp.<pid>`, reclaimed by `reconcile_index_temps()` (`:645-700`). `display_path()` renders the home prefix as
`@xlings/...` (`config.cpp:870-886`) — a different thing from the `${XLINGS_HOME}` placeholder used for **storage**
inside `versions`.
WARNING: **two unverified items**. `subos.<name>.dir` — written only via the NDJSON capability `create_subos`'s
optional `dir` input (`src/capabilities.cpp:344`, "Optional custom directory; defaults to
`$XLINGS_HOME/subos/<name>`"), which reaches `customDir` (`src/core/subos.cpp:521` signature) and is stored at
`src/core/subos.cpp:684-685`; **there is no `subos new --dir` flag** (`xlings subos new --help` lists only
`--storage` / `--image-size` / `--from` / `--runtime`, and `grep -rn '"--dir"' src/` is empty) — has **no
reader** on the path-resolution side: `Config::subos_dir()` unconditionally returns `homeDir/"subos"/name`
(`config.cpp:1212-1214`). And the nested `<home>/.xlings` path that `xlings self clean` deletes has no creator inside `src/`.

## 4. Package landing, naming rules, and `index_repos`

**The single constructor** `package_store_name()` (`src/core/xim/catalog.cpp:22-25`): `<ns>-x-<name>`, degenerating to
the bare name when the namespace is empty. **Full landing path = `<dataDir>/xpkgs/<ns>-x-<name>/<version>/`** (catalog
decides `:461`; installer executes `installer.cpp:197,943`; reverse-parse `xvm/owner.cppm`). An empty `storeRoot`
always falls back to `dataDir/"xpkgs"`.

WARNING: **the three spellings order their parts differently** (`xvm/owner.cppm` warns about this explicitly):
the version directory name is the **bare version without the ns** (the store directory itself is
`<ns>-x-<name>`, `installer.cpp:887-888` -> `package_store_name`), the **key** in the xvm version
DB carries the ns as `ns:version` (`installer.cpp:899-912` `version_namespace_`, applied at `:914-948`
`effective_version_namespace_`), and the command-line coordinate is a third form,
`ns:package@version`. Whether that key actually carries the `ns:` prefix is the **contract** in §5.

**What the install directory receives** (spec since 2026.9.14.1, `docs/spec/xpkg-manifest-v1.md:158`):

| Recipe shape | What lands in `pkginfo.install_dir()` |
|---|---|
| defines `install()` | whatever the hook puts there; extraction happens beside the archive, which is the hook's contract |
| `type = "subos"` with no hook | the built-in default (skeleton directories + xvm registration) |
| **neither** | **exactly the entries of that package's own archive, laid out the way the archive lays them out — the top-level directory is KEPT, never stripped — and nothing else.** The archive itself stays in the download cache and is never moved in |

Before 2026.9.14.1 the third row was not true: everything was extracted in the shared
`<data>/runtimedir` and the whole directory was moved in, so a hookless package received other
packages' archives and sidecars (upstream measured 221 of 401 version directories contaminated, 5.2
GiB of foreign archives). Staging is now private, `<runtimedir>/.stage/<plan key>-<pid>/`
(`installer.cppm:405-433`), and the "strip a single top-level directory" branch was deleted.
=> Descriptors that reach into an extracted tree by path can rely on the kept top-level directory.
=> To find pre-existing contamination: `xlings self doctor --deep` reports `SweptPayload`; `--fix`
repairs by remove-then-install.

**payload = the version directory itself** (`src/core/xim/payload.cppm` + `payload.cpp`):

| Concept | Landing path / criterion | Evidence |
|---|---|---|
| install stamp | `<payload>/.xpkg-install.json`, fields `os`/`version`/`xlings_version`/`registered` (optional) | constant `payload.cppm:26` |
| failure marker | same file, appending `incomplete: true` + `reason` (truncated to 200 chars) | `payload.cpp` |
| "has content" test | any entry besides `.xpkg-install.json`; **`.xim-installed` is deliberately not excluded** (wrapper packages use it to mean "installed but nothing here") | `payload.cppm:34-40` |
| **swept-payload marker** | a zero-length `<name>.lock` with a same-named sibling, a `<name>.meta` sidecar, or a top-level entry ending in a download/archive extension — i.e. the fingerprint of the pre-2026.9.14.1 sweep | `payload.cppm:72`, `payload.cpp:83` |
| platform attribution | read `os` from the stamp first; with no stamp, sample at most 8 files for ELF/MZ/Mach-O magic | `payload.cpp:19-38,71-110` |
| recipe snapshot | `<payload>/.xpkg.lua` | `installer.cpp` |
| staging when deletion fails | `<...>/data/trash/<pkgdir>-<version>[-n]/`, **must be a sibling of `xpkgs`** (otherwise 7 different "treat subdirectories as versions" scans misread it) | `payload.cpp:333`, reasoning `payload.cppm:150-165` |

WARNING: the distinction between `registered` and `kRegisteredUnrecorded = -1` matters (`payload.cppm:51-59`): `-1`
means the stamp predates the field, **not 0**; `0` means the package declares that it registers nothing (legitimate for
wrapper/meta packages).

**Multiple coexisting versions**: one subdirectory per version under the same `<ns>-x-<name>/`
(`installer.cpp:3940-3945`); the package directory is only scanned for emptiness when the last version is uninstalled
(`:3947-3964`); `profile::gc` walks the two levels `<pkgName>/<ver>`.

### `index_repos` entry fields (`config.cppm:43-53` + parser `config.cpp:29-61`)

| Field | Required | Semantics | Default |
|---|---|---|---|
| `name` | yes | **decides three things at once**: directory, namespace, and pointer key; missing/empty skips the whole entry | — |
| `url` | yes | missing/empty skips the whole entry | — |
| `artifact` | no | string \| `{GLOBAL,CN}`, artifact base URL | `""` = git only |
| `source` | no | `"" \| "auto" \| "artifact" \| "git"`, per-repo override of the global setting | `""` |
| `version` | no | #476 snapshot pin, **not validated at all** (the version namespace belongs to the index publisher) | `""`/`latest` = automatic routing |

- **Region object parsing** - *changed in 2026.9.16.1* (#598). Now: `parse_region_chain` (`src/core/config.cpp:30` at
  `84572b0`) turns the object into an **ordered list** `IndexRepo::artifactBases` of `{region, url}`: the `mirror` region
  first (an empty or unknown `mirror` counts as GLOBAL), then `GLOBAL`, then the remaining keys in declaration order;
  entries are trimmed and trailing slashes stripped. A failed pointer/asset fetch tries the next base; **git only after
  the whole chain**. `xim.index-base` is read the same way (`:148`) and, once exhausted, never falls back to the official
  server. `xim.mirrors.index-repo` takes **only the first** element (`:169`) because it names a git remote.
  At the 2026.9.14.1 baseline the object collapsed to one value: the `mirror` key, else `GLOBAL`.
- The region object **round-trips**: `xim-indexrepos.json` stores the object, not the one region used last time (writing
  back the pick is how region declarations used to collapse to a single region over successive runs).
- **Sub-indexes declared in the default index's `xim-indexrepos.lua`** may carry `["artifact"]` (string or region object)
  and `["source"]` since 2026.9.16.1; before, only a git URL could be declared there, so a sub-index got artifacts only
  through the official merged pointer. A block without `artifact` behaves as before.
- **Default index auto-completion**: if the user wrote `index_repos` but no `xim` entry, Config **inserts** the default
  entry **at the head of the array** (`:562-579`).
- **Directory mapping is unconditional** (`:1039-1043` `repo_dir_for`): `xim` -> `<data>/xim-pkgindex`; anything else ->
  `<data>/<name>`.
- **Fetch strategy: artifact first, git as fallback**, single entry point `sync_one_repo` (`xim/repo.cpp:465-534`):
  `mode = repo.source non-empty ? repo.source : $XLINGS_INDEX_SOURCE (default auto)`; if `artifact_is_declared_for`
  passes, look up the pointer -> `fetch_index_artifact`; when `mode == "artifact"` a failure is a **hard error with no
  fallback**, otherwise it WARNs and goes to git/local.
- The git path has two guards (`:209-334`): a tree with `pkgs/` but no `.git` -> **refuse** to `remove_all`+clone (that
  tree is artifact-managed); git has no connect timeout and a blocked github stalls for roughly 127s, so a 3000ms TCP
  pre-probe runs first; there is also a 7-day throttle stamp `<repoDir>/.xlings-sync-stamp`.
  WARNING: the pre-probe only proves the handshake; a peer that then goes silent held `xlings update` for 11.5 minutes
  (#599). Since 2026.9.16.1 git runs with a low-speed abort (60 s) and the whole update has a 300 s budget - see
  `env-vars.md` for `XLINGS_GIT_NETWORK_TIMEOUT` / `XLINGS_INDEX_HTTP_TIMEOUT` / `XLINGS_UPDATE_TIMEOUT`.
- **Two forms coexist**, distinguished uniformly by `get_repo_head_hash()` (`:664-700`): a git worktree -> read
  `.git/HEAD`, return the 40-character sha; an unpacked artifact tree (**no `.git`**) -> read `.xlings-index-version`,
  return `"artifact:<version>"`.
- **Local sources** (`file://` or a path): top-level entries become **symlinks**, sub-indexes become **git clone
  snapshots** — the asymmetry is deliberate (`repo.cppm:105-112`). **Local sources never take the artifact path.**
- **Cache**: the parse product `<repoDir>/.xlings-index-cache.json` (`index.cpp:215`, fields `version`(=2) /
  `repo_head_hash` / `default_namespace` / `entries` / `mutex_groups`); a hit requires all three to match, and any
  structurally inconsistent entry invalidates the whole file. **The index source must have a `pkgs/` directory or the
  rebuild fails** (`:190-193`). The artifact pointer cache is **in-process only, never written to disk**.
- **Index publisher contract** (`docs/design/index-version-contract.md`): the index root may carry `index-compat.json`
  `{"requires":{"xlings":{"min":"…"}}}`, `min` is **inclusive**, `max` **exclusive**, and there are **no range
  expressions** ("the syntax is deliberately too impoverished to misread"), at most 4 KiB. The pointer's outer layer
  carries `format_version: 2` and a `history[]` (**reverse-ordered, `history[0]` is the current snapshot**, each entry
  carrying its own `artifact.sha256`, so **only snapshots listed in history can be selected**) plus a **`client_latest`
  that must not be omitted** (otherwise clients routed to an old snapshot can never move forward). The history
  retention policy is a **union**: the most recent 8 together with the newest entry for each distinct `requires` value,
  capped at 32.
  WARNING: **getting the deployment order backwards hurts users** — before declaring a floor, history must already
  contain a snapshot to fall back to; when `tools/check_index_compat.py` reports "requires >= X", **do not copy it in
  immediately**.

## 5. Installation state: three sources and one arbiter

**xlings has no single installed DB.** `xim/install_state.cppm:10-34` records explicitly that the sources historically
disagreed with each other (on one real machine with 124 packages, four answers were inconsistent simultaneously).

- **Source A — `versions` (version ledger)**: the `versions` key of the global `<home>/.xlings.json`; in project mode
  it is written to `<projectDir>/.xlings/.xlings.json` (`config.cpp:1246`).
  Structure `VersionDB = map<string, VInfo>` (`xvm/types.cppm`):
  `VInfo{type(program|lib|files|group), filename, versions[<ns:ver or bare ver>] = VData, bindings}`.
  `VData` serialized fields: `path` (**the payload directory, may contain the `${XLINGS_HOME}`
  placeholder**), `kind`, `sourceName`, `destinationName`, `fileSrc`, `fileDst`, `includedir`, `libdir`, `alias[]`,
  `envs{}`, `bindingGroup{...}`, `bindingMembers{}`, `bindingHeaders[]`, `bindingIntegrityIssues[]`.
  WARNING: **the key is the xvm target name (program name), not the package name** — this is the entire origin of #576
  (`xvm/owner.cppm`): llvm registers several targets such as `clang`/`lld`/`llvm-ar`, while the index has only one
  package, `llvm`.

  **The version key's spelling is a contract, added in 2026.9.2.1** (`docs/spec/xlings-json-schema.md:70-85`,
  implementation `src/core/xvm/db.cppm:120-166`). Four rules, all of them worth knowing before touching
  `index_repos`:
  1. A package from the index **named `xim`** (`Config::DEFAULT_INDEX_REPO_NAME`) writes a **bare** key; any other
     index writes `ns:`. The decision reads the entry's **name**, **never its position in the array** — before this,
     `index_repos.front()` decided, so one documented command that moved `xim` down the array made the same package
     key its versions both `2.1.222` and `xim:2.1.222` on one machine.
  2. **A key's spelling is fixed at first write and never re-derived.** Re-registering the same version from the same
     provider (reinstall, repair) reuses whatever is already on disk; only a never-registered version is minted fresh.
  3. **Reads are tolerant in both directions**: `xim:2.1.222` finds a record stored as `2.1.222` and vice versa. But
     `ns:v` never matches `other:v` — that is a different index's payload.
  4. **Twins**: the same version present under both spellings with the same `path` is **one registration written
     twice** (damage from the old position-dependent rule). Every reader collapses to the one carrying
     `bindingGroup`; `remove` takes both; `self doctor` reports `duplicate version key` and `--fix` merges them and
     rewrites every subos reference. Upstream measured 240 merged on one home, 0 on the second run.
  Symptoms on 2026.8.30.2 and earlier: 767 targets that could not be removed, 240 versions registered twice, 10
  packages both uninstallable (`xvm-group-conflict`, now correctly named `xvm-version-key-spelling`) and unremovable.
- **Source B — `workspace` (each subos records its own)**: the `workspace` key of
  `<home>/subos/<active>/.xlings.json` (read `config.cpp:810-816`, write `save_workspace` `:1503`). Three value
  shapes: string (legacy), object `{active, installed[]}` (0.4.19+), or a platform-conditional object. The read side
  enforces the invariant "active is necessarily in installed". **Saving always writes only the subos-side file**, and
  since 2026.9.12.1 it **refuses to overwrite a file it cannot parse**. How to tell the object form from the
  platform-conditional form: **the presence of an `active` or `installed` key means object form.**
  WARNING: a subos whose `.xlings.json` does not parse used to vanish from every cross-subos question. Since
  2026.9.12.1 it is a `SubosUnreadable` finding, `list --all` says it could not show it, and `remove` treats it as
  "may still be using this payload" — detach, not delete, and `--force` does not override that.
- **Source C — the payload stamp** `.xpkg-install.json`, see §4.

**The single arbiter** `installation_state()` (`install_state.cpp:35-80`), three states
`Absent`/`Installed`/`Incomplete`:

| Condition | Verdict |
|---|---|
| stamp says `incomplete: true` | Incomplete (**checked first**, `:50-52`) |
| no payload and no ledger reference | Absent (`:57-58`) |
| ledger references it but the payload is gone | Incomplete, "record points at a payload not on disk" (`:62-63`) |
| payload present, ledger absent, and the stamp says `registered > 0` | Incomplete (`:70-71`) |
| everything else | payload present means Installed (`:78-79`) |

**Positive evidence is required deliberately** (`install_state.cppm:99-116`): on a real machine with 340 payloads, 115
were "payload without ledger", and the vast majority were leftovers superseded by a newer version rather than broken
installs; a naive rule would drown out the 29 genuine problems. `LedgerIndex` (`install_state.cpp:113-135`) pre-scans
the DB and reverse-parses each `data.path` through `expand_path` + `coordinate_from_payload_path` into
`{ns, package, version}` — **further confirmation that the payload path is the package identity, because the installer
wrote it**.
WARNING: a swept payload (§4) reads as **`Installed`** by every one of these rules — it has content, a stamp and a
ledger entry. That is exactly why the doctor repair ladder skips the cheap "install alone" rung for `SweptPayload` and
goes straight to remove-then-install.

**The implementation of #576** (`src/core/xvm/owner.cpp:195`):
```cpp
payload_path_names_another_package(payloadPath, ns, package) {
    auto coord = coordinate_from_payload_path(payloadPath);
    if (!coord) return false;          // unparseable -> cannot prove -> keep old behavior
    return coord->ns != ns || coord->package != package;
}
```
Call site `installer.cpp:2976`; when `payload_is_ours` is false the package is not considered installed and the
install hook keeps running. **The polarity is deliberately "can we prove this belongs to someone else"**
(`owner.cppm`), and **version is deliberately excluded from the comparison**.
WARNING: the commit states explicitly what this is **not**: publishing conflicting `<name>@<version>` entries to an
index **remains unsafe until this version becomes the floor** (clients older than it keep silently skipping the
install); this fix only targets accidental collisions.

## 6. `type = "files"` declarative file assets (easy to get wrong)

`docs/spec/xlings-json-schema.md:100-138`: a recipe declares non-program, non-library entries (headers, `.pc` files,
certificates) with `xvm.files{src=, dst=, binding=}`. They are **registered as their own target**, named by libxpkg as
`<pkg>.files.<n>`, and **bound to the release, not hung off the package's own entry**.
**Contract corollary**: to enumerate the assets a release placed you **must walk its members**
(`release_file_placements`); querying `file_placement` by package name **is always empty**. The uninstall path from
2026.7.27.0 through 2026.8.26.1 asked it exactly that way and never reclaimed a single asset (openxlings/xlings#423).
Both ends must be relative paths; the top level of `dst` **only allows `usr/`, `etc/`, `share/`** (no absolute paths,
no `..`, no `bin/`).
WARNING: verification criterion — **do not use `[ -e ]`** (it follows symlinks, so a dangling link left after the
payload is deleted reads as "does not exist"); use `-xtype l`.

## 7. `subos_info` and the `op` of `envs` (`docs/spec/xlings-json-schema.md:283-491`, the thickest section)

`workspace` records "what is installed"; `subos_info` records "what this is". The block is written into **each subos's
own `.xlings.json`** (`src/core/subos/manifest.cppm:36`, `SCHEMA_VERSION = 1`, `BLOCK = "subos_info"`). Fields:
`schema_version` / `runtime` (e.g. `glibc@2.44.2`) / `runtime_source` / `runtime_abi` / `envs` /
`created_at`+`created_by` **or** `described_at`+`described_by` / `host_glibc` (`manifest.cpp:302-331`).

Four hard semantics:
1. **An absent `runtime` means "known unknown"** (`:316-335`). Three states: no block (legacy format) / block present
   without a `runtime` key (**we looked and could not say**) / well-formed. When present it must be `<name>@<version>`;
   **the empty string is not valid**. Motivation: before 2026.8.17.1 the invariant demanded a well-formed value, so a
   description with no evidence had to invent one — measured on one real machine, two SubOSes declared `glibc@2.44`
   while `lib/libc.so.6` pointed at a 2.39 payload (#547). **Downstream readers seeing an absent value should degrade
   and explain why, not pick a default on its behalf.**
2. **Why `runtime_source` is recorded separately** (`:336-357`): the fallback constant and the index answer will be the
   same value for a long stretch of time, so "the mechanism is working" and "the mechanism is dead but the constant
   happens to be right" are byte-for-byte identical in the manifest. It has twice been the only usable discriminator.
   General rule: **when you add a field whose value can come from two sources in the same shape, record which one was
   used.** `fallback` is not an error.
3. **Creation vs description** (`:358-398`): creation writes `created_*`, description (`self doctor --fix`, upgrade
   paths) writes `described_*`; **one or the other, and only the absence of both is a defect**. Previously every
   backfill wrote `created_at`, so two different SubOSes on the same machine carried byte-identical creation times.
   `created_*` is only inherited when **the pair is complete** (`manifest.cpp:322-329`).
4. **Declaration beats the index; resolution has three priority levels** (`:399-426`): the SubOS-declared `runtime` >
   the version of that package already active in this SubOS > index resolution. WARNING: **`latest` and "the largest
   entry in the table" are two different questions asked of the same table** (in the index, `musl` has
   `latest = 1.2.5` while the table contains `1.2.6`). Also, **there are two kinds of runtime, vendored and hosted**
   (`:427-438`) — hosted runtimes (`ucrt`, `macos_sdk`) **have no payload and are never installed or pinned**, so for
   them "the declared runtime must be installed" is a **false proposition**. **Rebinding is an operation, not a side
   effect** (`:439-462`): **an index update never changes an existing SubOS's binding.**

**The `op` semantics of `envs`** (`:463-491`): values must use the placeholders
`${pkgdir}`/`${subosdir}`/`${home}`/`${xlings_home}`; a hardcoded absolute path only holds on the machine that wrote
it. **There are only two ops, and `set` is conditional — it does not "set"**:

| op | Semantics |
|---|---|
| `set` | exports **only if the variable does not exist**; if it already exists (**even with an empty value**) it is left untouched — **this is not an overwrite** |
| `prepend` | prepends to the existing value, joined with the platform path separator; when the variable does not exist this is equivalent to a plain assignment |

> This name has fooled people: it sent both the `xim-pkgindex#565` reporter and the `xlings#508` author in the wrong
> direction. Renaming would make recipes using the new op name fail at install time with `EnvDeclMalformed` on every
> already-released older client, so the name stays and the semantics live in the docs.

**"Does not exist" vs "value is empty": an empty value counts as set, and the user's value wins.** All four backends
must agree (`:466-472`): POSIX uses `: "${FOO=value}"`, **not `:=`**; fish uses `if not set -q FOO`; pwsh uses
`if ($null -eq $env:FOO)`, **not `-not`** (`-not` is true for the empty string); in-process code uses
`!utils::env_is_set(var)`, **not `existing.empty()`**. Three of the four backends used to be inverted, so the same
declaration produced different environments in different shells, silently. Implementation at
`src/core/subos.cppm:431-445` (`apply_subos_env_`) and `src/core/xvm/shim.cpp:336-350`.

## 8. xpkg descriptor essentials (when writing xim packages)

`xim-pkgindex` layout: `pkgs/<first letter>/<package name>.lua`, 27 directories, **187 `.lua` files**, no second
suffix. The filename equals `package.name`; the test mirror is `tests/<first letter>/test_<name with underscores>.py`.
Other root-level structure: `xim-indexrepos.lua` (sub-index registry, each entry `{GLOBAL=…, CN=…}`), `libs/*.lua`,
`docs/{V0,V1,V2}/xpackage-spec.md` (three generations of the spec coexist),
`.github/scripts/check-dep-namespace.lua`.
WARNING: **the index repo structure recognizes only `pkgs/`** (code at `xim/index.cpp:190`, `repo.cpp:25,231`,
`catalog.cpp:370,385,399`) — the `packages/<pkg>/xpkg.lua` form written at
`docs/quick-start/custom-index.md:132-141` is **wrong**.

**Two-stage form**: `package = {…}` (purely static metadata, only literals and `string.format` allowed) ->
`import("xim.libxpkg.*")` -> `function install/config/uninstall/installed/build()`. **179 of the 187 packages
define at least one lifecycle hook — that is the shape fingerprint** (the 8 exceptions are 7 `type = "script"`
recipes plus 1 `type = "template"`, which carry `xpkg_main` instead; 186/187 is a *different* fingerprint —
the number that `import("xim.libxpkg…")`. Re-counted at `origin/main @ 99bdba3`.) Key fields: `spec` / `name` / `type`
(`package|script|template|config|subos`) / `archs` / `status` / `programs` / `xvm_enable` / `ci = {mirror, update}` /
`deps` / `xpm` (platform x version x architecture resource matrix). `tests/test_xpkg_spec.py` enforces D1: `config()`
must call `xvm.add(package.name)`.

### V1 vs V2: `spec` is only a "client capability ceiling gate"
Distribution 117x`"1"` + 70x`"2"`; V2 describes itself as a **strict superset** of V1. The only spec check lives in the
installer (`installer.cppm:94` `max_supported_xpkg_spec = 2`; `installer.cpp:2519`). Two deliberate design choices
(`:2508-2527`, `refusedNodes` declared at `:2493`): **install side only** (an already-installed package must stay removable even if its recipe is ahead of
us); **refusal is per-package, not per-transaction** (the reason the `refusedNodes` set exists — a plain `continue`
would only skip the download, and the package would still run hooks and get registered).
**The most important correction here**: the V2 promise of "`spec >= 2` implies strict `archs` validation" **has been
replaced** (`src/core/xim/compatibility.cppm:35-46`) by `ArchEvidence`, inferred **from the facts of each resource
entry**:

| Evidence level | Trigger | Consequence |
|---|---|---|
| `Strong` | the entry enumerates architectures (any of `archs` map / `sha256_by_arch` / `arch_alias` non-empty) | **fail-closed**: host arch not in the set -> `E_UNSUPPORTED_TARGET` |
| `Open` | the URL contains `${arch}`/`${arch_alias}`, or `res = true` | no restriction |
| `Weak` | a single artifact only | **always supported**, advisory warning only |
| `None` | nothing declared | allowed through |

Reasoning (`compatibility.cppm:14-22`): `archs` is a **package-level union** while resources are grouped by OS
(`go.lua` declares `{"x86_64"}` but its macOS entry is darwin-arm64), and "of the 99 recipes that set it, the vast
majority write `{"x86_64"}`, meaning 'this is the arch I happened to test'". Therefore **changing a V1 recipe's `spec`
to `"2"` without changing its resource shape changes no behavior at all.** What actually switches on strict mode is
the act of writing per-arch resources. New packages should write `spec = "2"`; `res = true` is legacy input.

### Multi-architecture resources and namespaces
OS keys `linux`/`macosx`/`windows` (plus distro keys and `ref` inheritance); arch keys `x86_64`/`aarch64`/`x86`, with
aliases accepted and normalized on input (`arm64`<->`aarch64`, `amd64`/`x64`/`x86-64`<->`x86_64`).
WARNING: what must be matched is the **process ABI, not the machine ABI** (an x86_64 build under Rosetta must install
the x86_64 artifact).
Four shapes: Shape B (per-arch resource map), Shape C (URL template + per-arch sha256 + optional `arch_alias`), Shape
res (legacy), and **Shape source (recommended: hoist the URL to root/platform level, platform overrides root)**.
Placeholders `${name} ${version} ${os} ${arch} ${arch_alias} ${ext}`.
**GLOBAL/CN semantics**: GLOBAL is the **authoritative upstream**, other keys are **byte-equivalent fallback
mirrors**, and the relationship cannot be reversed ("both the version updater and the mirror materializer read GLOBAL
as the source of truth, so pointing it at a mirror makes the mirror mirror itself").
**An empty resource is not a failure**: `["0.1.1"] = { }` is legal and intentional (creating symlinks, compiling at
install time). `compatibility.cppm:60-84` spends a whole passage explaining `declares_no_download_source()`: "the
download is skipped while the install hook still runs, and that is the entire design. **The warning is the bug.**"
**Namespaces**: only 9 of the 187 descriptors declare a `namespace`; when omitted it **inherits the index repo's
default namespace**, and the default namespace **equals the index repo name** (`catalog.cpp:319/330/343/358`; a local
repo is `"local"`, `:372`).
Do not omit it: **dependencies must carry the namespace prefix (enforced by CI)** —
`.github/scripts/check-dep-namespace.lua` loads recipes in a Lua sandbox and walks the tables (rather than using
regexes). Reason: CI additionally registers every changed recipe into the `local:` namespace, so bare names become
ambiguous and break installs — "2026-08-08: 66 occurrences across 26 recipes, exposed by an earlier accidental name
collision with fontconfig".
**Query with the coordinate you declared**: `pkginfo.dep_install_dir("xim:glibc")` correct / `("glibc")` wrong
(openxlings/xlings#524: 6 of 7 call sites passed bare names, so gcc and meson could not install on any cold home).
WARNING: **`xvm.add` automatically prepends the index namespace, `xvm.remove` does not** — `uninstall()` has to
reverse-parse the ns from `pkginfo.install_dir()` itself.
