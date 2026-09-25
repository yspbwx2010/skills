# Contributing a package to xim-pkgindex

Writing, testing and submitting an `xpkg` recipe for `openxlings/xim-pkgindex`, the official
xlings tool index.

## 0. Version stamps and scope

- **Evidence baseline**: xlings side re-verified at `main @ 4ea4eac` (`VERSION = "2026.9.14.1"`,
  `src/core/config.cppm:13`), **dated 2026-09-16**. The **xim-pkgindex side is unchanged from the previous pass**
  (`origin/main @ 99bdba3`, 2026-08-31 — the pin was re-checked this round against the local clone and is
  byte-identical, so nothing has drifted); its citations were **spot-checked, not re-read end to end**.
  Read-only recon; no build, install or update was run.
- **Citations**: `[xlings src/…]` = xlings source; a bare repo-relative path (`pkgs/…`,
  `tests/…`, `docs/…`, `.github/…`) = xim-pkgindex.
- **Citation discipline**: this index's `docs/` **has been measured to contradict the recipes
  and tests in the same repository** (1.1). Priority: xlings source > a recipe comment carrying
  a measurement > tests > `docs/`.
- **Two xlings-side changes since the previous baseline directly affect recipe authors**: the local index that
  `--add-xpkg` writes to became a managed overlay that `xlings update` garbage-collects (1.6), and the install
  layout of a package with **no `install()` hook** is now specified rather than incidental (1.7). Everything else
  that moved is in `version-notes.md`.

---

## 1. Corrections to read before writing a recipe

### 1.1 `os.arch()` is NOT bound in the xim hook runtime — the V2 spec says it is

`docs/V2/xpackage-spec.md:285-292` tells you to derive an arch-named directory from `os.arch()`;
`docs/V2/xpackage-template.lua:51` repeats it. The recipes and tests say the opposite:

| Evidence | Says |
|---|---|
| `pkgs/n/node.lua:156-158` | "`os.arch` is not bound in the C++ xim hook runtime (xlings >= 0.4.6x, only os.host is) and `_RUNTIME.arch` is empty for install hooks" |
| `pkgs/g/godot.lua:241` | "cannot ask for the host arch: `os.arch` is not bound in the xim hook" |
| `tests/j/test_jdk_corretto.py:88`, `tests/j/test_jdk_zulu.py:86` | the arch-bearing directory name "can only be derived from the archive name (no `os.arch` in the hook)" |

Derive the arch token from what the hook does have: the download name via
`pkginfo.install_file()`, or the version key. If you must probe, probe defensively with a
fallback and then verify by listing — `pkgs/n/node.lua:160`:

```lua
local arch = (os.arch and os.arch()) or (_RUNTIME and _RUNTIME.arch) or ""
```

`install()` there probes both arch tokens with `os.isdir`. `pkgs/m/musl-cross-make.lua:323`
calls `os.arch()` unguarded; that is an outlier, not a licence.

### 1.2 `os.exists` / `os.files` / `os.filedirs` / `os.curdir` are nil

Calling one fails the install with `attempt to call a nil value (field 'exists')`, and what you
see is an install directory holding only `.xpkg.lua` — which reads exactly like a broken payload
[`pkgs/c/codex.lua:249-252`].

| Not bound | Use instead |
|---|---|
| `os.exists(p)` | `os.isdir(p) or os.isfile(p)` — ask about the two kinds separately [`pkgs/c/codex.lua:253`] |
| `os.files`, `os.filedirs` | `os.dirs` (directories only), or `os.iorun` around `grep -rl` / `find` |
| `os.curdir` | derive from `pkginfo.install_dir()` / `pkginfo.install_file()` |

`pkgs/g/gcc.lua:214-226` records all three failing the same way, and notes that
`pkgs/i/interposer-stub.lua:86` calls `os.filedirs` — so that error path has never run.
`os.iorun` is attested by 26 recipes (58 call sites, re-counted at `origin/main @ 99bdba3`); it raises on non-zero exit, so append `|| true` where an
empty result is healthy [`pkgs/g/gcc.lua:228-232`].

### 1.3 `path.*`, `os.host()` and `try {}` ARE part of the spec — do not avoid them

The V1 prelude explicitly provides `os.host()`, `os.isfile`, `os.isdir`, `os.mv`, `os.cp`,
`os.dirs`, `path.join`, `path.filename`, `path.directory`, `io.readfile`, `io.writefile`,
`string.split`, `try { fn, catch = { handler } }` and `cprint`
[`docs/V1/xpackage-spec.md:23-36`]. Measured across the 187 recipes on `origin/main`:
`path.join` in 169, `os.host` in 40, `try {` in 9, `raise(` in 24.

What is banned is the **xmake-private** surface, and the ban is enforced:

| Banned | Replacement | Enforced by |
|---|---|---|
| `import("xim.base.runtime")` | `import("xim.libxpkg.pkginfo")` | `assert_uses_new_api` [`tests/lib/assertions.py:212-222`] |
| `import("common")`, `import("platform")` | `xim.libxpkg.*` | same |
| `is_host("linux")` | `os.host() == "linux"` | `docs/V1/xpackage-spec.md:87` |
| `format(...)` | `string.format(...)` | `docs/V1/xpackage-spec.md:88` |
| `os.scriptdir()` | `system.xpkgdir()` / `pkginfo.install_dir()` | `docs/V1/xpackage-spec.md:90` |
| top-level `path.join(...)` | move inside a hook | `docs/V1/xpackage-spec.md:91` |

Current usage of those three imports across `pkgs/`: **zero**.

### 1.4 A cross-namespace `<name>@<version>` collision skipped `install()` silently — fixed at 2026.8.30.2, still unsafe below it

