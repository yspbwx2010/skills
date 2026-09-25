# Reference: mcpp environment variable table

> Method: read site by read site across `src/` and `modules/`, including the `mcpp::platform::env::` wrappers. Re-derive the whole
> "Read site" column mechanically rather than row by row - `grep -rn '"MCPP_[A-Z_]*"' src/ modules/` - because these numbers drift as a
> block between releases and a column that is only spot-checked reads as uniformly verified when it is not.
> WARNING: the obvious regex `getenv\("[A-Z_]+"\)` **only matches all-caps + underscore**, so it misses the mixed-case
> `WindowsSdkDir` / `WindowsSdkVersion` and the runtime-composed `MCPP_TOOL_<PKG>_<TOOL>`. Counting read sites and
> counting literal names are two different quantities; do not quote either as "the number of environment variables".
> Baseline `main @ 2fc7b5b0` (version `2026.9.15.2`), dated 2026-09-16, with the 2026.9.16.1-2026.9.21.3 additions read at
> `main @ b30e70c4` (2026-09-23; rows marked with their version), and the macOS / MSVC rows of §2 re-read at `main @ b4824697`
> (`2026.9.24.1`, 2026-09-24, source and docs only; cited `@ b4824697`). Line numbers in unmarked rows are from the older tree - the
> `MCPP_OFFLINE` read site, for one, moved from `env.cppm:106-108` to `:120`. All `src/…`, `modules/…` and `docs/…` paths
> below are relative to the mcpp source checkout.
> xlings' own network bounds (`XLINGS_UPDATE_TIMEOUT`, `XLINGS_INDEX_HTTP_TIMEOUT`, `XLINGS_GIT_NETWORK_TIMEOUT`, 2026.9.16.1)
> are read by the bundled xlings, not by mcpp: zero hits for them in mcpp's `src/` and `modules/`, so mcpp neither sets nor
> clears them and whatever the calling environment holds is what xlings sees. mcpp's own bound on a refresh is
> `[index] refresh_timeout` in `config.toml`. See the `xlings` skill's `references/env-vars.md`.
> **§3 (the contract mcpp writes for build programs) grew a lot in this window** - if you are writing a `build.mcpp`,
> read that section rather than an older list.

## 0. `MCPP_INDEX_MIRROR` does not exist