Until xlings **2026.8.30.2**, the install planner's fallback answer to "is this already
installed" was keyed on a bare short name, so with `xim:codex@0.146.1` present every
`local:codex@0.146.1` install was a **silent no-op** that still printed `N package(s) installed`
and left an install dir holding only `.xpkg.lua` [`pkgs/c/codex.lua:200-213`; proven there with
an `io.writefile` probe — the log file was never created].

Fixed in openxlings/xlings#576: `payload_path_names_another_package` reads
`coordinate_from_payload_path`, and the fallback now declines a DB entry it can prove belongs
elsewhere [xlings `src/core/xim/install_state.cpp:26,118`; `src/core/xvm/owner.cppm:64-65`].

WARNING: the fix commit states the rule explicitly — **publishing a colliding `<name>@<version>`
to an index is still unsafe until this version is the floor, because a client below it goes on
skipping the install silently.**

Clear both namespaces before testing:

```bash
rm -rf "$XLINGS_HOME"/data/xpkgs/{xim,local}-x-<pkg>/<version>
```

### 1.5 `raise()` in `install()` does not reach the summary; in `config()` it does

- `N package(s) installed` **counts recipes that did not raise, which is not the same as
  packages that work** [xlings `src/core/xim/installer.cppm:500-503`;
  `src/ui/info_panel.cpp:408`]. Two real installs printed the checkmark and left the user with
  nothing (llvm and gcc on Windows, openxlings/xlings#447), emitting no diagnostic.
- A `raise()` inside `install()` does **not** reach the summary either — a genuinely failed
  install can still be reported as succeeding. A Lua **runtime** error does surface
  [`pkgs/c/codex.lua:210-213`].
- A `raise` from `config()` **is** reported, by every client back to 0.4.29:
  `[warn] config hook failed for foo: …` then `[error] [foo] failed: config hook failed`
  [`docs/V2/xpackage-spec.md:574-585`; xlings `src/core/xim/installer.cpp:2373`].

End `install()` by asserting the artifact exists, never with a bare `return true`
[`pkgs/c/codex.lua:215-222,258-260`]. **Verify by listing the install directory, never by the
exit code.**

Backstop, not a substitute: after the whole plan runs, xlings checks `package.programs` against
the version database and reports a package that promised programs and registered **zero**.
Partial registration is normal and is not reported [xlings `src/core/xim/installer.cppm:500-520`].

### 1.6 The registration command is `xlings config --add-xpkg`, not `xlings install --add-xpkg`

`--add-xpkg <FILE>` is an option of **`config`** [xlings `src/cli/spec.cpp:40`], not of `install`. The repo's
issue template still shows the `install` form [`.github/ISSUE_TEMPLATE/add-xpackage-template.md:23`]; the CI
harness uses the `config` form [`.github/scripts/posix-test.sh:346,406`]. It copies the recipe into the
**local** index, where it then resolves as `local:<name>`.

**Since xlings 2026.9.12.1 the local index is a managed overlay, and that changes the test loop.** Three things
to know before you build a workflow on `--add-xpkg`:
- `--add-xpkg` **refuses to store** a recipe byte-identical to the already-synced index (Note
  `xim.overlay_identical`, exit 0, nothing written) [xlings `src/core/xim/commands.cpp:2259`]. A no-op that looks
  like a success is exactly the shape that wastes an afternoon — check with `--list-xpkg`.
- **`xlings update` garbage-collects** overlay recipes that have become byte-identical to the freshly synced
  index, and says which ones it removed [`commands.cpp:2477-2490`]. Once your recipe is merged upstream, your
  local copy disappears on the next update. That is intended; do not treat the overlay as version control.
- Inspect and clean up with the new verbs:
  ```bash
  xlings config --list-xpkg              # name / version / status / source
  xlings config --remove-xpkg <NAME>
  xlings config --clear-xpkg stale       # stale = identical / behind / missing
  ```
  `status` is `unique|identical|modified|behind|missing`; a recipe added by an older client has no provenance
  record and shows as `source = untracked`. An illegal category **exits 2**.
  `--clear-xpkg stale` removes exactly `identical`, `behind` and `missing` [`src/core/xim/commands.cpp:2435-2437`];
  a `unique` **or** `modified` recipe survives — which covers both the not-yet-upstream recipe you just wrote and
  the divergent one you are editing.
- Remember that every bare-name shadow in the overlay makes resolution fall through namespace priority and emit a
  `xim.namespace_priority` notice, so a home used for recipe experiments accumulates noise until you clear it.

### 1.7 A package with no `install()` hook now has a specified install layout (xlings 2026.9.14.1)

`docs/spec/xpkg-manifest-v1.md:158` (in the **xlings** repo) states it as a contract: for a package that is
neither `type = "subos"` nor defines `install()`, the installer runs no code to place files, and
`pkginfo.install_dir()` receives **exactly the entries of that package's own archive, laid out the way the archive
lays them out — the top-level directory is KEPT, never stripped — and nothing else**. The archive itself stays in
the download cache and is never moved into the install directory.

Two practical consequences for a recipe author:
- **You can write against the archive's own layout.** If your archive unpacks to `foo-1.2.3/bin/foo`, that is
  what `install_dir()` contains — `foo-1.2.3/bin/foo`, not `bin/foo`. Descriptors elsewhere that point into an
  extracted tree by glob depend on this, and it is now spec rather than an implementation accident.
- **Before 2026.9.14.1 this was not true**: everything was extracted into the shared `<data>/runtimedir` and the
  whole directory was moved in, so a hookless package received other packages' archives, `.lock` / `.meta` /
  `.part.*` sidecars and trees someone else had unpacked. Upstream measured 221 of 401 version directories
  contaminated on the reporting machine, 5.2 GiB of foreign archives. If your test home predates that release,
  run `xlings self doctor --deep` and look for `SweptPayload` before concluding your recipe placed something it
  did not. `--fix` repairs it by remove-then-install.

A package **with** an `install()` hook still extracts beside its archive — that is the hook's contract and did not
change. A hook that finishes leaving `install_dir()` empty now gets a private extraction rather than the shared
directory.

---

## 2. Descriptor format

A recipe is `pkgs/<first-letter>/<name>.lua`: a static `package = { … }` table, then hooks.

**Key constraint**: the `package` table must be **statically evaluable** — literals and
`string.format()` only, no runtime calls; partition resources by platform under `xpm` rather
than branching on `is_host()`; keep runtime initialisation inside hooks
[`docs/V1/xpackage-spec.md:74-79`].

### 2.1 Fields

Required, checked by `assert_required_fields` / `assert_valid_spec` / `assert_valid_type`
[`tests/lib/assertions.py:19-47`]:

| Field | Valid values |
|---|---|
| `spec` | `"0"`, `"1"`, `"2"` — new packages use `"2"` |
| `name`, `description` | |
| `type` | `package`, `script`, `config`, `template`, `bugfix` |

A `ref` package (`package = { spec = "1", type = "package", ref = "nodejs" }`) is exempt from all
three and is **deprecated** [`docs/V1/xpackage-spec.md:133-139`].

Recommended: `archs`, `status` (`dev`/`stable`/`deprecated`), `categories`, `keywords`,
`programs`, `xvm_enable = true`, and provenance (`authors`, `maintainers`, `licenses`, `repo`,
`docs`, `homepage`, `contributors`, `forum`) [`docs/V1/xpackage-spec.md:97-130`].

`archs` is validated **fail-closed**: if the host arch is not provided by the entry and `archs`
is non-empty and excludes it, the install aborts rather than fetching a wrong binary
[`docs/V2/xpackage-spec.md:167-169`; xlings `src/core/xim/installer.cppm:106`]. This is why V2
exists: in V1, `xpm` resolved by **platform + version** only and `archs` was **never used during
URL resolution and never validated**, so a recipe declaring `archs = {"x86_64","aarch64"}` while
hard-coding an `amd64` URL silently installed a broken binary on ARM
[`docs/V2/xpackage-spec.md:10-16`]. V2 is a **strict superset of V1** — every V1 recipe is a
valid V2 recipe — and needs **xlings >= 0.4.63 (libxpkg >= 0.0.45)** for the complete
`xpm.source` contract; the per-arch shapes work on 0.4.61+ [`docs/V2/xpackage-spec.md:4-6,18-22`].

Canonical arch spellings; aliases are normalized on input [`docs/V2/xpackage-spec.md:161-165`]:

| Canonical | Accepted aliases |
|---|---|
| `x86_64` | `amd64`, `x64`, `x86-64` |
| `aarch64` | `arm64`, `armv8` |
| `x86` | `i386`, `i686` |

### 2.2 Choosing a resource expression

[`docs/contributing.md:16-24`]

| Situation | Expression |
|---|---|
| Official xlings-res, URLs follow the default naming | `xpm.source = "xlings-res"` + per-arch `sha256` on the version entry |
| GitHub/third-party release, URLs regular | `xpm.source = "https://…/${version}/…${arch}…"` + per-arch `sha256` |
| URLs irregular per arch | per-arch resource map on the version entry, each `{url, sha256}` |
| One historical or special version | explicit `url`/mirror table on the version entry, overriding `source` |
| Legacy recipes | `"XLINGS_RES"`, `res = true`, single URL, `ref`, single hash stay compatible |

`xpm.source` may sit at the root or on a platform; **platform overrides root**, and an explicit
version `url` always overrides `source`. Values: `"xlings-res"`, an HTTP(S) URL template, or a
regional map where `GLOBAL` is the canonical upstream and other keys are **equivalent-byte**
mirrors [`docs/V2/xpackage-spec.md:220-237,265-268`]. `res = true` is a legacy input for the
same official resource URL and **should not be added to new recipes**
[`docs/V2/xpackage-spec.md:266-268`].

Template placeholders: `${name}` `${version}` `${os}` (`linux`/`macosx`/`windows`) `${arch}`
(canonical) `${arch_alias}` (via an optional `arch_alias` table) `${ext}` (`zip` on windows,
else `tar.gz`) [`docs/V2/xpackage-spec.md:191-193`]. `XLINGS_RES` auto-URL:
`{res-server}/{name}/releases/download/{version}/{name}-{version}-{os}-{arch}.{ext}`
[`:215-216`].

Platform inheritance: `ubuntu = { ref = "linux" }`. Empty resource for `script`/`config`:
`["0.0.1"] = {}`. **A platform/version that is not described is not added to the local index
database — it cannot be searched or installed** [`docs/V1/xpackage-spec.md:143,161,172`].

Best-practice official form [`docs/contributing.md:28-48`]:

```lua
xpm = {
    source = "xlings-res",
    linux = {
        ["latest"] = { ref = "1.0.0" },
        ["1.0.0"] = {
            sha256 = { x86_64 = "<linux-x86_64-sha256>", aarch64 = "<linux-aarch64-sha256>" },
        },
    },
}
```

Install-time resolution order [`docs/V2/xpackage-spec.md:270-281`]: follow version `ref`;
per-arch resource map (fail-closed); explicit version `url`/hash; platform `source` then root
`source`; expand `xlings-res`/URL template and pick the host-arch hash; else the V1 single-arch
path. **Mirror (`GLOBAL`/`CN`) selection applies after resource normalization.** The index keeps
raw, arch-agnostic data — arch resolves per host, so one shared index artifact serves every arch.

### 2.3 Publishing to xlings-res

Resource servers: `GLOBAL = github.com/xlings-res`, `CN = gitcode.com/xlings-res`
[`docs/quick-start/custom-index.md:103-104`; also `docs/design/package-index-ecosystem.md:80-81`.
`design/index-distribution.md` does **not** carry this pair — that file is 154 lines and the URLs are
not in it]. This is the **software-package binary** channel;
the `xim-index` index artifact is a separate release chain with its own versioned tarball,
pointer and SHA256 — do not put index artifacts under `xlings-res/<package>`, and do not treat a
binary resource as an index artifact [`docs/contributing.md:78-79`].

Required before a version may reference `xlings-res` [`docs/contributing.md:68-76`]:

1. Take every platform/arch artifact from the authoritative upstream release, or from one build.
2. Publish the same tag/release on **both** GitHub RES and GitCode RES under the `xlings-res`
   naming convention.
3. Emit a same-named `.sha256` sidecar per archive; check file size and SHA256.
4. Download once each from authoritative upstream, GitHub RES and GitCode RES; compare
   byte-for-byte and record the result.
5. Update the recipe's `source`/`sha256` and run the version checker. A missing platform, arch,
   sidecar or hash must make it **fail closed**.
6. Submit one PR only after every resource is verified. Backfilling an old version must not make
   `latest` regress.

If either mirror side is missing a resource, or the two differ, **do not** switch the version to
`xlings-res`: publish the mirror resources first, then change the index.

### 2.4 CI opt-in

Declare intent only; periods, cron, rate limiting and retries live centrally — **never write
`1d`/`3d` into a package file** [`docs/contributing.md:53-66`]:

```lua
ci = { mirror = true, update = true },
```

`mirror` handles already-declared versions; `update` only discovers versions and opens a PR.
Central policy at `.github/xpkg-ci.yml:5-10`: `interval: 3d`, `wakeup_cron: "17 2 * * *"`,
`max_packages_per_run: 50`, `request_budget: 500`.

**A self-built artifact sets no `ci`** [`docs/contributing.md:152-157`]: `mirror = true` would
mirror it onto itself (GLOBAL is already xlings-res), and `update = true` would point `latest` at
a URL nobody has built. Bumping such a package is a human action: run the build script, publish,
edit the recipe. Self-built artifacts must keep a **reproducible** build script in the repo (fixed
tar owner/mtime and member order — same input, same bytes) and the recipe must point at it.

---

## 3. Hooks

Order [`docs/V1/xpackage-spec.md:202-210`]: `installed()` -> download (framework) -> deps
(framework) -> `build()` -> `install()` -> `config()` -> `uninstall()`.

Modules, imported at top level [`docs/V1/xpackage-spec.md:38-50`]:

| Module | Core API |
|---|---|
| `xim.libxpkg.pkginfo` | `name()`, `version()`, `install_file()`, `install_dir()`, `dep_install_dir()`, `deps_list()` |
| `xim.libxpkg.xvm` | `add()`, `remove()`, `setup()`, `teardown()`, `use()`, `has()` |
| `xim.libxpkg.system` | `exec()`, `rundir()`, `xpkgdir()`, `bindir()`, `subos_sysrootdir()`, `unix_api()` |
| `xim.libxpkg.log` | `info()`, `warn()`, `error()`, `debug()` |
| `xim.libxpkg.utils` | `filepath_to_absolute()`, `try_download_and_check()`, `input_args_process()` |
| `xim.libxpkg.pkgmanager` | `install()`, `remove()` |
| `xim.libxpkg.elfpatch` | `patch_elf_loader_rpath()`, `auto()`, `apply_auto()`, `closure_lib_paths()` |
| `xim.libxpkg.json` | `encode()`, `decode()`, `loadfile()`, `savefile()` |
| `xim.libxpkg.base64` | `encode()`, `decode()` |
| `xim.libxpkg.subos` | `env()` — libxpkg >= 0.0.48 |

### 3.1 `install()`

Only the install action. `pkginfo.install_file()` is the downloaded (already extracted) input
path; `pkginfo.install_dir()` is the target; typical shape is `os.tryrm(install_dir())` then
`os.mv(...)` [`docs/V1/xpackage-spec.md:223-231`].

Make it **idempotent and self-asserting**: return early when the entrypoint exists, never wipe
`install_dir` before a replacement payload is confirmed, and never report success unless the
entrypoint landed — a bare `return true` gets stamped as installed and leaves a dangling shim
over an empty directory [`pkgs/c/codex.lua:215-222`].

`os.mv` is correct and is what every other recipe uses. The theory that moving consumes a shared
cache xlings will not re-extract **is wrong** — measured: delete `bin/` out of the download
directory and install again and xlings puts it straight back; it re-extracts, and re-downloads
when the archive is gone [`pkgs/c/codex.lua:232-239`].

ELF relocation is **not** done in the recipe: the hook only flips a switch (`elfpatch.auto(...)`)
and xlings applies it centrally after the hook.

### 3.2 `config()`

Registers the version with xvm (subos isolation routing):

```lua
xvm.add("tool")
xvm.add("tool", { bindir = path.join(pkginfo.install_dir(), "bin"), alias = "…" })
```

`bindir` must be explicit when the executable is not at the install root. `xvm.add` `opt` keys:
`version`, `bindir`, `alias`, `type` (`"program"` default, `"lib"`, `"group"`), `filename`,
`binding`, `envs` [`docs/V1/xpackage-spec.md:286-296`]. `xvm.setup`/`teardown` `opt` keys:
`install_dir`, `version`, `bindir`, `libdir`, `includedir`, `programs`, `libs` [`:298-308`].

For a **config-type** package writing a user tool's configuration [`docs/contributing.md:111`]:
keep `install()` light (`return true`) and put the write in `config()`; read and preserve the
existing object and update only the keys this package owns; back up before writing; report through
`log.info/warn/error` and never print a token in clear text. If the user supplied no new key but a
valid one exists, `log.warn` that the old key is reused and the token unchanged; with no reusable
key, `log.error` and fail.

### 3.3 Shared names and flavor versions — check before registering

One xvm name may be provided by **several packages**: `java`/`javac` by every JDK distribution,
`gcc` by `gcc.lua` and `musl-gcc.lua`, `crt1.o`/`libc.so` by `glibc.lua` and `musl.lua`.
Registering a shared name at a bare version fails in **two different ways**:

| Case | Result |
|---|---|
| **Same name, same version** | xvm refuses outright; the second package's **whole config batch** is rejected: `another package already owns this exact name and version; uninstall that package first, or install this one at a different version` [xlings `src/core/xvm/errors.cpp:54-58`; `pkgs/j/jdk-temurin.lua:229-236`] |
| **Same name, different versions** | **Accepted** — the name gets two owners, and one `xvm use` landing on the other side silently repoints the shared `lib/` symlinks [`pkgs/m/musl.lua:186-193`] |

The second is the dangerous one: everything looks fine at install time. Measured, before musl was
added: `crt1.o = {"active": "glibc-2.39", "installed": ["glibc-2.39", "musl-1.2.5"]}` — once
`crt1.o` flips to the musl side, every glibc C link in that subos silently breaks.

**Rule**: register shared names at `<version>-<flavor>`, and list the colliding set as its own
table in the recipe [`pkgs/m/musl.lua:200-226`]:

```lua
local SHARED_LIBS = { "Scrt1.o", "crt1.o", "crti.o", "crtn.o",
                      "libc.a", "libc.so", "libdl.a", "libm.a",
                      "libpthread.a", "librt.a", "libutil.a" }
local MUSL_ONLY_LIBS = { "ld-musl-x86_64.so.1", "rcrt1.o",
                         "libcrypt.a", "libresolv.a", "libxnet.a" }
local FLAVOR = "musl"
local function flavor_version() return pkginfo.version() .. "-" .. FLAVOR end
```

1. **Compute the colliding set, do not eyeball it.** Intersect the other recipe's registration
   table with the real directory listing in your payload, and lock the result with a test so an
   upstream file-set change is caught.
2. **Flavor-tag the colliding names AND the non-colliding ones**, so the whole set switches in one
   `xlings use` and a third package later collides with a convention rather than with a version
   number that happened to be free [`pkgs/m/musl.lua:206-211`].
3. **The binding root uses `type = "group"`.** The root names no artifact (there is no
   `bin/musl`); left as the default `program` kind it becomes a shim that can only ever fail
   (`subos/*/bin/musl -> bin/xlings`), which `self doctor` reports as an orphan
   (openxlings/xlings#452) [`pkgs/m/musl.lua:232-235`; `pkgs/j/jdk-temurin.lua:260-265`].
4. **`uninstall()` must be version-scoped**: `xvm.remove(name, <stored key>)`. Removing by bare
   name deletes the other package's registration too.

   WARNING: **`xvm.add` prefixes the index namespace itself; `xvm.remove` does not.** Registering
   `version = "1.2.5-musl"` stores a bare `1.2.5-musl` from the primary `xim` namespace but
   `local:1.2.5-musl` from any other; hand `xvm.remove` the bare key from a secondary namespace
   and it matches nothing. Measured after `xlings remove local:musl`: the package root was gone
   and every lib node was still there [`pkgs/m/musl.lua:285-305`].

   **CI does not catch this** — `posix-test.sh`'s post-uninstall check only looks for leftover
   *shims* in `bin/`, restricted to names in the package's `programs` list, and lib nodes make no
   shims [`pkgs/m/musl.lua:300-302`; `.github/scripts/posix-test.sh:65-89`]. The namespace is not
   exposed to a hook but the store directory is (`<data>/xpkgs/<ns>-x-<name>/<version>`), so derive
   it [`pkgs/m/musl.lua:310-316`; same shape as `pkgs/g/glibc.lua:446-452`]:

   ```lua
   function __stored_version()
       local store = path.filename(path.directory(pkginfo.install_dir()))
       local ns = store:match("^(.-)%-x%-")
       local bare = flavor_version()
       if ns and ns ~= "" and ns ~= "xim" then return ns .. ":" .. bare end
       return bare
   end
   ```

   Acceptance: install -> read `subos/<name>/.xlings.json`'s `workspace` -> uninstall -> read it
   again; it must be back to `null`. `posix-test.sh` alone does not show a clean uninstall.
5. **Headers behave the same way.** Two libcs disagree on `stdio.h`/`features.h`; scattered into a
   shared `usr/include`, whichever lands second silently wins every compile in the subos. A
   non-system libc puts its headers in its own namespace (`usr/include/musl`) and consumers point
   at it with `-isystem` [`pkgs/m/musl.lua:325-330`].

Precedents to copy: `jdk-temurin`/`corretto`/`zulu` at `25.0.4+7-temurin`, `musl-gcc.lua` at
`16.1.0-musl`, `musl.lua` at `1.2.5-musl`.

### 3.4 Dependencies

Declare a dependency as a question under `xpm.<platform>.deps`; the resolver's answer is
`_RUNTIME.resolved_deps`, available in `install()` and `config()` from xlings 2026.8.5.3 /
libxpkg 0.0.50 [`docs/V2/xpackage-spec.md:352-376`].

- **Do not re-derive the answer.** Hand-building `…/xpkgs/xim-x-glibc/<ver>/lib64`, or looping over
  `{"lib64","lib"}`, is a second answer to a question that already has one. Both were real code;
  with two versions installed they disagreed with the resolver and produced a binary whose
  interpreter came from one payload and whose RUNPATH came from another — a fault before `main`
  reporting `undefined symbol: __pointer_chk_guard, version GLIBC_PRIVATE`, which names neither
  package nor version [`docs/V2/xpackage-spec.md:378-398`].
- **Ask with the coordinate you declared**: `pkginfo.dep_install_dir("xim:glibc")`, not `"glibc"`.
  Omit the version, or pass the range you declared. Only what you declared has a record — a
  transitive dependency returns nil. Measured in openxlings/xlings#524: six of seven
  `dep_install_dir` call sites in this index passed a bare name; when xlings 2026.8.10.1 began
  supplying explicit store roots, gcc and meson stopped installing on any cold home and godot
  silently fell back to the host's GL. `tests/test_dep_query_coordinates.py` now enforces this
  [`docs/V2/xpackage-spec.md:401-438`].
- **Namespace every dep name that also names a package in this index.** A bare name resolves only
  while exactly one index provides it, and CI registers every changed recipe a second time under
  `local:` — so a PR touching two such packages gets `package '<name>' is ambiguous` and the
  install stops. 2026-08-08: 66 such names across 26 recipes
  [`.github/scripts/check-dep-namespace.lua:42-49`]. The **one exemption** is a package that does
  not exist yet: a PR adding P and a consumer of P has P only under `local:`, so `xim:P` fails with
  `package 'xim:P' not found` (hit in #498 and #540). List the `(recipe, dep-name)` pair in that
  script's `EXEMPT` table **in the same PR**, and remove it in the follow-up after publication
  [`:58-75`].
- **A payload that ships its own shared libraries must NOT declare a loader provider**
  (`xim:glibc` and friends). Declaring one gives xlings's predicate-driven elfpatch a keyable
  loader provider, and it **replaces `DT_RPATH` wholesale rather than prepending**. Field-tested
  2026-08-19 on a `qemu-riscv` payload: upstream `[$ORIGIN/../libexec]` became
  `[<install>/lib:<glibc>/lib64:<subos farm>/lib]`; every bundled library was lost **and install
  still reported success** — every existence check passed, and only the first real run failed with
  `libpixman-1.so.0: cannot open shared object file` [`docs/contributing.md:114-139`]. Decide from
  the **measured `DT_NEEDED` closure** (`LD_TRACE_LOADED_OBJECTS=1 <bin>`), not a manifest. When
  only core glibc crosses the payload boundary, empty `deps` is right. A `verify` test for such a
  package must **actually run the binary** — the breakage is invisible to `--version`.
- **Declare what the payload loads.** `deps` is the only input to the RPATH closure xlings stamps
  at install time (`elfpatch.closure_lib_paths`, which reads the **direct** runtime deps, not the
  transitive set). An undeclared library is simply absent from the closure: nothing fails at
  install time, nothing fails on a developer machine that happens to have a copy, and it fails
  elsewhere with an error naming a soname rather than the package that forgot it. That is how
  libxcb came to search for libXau with no libXau on any search path — an index-wide sweep of 28
  recipes to repair. Enforced per package after install by `.github/scripts/dep-closure-check.sh`
  [`:1-24`].

### 3.5 Target sysroot packages differ from host-library packages in three ways

[`docs/contributing.md:141-157`]

1. **Headers never enter the subos sysroot.** A host library copying headers into `usr/include` is
   correct; a cross/bare-metal **target**'s headers doing so masks the host libc for every ordinary
   build. Such a package's `config()` registers only the umbrella node, and consumers point
   `--sysroot` / `-isystem` at its install directory themselves.
2. **Payload is host-independent => one sha256 serves every platform.** Target code is the same
   bytes everywhere, so write one hash across all three platforms and **no per-arch table** — a
   per-arch table makes the mirroring tool treat it as arch-differentiated and chase a second URL
   that does not exist.
3. **No `ci` block** (2.4).

### 3.6 `subos.env` (libxpkg >= 0.0.48)

For what cannot be linked or PATH'd into place (a GL driver found via `LIBGL_DRIVERS_PATH`, an EGL
vendor via `__EGL_VENDOR_LIBRARY_DIRS`). Probe with `type()`, not truthiness (3.7).

| Field | Required | Meaning |
|---|---|---|
| `var` | yes | variable name |
| `op` | no | `set` (default) or `prepend`. `append` / `set-if-unset` are **refused**, not silently downgraded |
| `value` | yes | must use placeholders |
| `binding` | no | `<name>@<version>`, defaults to this package's. Declaring for another package is refused |

Placeholders: `${pkgdir}` (declaring package's install dir), `${subosdir}`, `${home}`,
`${xlings_home}`. An unresolvable placeholder is left **verbatim** rather than blanked —
`${pkgdir}/lib/dri` collapsing to `/lib/dri` would be a real host path outside the subos; `xlings
self doctor` reports it [`docs/V2/xpackage-spec.md:321-340`].

**Do not write cleanup in `uninstall()`** — declarations are provider-scoped and xlings drops the
whole section with the package; a recipe removing them would be a second owner of that state.
Conflicts resolve deterministically by binding order, never by install history; a variable the
**user** already exported wins over a `set`, and `prepend` still composes with it [`:342-350`].

A declaration of a variable that can load **code** into a process is **privileged** and must carry
a comment saying why RPATH cannot serve the same need — essentially the only real answer is a
library that `dlopen`s its siblings by bare SONAME. xlings reports these at install time and
**refuses outright** to put a directory containing a `libc` on a loader search path; that guard
exists because such a declaration once returned an `xlings subos use` shell that died of SIGSEGV
before printing a character. Variables that cause **data** to be found (`XDG_DATA_DIRS`, `MANPATH`,
`PKG_CONFIG_PATH`) are ordinary [`docs/V2/xpackage-spec.md:131-154`].

### 3.7 Adopting a capability older clients lack

The index serves every client version at once and there is **no `min_xlings` field** — a field is
only read by clients that implement it, and the clients that need telling are exactly the ones that
do not [`docs/V2/xpackage-spec.md:480-481,564-572`]. A **new field on an existing shape is safe**
(unknown keys are read with `j.value(key, default)` and ignored, which is why `spec = "2"` shipped
as a plain opt-in); a **new xvm node kind is not** — an older client validates the kind against a
whitelist and aborts the whole registration with `error: unsupported registration node kind 'files'
/ nothing was changed`.

| The capability is… | Probe |
|---|---|
| a new function on an existing module (`xvm.files`) | `if xvm.files then` |
| a new module (`subos.env`) | `if type(subos.env) == "function" then` |

Truthiness is wrong for a module because `import()` answers an unknown module with a **permissive
proxy stub** whose every key returns a truthy, callable table: the old client takes the new branch,
the call evaporates, install succeeds, nothing is configured, nothing complains. The stub is a
`table` with a `__call` metamethod; the real entry point is a `function` — that is the only
difference [`docs/V2/xpackage-spec.md:496-528`].

Rules [`:535-551`]: probe the **new function name** (`xvm.add{type="files"}` does not work —
`xvm.add` exists on old clients and passes `type` straight to the whitelist); keep the legacy branch
**byte-identical** (it is the old client's only path and has no test coverage of its own); **branch
in `uninstall()` too**, or the same files end up with two owners; verify against a real old binary;
compare the old-client result **differentially** ("same as before the migration", not "the file is
there"), because many recipes guard their copy on `os.isdir(sysroot/usr/include)`, which does not
exist in a fresh home.

Retiring a probe: replace `if cap then … else <legacy> end` with
`sysroot.require_capability(cap, "xvm.files", "2026.7.27.0")`, which raises from `config()` and
prints verbatim on every client back to 0.4.29 [`:574-593`]. `config()` runs after download and
extraction, so a refused client pays one download — deliberate: an actionable message beats a field
they cannot read.

---

## 4. Isolation compliance (hard rules)

Enforced as L2 tests on every PR [`tests/lib/assertions.py:191-234`]:

| Do not | Assertion | Instead |
|---|---|---|
| `os.exec("xvm add …")` / `os.exec("xvm remove …")` | `assert_no_exec_xvm` `:191-195` | `xvm.add()` / `xvm.remove()` |
| `append_bashrc`, `append_to_shell_profile` | `assert_no_bashrc_modification` `:198-202` | xvm shim routing |
| `os.addenv(… PATH …)`, `os.setenv(… PATH …)` | `assert_no_direct_path_modification` `:205-209` | xvm shim routing |
| `import("xim.base.runtime")`, `import("common")`, `import("platform")` | `assert_uses_new_api` `:212-222` | `xim.libxpkg.*` |
| `apt install`, `brew install`, `pacman -S` | `assert_no_direct_pkg_manager` `:225-235` | `xpm.<platform>.deps` |

Two repo-wide guards also run in `ci-test.yml`:

- **No blocking stdin.** `io.read()` in an install hook does not degrade when nobody is there to
  answer — it blocks forever, so an unattended install **hangs** rather than failing, and from the
  outside "slow" and "stuck" look identical. Measured 2026-08-08: a `rust` Windows hook asked
  `please input (1 or 2):` and a windows-test job sat on it for four hours against a normal runtime
  under three minutes; GitHub serves no logs for an in-progress job, so nobody could see the prompt
  [`.github/scripts/check-no-blocking-input.sh:1-23`].
- **No direct `LD_LIBRARY_PATH`.** Allowlisted exceptions only, currently `pkgs/m/musl-gcc.lua`
  (alias wrappers invoking the musl dynamic linker, where RPATH cannot apply)
  [`.github/scripts/check-no-direct-ld-libpath.sh:7-13`].

---

## 5. Testing

`tests/` mirrors `pkgs/` one-to-one: `pkgs/n/mypackage.lua` -> `tests/n/test_mypackage.py`, with
`-` replaced by `_` [`docs/test/usage.md:70-76`]. Five layers [`docs/test/design.md:47-53`]:

| Layer | Name | Mark | Needs xlings | Cost | Checks |
|---|---|---|---|---|---|
| L0 | static analysis | `@mark.static` | no | <1s/pkg | Lua syntax, field completeness, typos |
| L1 | index registration | `@mark.index` | yes | <2s/pkg | can the recipe be registered |
| L2 | isolation compliance | `@mark.isolation` | no | <1s/pkg | subos compliance (§4) |
| L3 | install/uninstall | `@mark.lifecycle` | yes | 10-180s/pkg | install -> config -> verify -> uninstall |
| L4 | functional verify | `@mark.verify` | yes | 5-30s/pkg | the installed program works |

L0, L1, L2 are **mandatory** for a new package; L3 and L4 recommended
[`docs/test/usage.md:104,123,130,149,157`]. A minimal test file changes only `PKG`, `PKG_FILE` and
the docstring, importing its assertions from `tests.lib.assertions` [`docs/test/usage.md:80-168`].

```bash
pip install pytest

pytest tests/ -m static                 # no xlings needed, seconds
pytest tests/ -m "static or isolation"  # what a PR must pass first
pytest tests/ -m index                  # needs xlings installed
pytest tests/ -m lifecycle              # actually installs packages
pytest tests/ -m verify
pytest tests/<letter>/test_<package>.py -m "static or isolation" -v

python3 .github/scripts/version-check.py --workspace .   # dry-run static check
```
[`docs/test/usage.md:7-60`; `docs/contributing.md:83-90`]

`version-check.py` is **dry-run without `--apply`**; `--apply` edits lua files in place, appending
a new version block and bumping `["latest"].ref` for every package whose upstream is ahead.
`--only <lua-basename>` restricts the scan [`.github/scripts/version-check.py:791-816`].

**Install behaviour must be exercised in an isolated home; never modify the developer's real
environment** [`docs/contributing.md:92-100`]:

```bash
TMP_HOME="$(mktemp -d)"
XLINGS_HOME="$TMP_HOME" xlings update
XLINGS_HOME="$TMP_HOME" xlings install <package>@<version> -y
XLINGS_HOME="$TMP_HOME" xlings -y remove <package>
rm -rf "$TMP_HOME"
```

For multi-arch resources check at least the x86_64 and aarch64 resolution results; for mirrors
check the actual `GLOBAL`/`CN` URL responses and SHA256; for bad-cache handling seed a wrong-size
cache and confirm xlings evicts and re-downloads rather than treating a non-empty file as a hit
[`docs/contributing.md:102-104`].

CI on a PR: L0 + L2 on every push; L1 after installing xlings; L3 + L4 as a closure lifecycle job;
plus the libpath, blocking-stdin and dep-namespace linters, `version-check` unit tests, and
per-platform install/uninstall of the **changed** packages on Linux, macOS and Windows
[`.github/workflows/ci-xpkg-test.yml:38-42,78-79,160-161`;
`.github/workflows/ci-test.yml:68,80,109,116,199,263`].

---

## 6. Submitting

1. Add or edit `pkgs/<first-letter>/<name>.lua`.
2. For a new package, add the mirrored `tests/<first-letter>/test_<name_with_underscores>.py` with
   at least L0, L1 and L2.
3. Run local direct-command verification in an isolated home: register, search, install,
   repeat-install, list, uninstall, repeat-uninstall — the steps the issue template walks through
   [`.github/ISSUE_TEMPLATE/add-xpackage-template.md:23-74`].
4. Run the test suite plus `version-check.py`.
5. Open the PR.

Commits follow `<type>(<scope>): <description>`, e.g. `feat(pkg): add foo 1.2.0` or
`fix(index): add missing aarch64 checksums`. Merge only after the Linux, macOS, Windows and
index-publishing checks pass [`docs/contributing.md:169-171`].

The PR description must contain [`docs/contributing.md:161-167`]:

1. what the package is for, and which platforms and architectures it supports;
2. resource origin, version, mirror release/tag and SHA256;
3. whether `install`/`config`/`uninstall` modify the user's environment;
4. local command, pytest, static-check and isolated-install results;
5. if `latest` moved, the verified version it now points at.

---

## 7. Minimal V2 skeleton

```lua
package = {
    spec = "2",
    name = "demo",
    description = "demo package",
    type = "package",
    archs = { "x86_64", "aarch64" },
    status = "stable",
    categories = { "tools" },
    keywords = { "demo" },
    programs = { "demo" },
    xvm_enable = true,
    xpm = {
        source = "xlings-res",
        linux = {
            ["latest"] = { ref = "1.0.0" },
            ["1.0.0"] = {
                sha256 = { x86_64 = "<sha256>", aarch64 = "<sha256>" },
            },
        },
    },
}

import("xim.libxpkg.pkginfo")
import("xim.libxpkg.xvm")

function install()
    local exe = path.join(pkginfo.install_dir(), "bin", "demo")
    if os.isfile(exe) then return true end

    os.tryrm(pkginfo.install_dir())
    os.mv("demo", pkginfo.install_dir())

    return os.isfile(exe)   -- assert the artifact, not the intent (1.5)
end

function config()
    xvm.add("demo")
    return true
end

function uninstall()
    xvm.remove("demo")
    return true
end
```

Reference implementations: `docs/V2/xpackage-spec.md`, `docs/V2/xpackage-template.lua`,
`pkgs/g/github-gh.lua`.

---

## 8. Boundary: xim-pkgindex vs mcpp-index

A descriptor with **`function config()` + `xvm.add`** belongs in **xim-pkgindex**; one with an
**`mcpp` table or a `namespace`** belongs in **mcpp-index** (`mcpplibs/mcpp-index`). By
deliverable: a **built artifact** (binary, toolchain, font, driver, script, config) acquired with
`xlings install`, landing in PATH/sysroot/xvm, needing hooks and varying by OS x arch ->
**xim-pkgindex**; **a library to link into a C++ project**, acquired with `mcpp add`, no hooks, and
an `xpm` holding a source archive -> **mcpp-index**.

For the mcpp side, see the `mcpp` skill's packaging reference.

---

## 9. Unverified

- "Putting two files with the same `package.name` into a local index makes the whole local repo
  silently disappear from the search path (`package 'local:foo' not found, searched repos: [xim,
  scode]`), fixed by deleting the duplicate." The `searched repos:` hint exists [xlings
  `src/core/xim/commands.cpp:517,530`], but no evidence was found that a duplicate name drops a
  whole repo. **Unverified.**