Whole-tree grep (including `modules/`, `docs/`, `scripts/`, `tools/`, `install.sh`) gives **0 hits**. Setting it is a
**no-op for mcpp**. mcpp's child processes inherit the whole environ: the launchers take an `extraEnv` that is *added* to the child
(never a replacement `envp`, and never a mutation of mcpp's own environment) [modules/platform/src/process.cppm:80-83], so
pass-through is the platform default and not a decision mcpp makes. It **may** therefore be read by xlings, but **mcpp definitely
does not read it**. WARNING: recipes copied from elsewhere
sometimes carry `MCPP_INDEX_MIRROR=GLOBAL`; that line does nothing for mcpp — delete it, or annotate it as "this one is
for xlings".

**Three real approximations**:
1. `mcpp self config --mirror CN|GLOBAL` — WARNING: **only effective while seeding `.xlings.json` for the first time** [src/config.cppm:271-277]
2. `MCPP_INDEX_FLOOR=ignore` — debug escape hatch for the index contract version floor
3. The artifact mirror base is a **compile-time constant**: `kMcpplibsIndexArtifact` [src/config.cppm:59]

There is now a fourth, and it is the one that actually redirects an index: **`[index.repos.<name>]` in
`$MCPP_HOME/config.toml`**. It reaches an **already-initialised** home (it used to seed only a home that did not yet exist,
so adding it to a home that had ever run did nothing and said nothing), and what mcpp wrote is recorded in
`.mcpp-index-overrides.json` beside `.xlings.json`, so deleting the table restores the previous entry — while the file still
holds what mcpp wrote. Each change prints one line; the default `mcpplibs` entry mcpp adds without a table is not reconciled.
```toml
# $MCPP_HOME/config.toml
[index.repos.mcpplibs]
url      = "https://github.com/<org>/<fork>.git"
artifact = "https://..."      # optional
source   = "auto"             # optional: auto | artifact | git
```
=> The override is scoped to one home, so a project-local `MCPP_HOME` needs its own table. And
`.mcpp-index-overrides.json` lives inside `registry/`, so a "delete the registry and re-bootstrap" recovery discards it.
WARNING: entries you wrote earlier and that were ignored will **start taking effect** on upgrade.

## 1. mcpp's own variables (user-settable)

| Variable | Effect | Applicability / priority | Read site |
|---|---|---|---|
| `MCPP_HOME` | mcpp sandbox root | **Highest priority**, see §4 | src/home.cppm:78 |
| `MCPP_LOCKED` | fail if the resolution differs from `mcpp.lock` | `--locked` / `--frozen` just set it; it **also disables the fast path**, otherwise the assertion never runs | src/cli.cppm:184; src/build/execute.cppm:1379,1503 |
| `MCPP_NINJA_DEBUG` | append `-d <topics>` to ninja | e.g. `explain` — the direct answer to "why did this edge rebuild", more reliable than comparing mtimes | |
| `MCPP_OFFLINE` | never touch the network | empty / `"0"` = off. `--offline` just sets it. **Also skips the first-use sandbox bootstrap** (measured on an empty home: 26 s / 126 MB -> 0.3 s), printing one `Skipping sandbox bootstrap (offline mode…)` line. => `--offline` really is offline now, which also means a command needing an unbootstrapped tool fails rather than quietly installing it | modules/platform/src/env.cppm:106-108; src/config.cppm:791-820 |
| `MCPP_NO_AUTO_INSTALL` | do not auto-install toolchains/packages | empty / `"0"` = off | modules/platform/src/env.cppm:110-112 |
| `MCPP_VERBOSE` | global verbose logging | on when non-empty and != `"0"`. **`--quiet` still wins** (the pre-scan runs first) | src/cli.cppm:225-232 |
| `MCPP_JOBS` | compile concurrency | positive integer; a parse failure **does not silently fall back to the default**, it reports invalid. Top of a four-rung ladder: `MCPP_JOBS` > `[build] jobs` (per package) > `[build] default_jobs` (per machine, in `$MCPP_HOME/config.toml`) > 0. The third rung **also bounds `mcpp test`'s test-process concurrency**, whose fallback is otherwise the whole machine | src/build/schedule/policy.cppm:280-288 (ladder comment at :127-141) |
| `MCPP_TOOLCHAIN` | toolchain spec for one build | used when non-empty; **counts as user-explicit**, mcpp will not quietly change it. **Beats the global default** | src/build/prepare.cppm:2489; src/build/execute.cppm:118 |
| `MCPP_BUILD_CACHE` | dependency cache mode | `global`\|`local`\|`off`. Priority `--cache` > **this variable** > `[build] cache` > Global | src/build/prepare.cppm:989,2223-2227 |
| `MCPP_BMI_SCHEDULE` | BMI scheduling | `auto`(default)\|`on`\|`off`, **exact match**. **Beats `[build] bmi_schedule`** | src/build/schedule/policy.cppm:295 |
| `MCPP_SCANNER` | module scanner backend | default is the regex scanner; `=p1689` switches to compiler-driven P1689 | src/build/prepare.cppm:11036 |
| `MCPP_ALLOW_HOST_LIBS` | disable the hermetic link check | on when non-empty and **first character != `'0'`** | src/build/hermetic.cppm:133; src/build/runtime_validation.cppm:229 |
| `MCPP_NINJA_DYNDEP` | dyndep mode | **on by default**; set `0`/`off`/`false` to fall back to static dependency emission | src/build/ninja_backend.cppm:405 |
| `MCPP_VERIFY_MODGRAPH` | widen module graph validation | only when `="1"`, extends P1689 validation to **every** module unit (default validates only those in `scan_overrides`) | src/build/ninja_backend.cppm:1898 |
| `MCPP_STAGE_VERIFY` | staged check for `mcpp stage` | `content`(default)\|`size`; an **unrecognised value also falls back to `content`**. `--verify` overrides it, and `--verify`'s own default is `content` too, so the effective default is `content` either way. WARNING: older write-ups say `size` because the help text once did - that claim is **retired**, see commands.md §2 | src/cli/cmd_build.cppm:847 (parse at src/build/stage.cppm:116,288; enum default at :59) |
| `MCPP_BUILD_PROGRAM_TIMEOUT` | build.mcpp run limit (seconds) | must be a non-negative integer, otherwise ignored. **Beats `[build] build_program_timeout` > 600** | modules/buildmcpp/src/program_protocol.cppm:147 (precedence comment at :117, default at :77) |
| `MCPP_TOOL_BUILD_VERBOSE` | disable output filtering for inner tool builds | filtered by default; error messages actively suggest setting it | src/build/prepare.cppm:9488 (the messages that suggest it: :9453,:9496) |
| `MCPP_INDEX_FLOOR` | ignore the index contract's minimum mcpp version | bypass **only on exact `="ignore"`** | src/pm/index_contract.cppm:194,240 |
| `MCPP_LOG_LEVEL` | log level | `debug`\|`info`\|`warn`\|`error` (**case-insensitive**), any other value -> `off`. Priority **env > `--verbose` > config > default** | modules/log/src/log.cppm:169 (parse at :80-89) |
| `MCPP_NO_COLOR` | disable color | WARNING: **only when the first character is `'1'`** | src/ui.cppm:210 |
| `MCPP_VENDORED_XLINGS` | use the stock xlings binary (for large-package installs on Windows) | **only effective if the path exists**; first in resolution order | src/config.cppm:127-131; src/fallback/xlings_binary.cppm:107,219 |
| `MCPP_TOOL_<PKG>_<TOOL>` | host tool path override | **first hit wins, ahead of `[tools.overrides]`** | modules/buildmcpp/src/tool_store.cppm:295-296 (name assembly), :157-159 (precedence comment) |

### One detail about `MCPP_VENDORED_XLINGS`
Even with the vendored binary, **`XLINGS_HOME` still points at the mcpp sandbox** (it returns
`{vendored, cfg.xlingsHome()}` [src/config.cppm:127-130]) => **the install destination is unchanged**. The branch inside
`make_xlings_env` is **Windows-only** (`#if defined(_WIN32)`; rationale: the xlings copy inside the sandbox lacks a
complete runtime, so large-package installs break). The cross-platform main path is in `src/fallback/xlings_binary.cppm`.

## 2. Non-mcpp-prefixed standard variables that are read

| Variable | Effect | Read site |
|---|---|---|
| `NO_COLOR` | disable color (**any non-empty value works**, looser than `MCPP_NO_COLOR`) | src/ui.cppm:211 |
| `HOME` / `USERPROFILE` | `$HOME/.mcpp` (Windows `%USERPROFILE%\.mcpp`); if neither is set, `cwd/.mcpp` | src/home.cppm:57,60,62 |
| `PATH` | inherited by child processes; on Windows the first `cl.exe` on it is the third candidate for `msvc@system` (see the MSVC row) | src/build/build_program.cppm:719; src/toolchain/msvc.cppm:1060-1072,1343 @ b4824697 |
| `CXX` | probe the system compiler (falls back to `g++`). WARNING: it selects a **compiler executable**, injects no flags, and is subject to the "managed toolchains only" policy | src/toolchain/probe.cppm:276 |
| `COLUMNS` | terminal width | modules/platform/src/terminal.cppm:70 |
| `MACOSX_DEPLOYMENT_TARGET` | macOS deployment target, **takes priority over `[build] macos_deployment_target`**. Read on every host and applied only when the target's `os` is `macos`, so it also governs `--target aarch64-macos` from Linux or Windows | modules/platform/src/macos/macos.cppm:125-132 @ b4824697 |
| `SDKROOT` | macOS SDK root | modules/platform/src/macos/macos.cppm:237 @ b4824697 |
| `VCToolsInstallDir` / `VSINSTALLDIR` / `VCINSTALLDIR` | Which MSVC toolset `msvc@system` means, for the cl.exe row and for clang's `*-windows-msvc` sysroot alike: `VCToolsInstallDir` names a toolset (first candidate), `VSINSTALLDIR` (else `VCINSTALLDIR`'s parent) an instance whose default toolset is the second; then the first `cl.exe` on `PATH`, then the newest vswhere instance. A pinned `msvc@<toolset>` ignores them and reports a `VCToolsInstallDir` naming another toolset in a `note:` | src/toolchain/msvc.cppm:1054-1059 (read), :883-968 (selection) @ b4824697 |
| `VS170COMNTOOLS` / `VS160COMNTOOLS` / `VS150COMNTOOLS` | instance fallback, consulted only when vswhere is absent or fails | src/toolchain/msvc.cppm:445, 1043-1046 @ b4824697 |
| `WindowsSdkDir` / `WindowsSdkVersion` | Windows SDK location for an installed toolset | src/toolchain/msvc.cppm:1156,1198,1250-1251 @ b4824697 |
| `LD_LIBRARY_PATH` / `DYLD_LIBRARY_PATH` | WARNING: **special handling** — when composing explicitly it runs `strip_private_glibc(existing)`, otherwise a nested `mcpp run -> mcpp test` chain makes child tools **segfault inside the dynamic linker** | modules/platform/src/env.cppm:234-235 (helper at :193) |

WARNING: **whether `WindowsSdkDir` / `WindowsSdkVersion` are adopted follows the toolset's origin** [docs/20-toolchains.md:474-477
@ b4824697]: for a **payload** toolset (`xim:msvc@<toolset>`, or `msvc@<toolset>` when no installed toolset matched) the environment
values are **ignored** (mcpp prints a `note:`) and the `windows-sdk` payload beside it is used; for an **installed** toolset
(`msvc@system`, or `msvc@<toolset>` found on the machine) they are adopted, then it falls back to
`C:\Program Files (x86)\Windows Kits\10`.

WARNING (worth memorizing): **the private libc directory is never exported through an environment variable**
[docs/91-toolchain-internals.md]. glibc 2.44's `libc.so.6` has an undefined `__pointer_chk_guard` that only 2.44's own loader exports.
The `PT_INTERP` of `/bin/sh` names the **host** loader and no environment variable can override it, so children of
`popen()`/`system()` **die during relocation, before `main`, with no output at all** (mcpp#401).

## 3. Contract variables mcpp **writes for** build programs / packaging scripts

Source [src/build/build_program.cppm]; read-back interface [src/build/hostprogram.cppm]; docs [docs/30-build-mcpp.md].

**Always emitted, empty string when not applicable** [build_program.cppm:590-600]: build programs read via `env_or`,
which cannot tell "absent" from "empty", and absence would make the answer depend on whatever the parent process
happened to export. **These values unconditionally enter the re-run key** — changing target/profile/features re-runs the
program, no `rerun-if-env-changed` needed.

> The rows below are all `emplace_back` calls inside **one contiguous emission block** [build_program.cppm:554-700]. Re-derive the whole
> Evidence column at once with `grep -n 'emplace_back("MCPP_' src/build/build_program.cppm` rather than trusting any single line number -
> the block moves as a unit, so a row number that has drifted has drifted by the same amount as every other row.

| Variable | Value | Evidence |
|---|---|---|
| `MCPP_TARGET` | target triple; filled with the host triple when empty | :554 |
| `MCPP_TARGET_REQUESTED` | `env.targetTriple` **verbatim** (may be empty) | :579 |
| `MCPP_TARGET_OS` / `_ARCH` / `_ENV` | the three segments split out by the canonical triple parser. On macOS with no env segment, `_ENV=""`; for an escape-hatch triple all three are `""` | :586-588 |
| `MCPP_HOST` | host triple | :589 |
| `MCPP_TOOLCHAIN_DIR` / `MCPP_COMPILER` | toolchain directory / compiler id | :594, :597 |
| `MCPP_TARGET_SYSROOT` / `MCPP_TARGET_BUILTINS_LIB` | target sysroot / builtins library | :599-600 |
| `MCPP_TARGET_LIBC_PROFILE` / `MCPP_TARGET_LIBC` | target libc | :601-602 |
| `MCPP_PROFILE` | current profile | :610 |
| `MCPP_OUT_DIR` | output directory (**always an absolute path**) | :621 |
| `MCPP_MANIFEST_DIR` | package root | :622 |
| `MCPP_FEATURES` | comma-separated list of active features | :638 |
| `MCPP_FEATURE_<SANITIZED>` | one per active feature, value `"1"` | :636 |
| `MCPP_DEP_<SANITIZED_NAME>_DIR` | payload directory of each direct dependency | :647 |
| `MCPP_DEP_<PKG>_BIN_<TOOL>` | **absolute path** (not directory) of a host tool requested via `tools = [...]` | :685; naming at tool_store.cppm:189-192 (`env_var_name`; `sanitize_env` at :182-186) |
| `MCPP_XPKG_[<NS>_]<NAME>_DIR` | xlings package directory, **emitted twice — once namespaced, once bare** (namespaced form first). The matching accessor `mcpp::xpkg_dir` answers **range** expressions now; it used to compare the whole location as a directory name, so `>=8.5.0` installed the payload and then answered "not installed" | |
| `MCPP_BUNDLE_DIR` | exported by the launcher script generated by `mcpp pack`, points at the bundle root | src/pack/pack.cppm |
| `MCPP_IDE_CONFIGURE_FAILED` | IDE configuration failure signal | src/wire.cppm |

**Added to the contract since the previous baseline** (read the source if you need the exact emission point; they are all
written unconditionally, empty when not applicable, and all enter the re-run key):

| Variable | Accessor | Value |
|---|---|---|
| `MCPP_PKG_NAME` / `MCPP_PKG_NAMESPACE` | `mcpp::package_name()` etc. | the package's declared identity. **Use these instead of the last segment of `MCPP_MANIFEST_DIR`** — that is a directory name, and the two differ whenever packages sit under a shared directory |
| `MCPP_PKG_VERSION` / `_DESCRIPTION` / `_LICENSE` / `_AUTHORS` / `_REPO` | `mcpp::package_*()` | the rest of `[package]`. `_AUTHORS` is joined with `;`, not `,`, because an author entry is conventionally `Name <mail@host>` |
| `MCPP_CXX_STDLIB` | `mcpp::cxx_stdlib()` | `libstdc++` \| `libc++` \| `msvc-stl`, empty with no toolchain resolved. `compiler()` cannot answer this: clang links libc++ on one machine and libstdc++ on another and says `clang` both times. The name says `cxx` on purpose — `MCPP_TARGET_LIBC` is the C library |
| `MCPP_TARGET_MIN_PLATFORM_VERSION` | `mcpp::min_platform_version()` | the platform deployment floor carried by the effective triple; **empty on ordinary Linux rows**, so do not read an empty string as failure |
| `MCPP_TOOLCHAIN_SYSROOT` / `MCPP_TOOLCHAIN_BINUTILS_DIR` | | the `--sysroot` and `-B` mcpp passes its own compiler. **Required** by any action that drives a second compiler mcpp did not resolve: inside a sub-OS the C library is not in `/usr/include` and the assembler is not in `/usr/bin`, so that compiler fails on its first `#include` |
| `MCPP_LANGUAGE_MODULES` | | `[language] modules`. An older engine does not set it, and the rules read absence as "headers", which is why adopting it needed no project change |
| `MCPP_ACCEL` / `MCPP_DEVICE_SOURCES` | | the device axis, and the device sources handed to a rule package. WARNING: `MCPP_DEVICE_SOURCES` is **newline-separated**. A rule splitting on `;` is still correct for exactly one device source and builds a path that does not exist for two |
| `MCPP_PACK_FORMAT` / `MCPP_PACK_STAGE_DIR` | `mcpp::pack_stage_dir()` | which distributable format is being produced, and the staged bundle tree; empty when not packing |
| `MCPP_DEP_<NAME>_LINKAGE` | `mcpp::dep_linkage(name)` | `static` \| `shared` for each dependency, computed once **before** the root build program runs so the root can read it. A dependency's own build program does not get it: only the root decides the form |
| `MCPP_PACK_STRIP` *(2026.9.16.1+)* | `mcpp::pack_strip()` | `1` when the `mcpp pack` pass strips, `0` under `--no-strip`, empty outside a pack. A member staging libraries of its own follows it [build_program.cppm:647 at `b30e70c4`] |
| `MCPP_PACK_DEBUG_SYMBOLS_DIR` *(2026.9.16.1+)* | `mcpp::pack_debug_symbols_dir()` | absolute directory `--debug-symbols` sends separated `*.debug` files to; empty when they are discarded or not packing [:648] |
| `MCPP_GRAPH_FILE` *(2026.9.16.1+)* | `mcpp::graph_file()` | the resolved graph as a JSON document (`kind = "mcpp.graph"`, `version = 1`, packages dependencies-first with `manifest_dir`, `features`, `targets`, `link` and `[package.metadata]` verbatim). **Root package's program only**; a dependency's program reads `""`. The document's content is part of the re-run key [:649] |

Naming note (2026.9.16.1+): `MCPP_DEP_<NAME>_DIR` / `_LINKAGE` / `_BIN_*` now come from one derivation - the manifest `name`, the
qualified `namespace.name` and the bound tail - so a package written `namespace = "ns"`, `name = "x"` is reachable as
`MCPP_DEP_NS_X_*` as well as `MCPP_DEP_X_*` (its tools used to be published under the bare name only).
| `MCPP_RUNTIME_FILES` | | handed to **each runner** (not to build programs): deployed files plus linked shared libraries, **TAB-separated**. A runner that copies a program onto a device no longer has to work out which `.so` files to take |
| `MCPP_PKG_CONFIG_LIBDIR` | `mcpp::pkg_config_libdir()` | the pkg-config view directory |

WARNING: a dependency's **install hook** receives `MCPP_TARGET` / `_OS` / `_ARCH` / `_ENV`, and `MCPP_COMPILER` /
`MCPP_CXX_STDLIB` are always written but **empty at that moment** — the toolchain is resolved after the dependency graph,
because a package in the graph may supply a target-side layer. Do not read them in an install hook. Every variable is written
explicitly, so a hook never sees an inherited value from the parent process.

**Name sanitizer** (shared by `MCPP_FEATURE_` / `MCPP_DEP_` / `MCPP_TOOL_`): uppercase, non-alphanumeric -> `'_'`
[tool_store.cppm:182-186 (`sanitize_env`); the three-channel precedence comment is at :157-159, and `MCPP_DEP_<pkg>_BIN_<tool>`
is assembled at :190-191].

WARNING: **dependency name collisions are warned about** [build_program.cppm:649-655 (`_DIR`) and :662-671 (`_LINKAGE`); the
tool-name variant is at :713-715]: `foo.bar` and `foo-bar`, or a
bare `zlib` and another dependency's short name `zlib`, sanitize to the same variable name. mcpp **keeps the first** and
warns about the conflicting value:
```
build.mcpp: dependency name collides on <VAR> (kept '<a>', ignored '<b>') —
rename one dependency to disambiguate
```

WARNING: **`MCPP_BUNDLE_DIR` is the only correct way to locate resources inside a self-contained bundle**
[docs/10-pack-and-release.md]. `/proc/self/exe` breaks under `self-contained` (the kernel sets it to the **loader**), so "look for
resources next to the executable" resolves to `lib/` instead of the bundle root, and it fails **silently**: blank GUI
text (fonts gone), `assets/` not found, helper binaries not located.
```c
const char *base = getenv("MCPP_BUNDLE_DIR");   /* set by run.sh */
```
If the application cannot be changed, use `--mode vendored`.

## 4. The `MCPP_HOME` resolution chain (memorize this)

[src/home.cppm:67-105], in priority order:
1. **The `$MCPP_HOME` environment variable** (explicit override — CI / development / multiple instances)
2. **`<binary-dir>/..`** — self-contained mode, when mcpp sits at `<root>/bin/mcpp`. Release tarballs and `xlings install mcpp` use this layout, so **the unpacked tree is the home**
3. Fall back to `$HOME/.mcpp` (Windows `%USERPROFILE%\.mcpp`; if neither is set, `cwd/.mcpp`)

**Step 2 has two disqualifying cases** [:87-98]:
- **dev builds**: the path has a `target` ancestor directory (`.../target/<triple>/<fp>/bin/mcpp`)
- **xlings packages**: `.../data/xpkgs/xim-x-mcpp/<ver>/bin/mcpp` — creating a nested xlings sandbox inside the xpkgs
  directory breaks toolchain installation (nested XLINGS_HOME) and loses installed toolchains when the mcpp package
  version is upgraded

WARNING: **this explains the warning in `tools/dev-mcpp-path.sh`**: mcpp resolves MCPP_HOME from **the binary's own
location**, so **a binary copied elsewhere is a different binary as far as several tests are concerned** —
`30_dev_binary_home.sh` fails on the copy and passes in place.

Derived paths: `cache_root() = root()/build-cache/v1` [:108-110]; `legacy_bmi_root() = root()/bmi` [:112-114];
`registryDir = mcppHome/registry` [src/config.cppm:67 (declaration), :618 (assignment)];
`xlingsHome() = xlingsHomeOverride.empty() ? registryDir : xlingsHomeOverride` (the override comes from
`config.toml [xlings].home` — **not an env var, it requires writing the global config file**).

## 5. Variables mcpp **sets** itself (rather than reads)

| Variable | When set | Rationale |
|---|---|---|
| `MCPP_OFFLINE` / `MCPP_LOCKED` / `MCPP_JOBS` / `MCPP_TOOLCHAIN` | the pre-scan of the corresponding flag (`--locked`/`--frozen` rides the same side channel and the row used to omit it) | src/cli.cppm:172 (offline), :184 (locked), :190,192,201 (jobs), :197,199 (toolchain) |
| `XLINGS_HOME` | **set fresh on every run, never persisted**, points at `<MCPP_HOME>/registry` | src/xlings/xlings.cppm:1095,1104,1113,1390,1547,1553 |
| `XLINGS_SUBOS_LD_PATHS=0` | declared **for this process and all its children** | that wrapper appends `-rpath "$XLINGS_SUBOS_LIB"` to every link, and that variable refers to the **active shell's** SubOS, which is not the one mcpp resolved; inheriting it would put **a second libc** on the artifact's search path [src/cli.cppm; docs/91-toolchain-internals.md] |
| `XLINGS_PROJECT_DIR` | set for project-level xlings invocations; global-mode provisioning does not set it | src/xlings/xlings.cppm |
| **`XLINGS_ACTIVE_SUBOS` — removed, not set** | stripped from **every** xlings invocation (`env -u` prefix on POSIX, a scoped guard that restores it on Windows) | src/xlings/xlings.cppm:285,1206 |

**`XLINGS_ACTIVE_SUBOS` is explicitly called out as not consulted** [docs/23-the-project-environment.md]: "Neither
`XLINGS_ACTIVE_SUBOS`, `current`, the compiler's owner home, nor a CLI/env override is a third selection rung." There are exactly two SubOS
selection modes: `McppDefault` (no `[xlings].subos`) and `NamedSubos(name)` (written explicitly, including `"default"`).
WARNING: that used to be a statement about mcpp's *selection logic* only — the variable was still **inherited** by the bundled xlings, where
it outranks a home's own `activeSubos`. Since it names a SubOS of the *shell's* xlings home while mcpp's registry is a different home whose
tool, sysroot and pkg-config paths all derive from `subos/default`, a shell that had run `xlings subos use <name>` sent bootstrap tools and
project payloads into a same-named other SubOS and left the pkg-config view empty. mcpp now strips it on every call.
=> The symptom is indistinguishable from a broken registry. **Do not re-bootstrap a home on that evidence alone.** Keep the
`env -u XLINGS_HOME -u XLINGS_BIN` prefix regardless — the engine only guards this third variable.

## 6. flag / env equivalence quick reference

| flag | Equivalent env | Difference |
|---|---|---|
| `--offline` | `MCPP_OFFLINE=1` | the flag literally sets it, fully equivalent |
| `--locked` / `--frozen` | `MCPP_LOCKED=1` | same as above |
| `-j N` | `MCPP_JOBS=N` | same as above |
| `--toolchain SPEC` | `MCPP_TOOLCHAIN=SPEC` | same as above |
| `--cache MODE` | `MCPP_BUILD_CACHE=MODE` | **the flag wins** |
| `--no-color` | `MCPP_NO_COLOR=1` / `NO_COLOR=<any non-empty>` | `MCPP_NO_COLOR` **only honors first character `1`**, `NO_COLOR` accepts any non-empty value |
| `--verbose` | `MCPP_VERBOSE=1` | `--quiet` still wins; `MCPP_LOG_LEVEL` takes priority over `--verbose` |
| `[build] allow_host_libs = true` | `MCPP_ALLOW_HOST_LIBS=1` | equivalent for a single run |

WARNING: **`MCPP_NO_AUTO_INSTALL=1` is not the same thing as `--offline`** [docs/05-dependencies.md]. It is the older,
**narrower** spelling: it gates toolchain auto-install only, while `--offline` additionally blocks index refresh, downloads,
`git ls-remote`/`clone` and the first-use bootstrap. **Do not conflate them.** Both, however, now gate tool provisioning.
Precedence when they disagree: `--offline` on the command > `MCPP_OFFLINE=1` for the session > `[index] auto_refresh = false`
in `config.toml` (no automatic refresh, downloads still allowed).

## 7. What `--offline` actually forbids (exhaustive)

| Action | Behavior | Location |
|---|---|---|
| index refresh | **silently skipped, returns 0** ("Offline is absolute … Reported as success") | src/xlings/xlings.cppm |
| explicit `mcpp index update` | hard refusal, exit 1 | src/pm/index_management.cppm |
| dependency download | hard error, names the package | prepare.cppm |
| toolchain auto-install | hard error; `--offline` subsumes `MCPP_NO_AUTO_INSTALL` | prepare.cppm |
| **tool provisioning (`[xlings.workspace]`)** | hard error, **naming what it would have installed** | prepare.cppm:1541-1571 |
| git dependency clone/fetch | hard refusal; `file://` and local paths are **exempt** | prepare.cppm |
| **first-use sandbox bootstrap** (index clone, `ninja`, `patchelf`) | skipped, one line printed per process | src/config.cppm:791-820 |
| MSVC repair | not repaired | prepare.cppm |

The check sits **at the moment of download**; every local action before it (reading descriptors, resolving versions,
reusing already-installed packages) is allowed. When a dependency is missing there is **no silent degradation — always a
hard error**.
Only two things need the network at all: resolving a branch with no commit in the lock, and cloning a commit not yet cached.
A `git =` value naming a local directory or a `file://` URL is therefore never refused offline.

WARNING (stale-claim retired): older notes say tool provisioning **has no offline or flag check at all** and there is **no
opt-out**. That was true of the original implementation and is not true now — `--offline`, `MCPP_OFFLINE=1` and
`MCPP_NO_AUTO_INSTALL=1` all refuse it and name the set. The reason to keep a project-local `MCPP_HOME` is now disk
ownership (provisioning spans the whole dependency graph), not the absence of a switch. See `../SKILL.md` §1.5.
