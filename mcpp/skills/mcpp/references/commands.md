# Reference: complete mcpp command surface

> Baseline: the `cl::App` declarations in `src/cli.cppm` of mcpp source `main @ b30e70c4` (version `2026.9.21.3`), read from
> source on 2026-09-23. The tables were first cross-checked entry by entry against `--help` of the `mcpp 2026.9.15.2` release
> binary (2026-09-16); line citations of the form `[:N]` are from that tree unless marked "re-read". The 2026.9.16.1-2026.9.21.3
> additions below were read from source only.
> `2026.9.24.1` (`main @ b4824697`, read 2026-09-24, source and docs only) did not touch `src/cli.cppm`: every declaration below
> holds unchanged. What moved is behaviour behind three commands - `toolchain list` / `toolchain default` on Windows, the spelling
> parser shared by `toolchain` and `--toolchain`, and one new `self doctor` check - noted in their sections.
> Delta from `2026.9.15.2`: **nothing was removed or renamed; the 28 command words are unchanged.** New options: `test --no-run`;
> `pack --release` / `--dev` / `--message-format`; `why --features`; `--features` everywhere now also accepts `<dep>/<feature>`.
> Delta from `2026.8.30.2` (previous window): **nothing was removed or renamed.** New at the CLI level:
> the `emit sbom` and `emit build-database` subcommands, and the options `--locked` / `--frozen`, `--stale` /
> `--dry-run` / `--older-than`, `--all-versions`, `--spec`, `--accel` / `--no-accel`, `--runner` / `--list-runners` /
> `--no-runner`, plus existing option names appearing on more commands.

## 1. Global options

| Flag | Short | Meaning | Evidence |
|---|---|---|---|
| `--quiet` | `-q` | suppress status output | src/cli.cppm:318 |
| `--verbose` | `-v` | detailed progress on stderr | :320 |
| `--no-color` | - | disable color | :322 |
| `--offline` | - | never go online (index refresh / download / toolchain install / first-use bootstrap) | :324 |
| `--locked` / `--frozen` | - | **fail if the resolution differs from `mcpp.lock`** (also `MCPP_LOCKED=1`); refuses the fast path so the assertion runs | :331,:334; :97 |
| `--protocol-version` | - | print the machine-output protocol document (JSON); **answered before anything parses** | :341,:1081-1085 |
| `--help` / `-h`, `--version` / `-V` | - | intercepted before the App | - |
| `--explain CODE` | - | **legacy form**, special-cased before the App | - |

**Pre-scan mechanism**: `--quiet` / `--no-color` / `--verbose` / `--offline` / `--locked` / `--jobs` / `--toolchain` are
scanned once **before** App parsing; the last **four** (`--offline` / `--locked` / `--jobs` / `--toolchain`) are **passed down by
setting env variables**:

```
--offline          -> MCPP_OFFLINE=1
--locked/--frozen  -> MCPP_LOCKED=1        (src/cli.cppm:184)
--jobs N / -jN     -> MCPP_JOBS=N
--toolchain SPEC   -> MCPP_TOOLCHAIN=SPEC
```

The pre-scan stops at a bare `--`, so the `-j` in `mcpp run -- -j 4` goes to the child process.
This side channel is why `--toolchain` reached `run` / `test` / `pack` long before those commands declared it as an
option — the value arrived, the spelling was refused. They declare it now.

## 2. Top-level command table (28 known words)

```
new build run test clean add remove update search publish pack emit xpkg
toolchain cache index self explain version dyndep why resolve stage
bmi-equal coff-def bmi-compile bmi-supervise bmi-await
```
[src/cli.cppm:1103-1109]; no match -> `error: unknown command '<x>'` + usage, **exit code 127** [:1112-1115].

`dyndep` / `stage` / `bmi-equal` / `coff-def` / `bmi-compile` / `bmi-supervise` / `bmi-await` are marked `(internal: invoked by
ninja)`; humans should not type them.

Aliases: `mcpp explain <code>` = `mcpp self explain`; `mcpp version` = `mcpp self version`; `mcpp help` and bare `mcpp` print
usage and exit 0 [:872-886, :954-963].

### Hidden internal command `__action-stamp`

`mcpp __action-stamp <stamp>... -- <cmd>...`. Purpose: an action with `role="check"` outputs a stamp file, but analyzers
(clang-tidy) write nothing on success. Previously every check needed a wrapper script, and an action's command is argv with no
shell, which cannot be expressed on Windows. Now the engine itself is the portable wrapper. **The stamp is written only when the
command exits rc=0, and an existing file is left alone** => older wrapper scripts keep working verbatim. Missing arguments exit
2; otherwise the **child exit code is passed through**.

### `mcpp stage` is an internal command with a public contract

`mcpp stage --verify content --output <dst> <src>` copies one file, creating the destination's parent and writing only when the
bytes differ. ninja calls it, and so does any build-program action that reaches the engine through `${mcpp.self}` — which is the
portable way to copy a file from an action, since an action's command is argv with no shell. **The argument shape is therefore a
contract.** `--verify` accepts `content` (default) | `size`.
WARNING (stale-claim retired): older write-ups say `--verify` defaults to `size` because the help text said so. The
implementation default was `content` all along, and the help text has been corrected. **When recording a default, read the
implementation, not `--help`** — that mistake has now been made twice in this surface (`--profile` was the other).

## 3. Per-command flags

### `mcpp new [name]` [:345-354]
| Flag | Value |
|---|---|
| positional `name` | package directory name, **not required** (`--list-templates` does not need it) |
| `-t, --template SPEC` | `bin` (default) or `[ns.]pkg[@ver][:template]` |
| `--list-templates PKG` | list templates |

Template default rule (in order; must be unique) [docs/specs/package-identity.md]: exactly one `default = true` -> that
one; no default but the version has only one template -> that one; several with no default -> **hard error** pointing at
`--list-templates`. **There is no `--variant`.** Template resolution is **atomic**: a failed download / render / hook /
validation leaves no half project directory behind [docs/01-getting-started.md].

### `mcpp build` [:355-391]
| Flag | Short | Value | Meaning |
|---|---|---|---|
| `--configure-only` | | | generate `compile_commands.json` only. WARNING: **not read-only**, see below |
| `--print-fingerprint` | | | print the toolchain fingerprint and its 11 inputs |
| `--cache MODE` | | `global`(default)\|`local`\|`off` | see `../SKILL.md` §8 |
| `--jobs N` | `-j` | number or `auto` | really sets `MCPP_JOBS` |
| `--toolchain SPEC` | | e.g. `llvm@22.1.8` | really sets `MCPP_TOOLCHAIN` |
| `--no-cache` | | | **deprecated** spelling of `--cache=off`, and genuinely equivalent: `coldBuild = no_cache \|\| cacheMode == Off`, and either one wipes `target/<triple>/<fp>/` [src/build/execute.cppm:828-835; src/cli/cmd_build.cppm:129-133]. The help text's "(**also** clears the build dir)" is misleading - `--cache off` alone clears it too |
| `--target TRIPLE` | | | looks up `[target.<triple>]` |
| `--accel SPEC` | | e.g. `'cuda12.8+{sm_89}'` | device backends and architectures; overrides `[build] accel` |
| `--no-accel` | | | **an explicit request for no accelerator**, not merely the absence of `--accel` |
| `--static` | | | forces `-static`; on Linux pair it with `--target <arch>-linux-musl` |
| `--package NAME` | `-p` | | build only the named member. WARNING: **turns off the fast path** |
| `--profile NAME` | | | `dev` (default) \| `release` \| `dist` \| a `[profile.*]` name |
| `--release` / `--dev` | | | shorthand for `--profile release` / `--profile dev`; `--profile` wins if both are given |
| `--features LIST` | | comma-separated | activate root-package features; `<dep>/<feature>` opens a dependency's feature for this command (2026.9.16.1+, never a root feature, never a macro; a token naming no dependency warns, an error under `--strict`) |
| `--cap LIST` | | `blas=openblas,...` | pin capability providers |
| `--strict` | | | promote manifest schema warnings to errors |
| `--workspace` | | | build all members |

WARNING: **`--configure-only` is not a read-only operation**: `build.mcpp`, missing dependencies or toolchains, lock/resolution
metadata and build-directory metadata may still be updated. **Run it only in a trusted workspace.**
[docs/01-getting-started.md]. The stable integration contract is the **exit code plus `compile_commands.json`**; **stdout is for
humans only**. The CDB it produces covers ordinary sources **and** the discovered tests.
=> For a compile database **without** writing into the project, use `mcpp emit build-database --spec compile-commands`.

WARNING: **flag set that bypasses the fast path** (non-empty means bypass, because the cached `build.ninja` was generated without
them and the fast path would silently ignore them): `--profile` / `--features` / `--strict` / `--target` / `--static` / `--cap` /
`-p` / `--cache` / `--accel` / `--no-accel` [src/cli/cmd_build.cppm:205-208]. Declaring active `[hooks]` also bypasses it, and so
does `--locked` (from inside `try_fast_build`).

### `mcpp run [bin] [-- args...]`
The positional is a **binary name, not a triple**. The source carries a long comment explaining that this rename is
load-bearing: it used to be called `target`, and `ParsedArgs::value()` falls back from an unset option to the **positional of
the same name**, so `mcpp run q` reported `error: unknown target 'q'`.

| Flag | Meaning |
|---|---|
| `--target TRIPLE` / `--target-triple` | the alias is the only spelling 2026.8.19.1 had, kept for compatibility |
| `-p, --package NAME` | single member, no `--workspace` fan-out |
| `--cache MODE` / `--no-cache` / `--toolchain SPEC` | as on build |
| `--accel SPEC` / `--no-accel` | run the variant built for that device set |
| `--features LIST` | comma **or space** separated here |
| `--profile NAME` / `--release` / `--dev` | which artifact to build and run. *changed in 2026.9.16.1*: `--profile` wins over a shorthand here too (on `run` the shorthand used to win) |
| `--runner NAME` | reach the artifact through a named runner a package supplied |
| `--list-runners` | list the named runners this project supplies, and exit |
| `--no-runner` | execute the artifact directly, ignoring `[target.<triple>].runner` |
| `--format NAME` | run the distributable a `pack --format NAME` would produce; **refused together with `--no-runner`** |

**Exit status is the program's own** [docs/50-machine-output.md:199-201]: `0`-`124` passed through unchanged; `125`-`127` mean the
spawn was attempted and refused (`127` not found, `126` found but not executable - also the answer when `--format` produced a
directory no runner reaches - `125` anything else); `2` means mcpp refused before attempting anything. A launch failure always
writes a reason to stderr; the program's own status never does.

### `mcpp test [pattern] [-- args...]`
| Flag | Default | Meaning |
|---|---|---|
| positional `pattern` | | **plain substring containment**, case-sensitive, no `--exact` |
| `--target TRIPLE` | | |
| `--accel SPEC` / `--no-accel` | | test the variant built for that device set |
| `--message-format FMT` | `human` | `human`\|`json` (**NDJSON, one line per test**) |
| `--list` | | **list only: no toolchain resolution, no build, no run** |
| `--no-runner` | | run the test binaries directly, ignoring `[target.<triple>].runner` |
| `--no-run` | | (2026.9.21.3+) build and link every selected test for `--target` and execute none; result `N built, not run`, **exit 0**. **Refused together with `--no-runner`** (exit 2) |
| `--timeout SECS` | **300** | kills tests still **running**; `0` = unlimited |
| `--build-timeout SECS` | **0 (unlimited)** | kills compiles/links still running; **POSIX only**, silently ignored on Windows |
| `--workspace-timeout SECS` | **0 (unlimited)** | stop the fan-out after the timeout and report what already ran |
| `--profile NAME` | `dev` | `dev` \| `release` \| `dist` \| a `[profile.*]` name. WARNING: **no `--release` / `--dev` here** - unlike `build` / `run` / `pack` / `emit build-database`, `test` declares neither shorthand (still true at 2026.9.21.3, src/cli.cppm:489-533 re-read), so `mcpp test --release` is `error: unknown option: --release`, exit 2. Write `--profile release` |
| `--toolchain SPEC` | | build the tests with this toolchain for one invocation |
| `--features` / `--cap` / `--strict` | | same as build |
| `-p, --package NAME` | | member directory basename **or** member relative path, exact equality |
| `--cache MODE` / `--no-cache` | | same as build |
| `--workspace` | | fan out over all members (serial, replanned per member) |

Arguments after `--` are **forwarded verbatim to every** test binary. WARNING: the two timeouts are orthogonal: **a link that
never returns is a `--build-timeout` case; no `--timeout` value stops it.** The reason `--build-timeout` has no default: a member
in mcpp-index builds OpenCV from source, taking 1019s on Linux and 1289s on Windows. Testing is **framework-agnostic**: one file,
one binary, either a bare main or gtest via `[dev-dependencies]`.
**Which files are tests is configurable** with `[test] discover` (see `mcpp-toml.md`); `--list` falls back to `tests/**/*.cpp`
when the manifest cannot be loaded, so its answer can differ from the real set.
**Exit status**: `0` every test ran and passed (or, under `--no-run`, every selected test built) / `1` a test ran and failed,
or did not compile / **`2` a test was built and never run** [src/build/execute.cppm:2898 at 2026.9.15.2]. `2` is also the
usage-error code, so a script cannot tell them apart by number; read stderr, or read `not_run` out of the JSON.
WARNING: `mcpp build --target <t>` is **not** a substitute for `test --no-run`: `build` compiles the package, so a member whose
sources are all under `tests/` compiles only its dependencies and exits 0.

### `mcpp clean`
`--bmi-cache` also clears the global build cache. `--stale` removes only the `target/<triple>/<fingerprint>/` directories no
recorded build considers current; `--dry-run` lists and deletes nothing; `--older-than <DURATION>` (`12h`, `3d`, `0`; default
`1d`) keeps unrecorded directories written more recently than that. **Any one of the three selects the stale mode**, so
`mcpp clean --older-than 3d` cannot fall through to the full wipe. The stale mode is **mutually exclusive with `--bmi-cache`**
(exit 2: `target/` is per project, the build cache is machine-wide and has its own gc), a negative duration is refused (exit 2),
and with **no build record at all** it refuses rather than guessing. Hierarchy in the table in §6.

### `mcpp why [topic]` / `mcpp resolve`
`topic` in `toolchain` | `runtime` | `deps` | `runners` (default all). Flags: `--target TRIPLE`, `--toolchain SPEC`,
`--features LIST` (2026.9.16.1+; root features and `<dep>/<feature>`, resolved as `build --features` would), `--format json`. `resolve` shares `cmd_why` with `why` and has `--explain`. WARNING: see `../SKILL.md` §1.4 - not a read-only
command; refused still exits 0; `--format` only works for `toolchain`.
`mcpp why deps` prints the `graph` object recorded in `resolution.json`: every package, every request with the key **as written**
and the table that declared it, and each library's link form with its reason (`default` / `package-default` / `requested` /
`package-kind` / `row-kind` / `packaged` / `no-sources` / `prebuilt-inputs` / `no-loader` / `static-libc`). **Assert against that
record, not against a warning's wording.** `mcpp why runners` and `mcpp run --list-runners` are the two entry points when a test
comes back `NOT RUN`; both run `prepare`, so neither is read-only.

### `mcpp add <pkg>` / `remove` / `update` / `search`
`add` has `--dev` (adds to `[dev-dependencies]`). The positional is required for `remove`/`search` and optional for `update`.
`mcpp add <bare name>` writes the **canonical dotted form** back into `mcpp.toml`.
`search` appends each hit's published versions - the union of the descriptor's per-OS version tables, SemVer-descending,
de-duplicated, **latest 3 by default** with truncation marked `, ...`; `--all-versions` lists them all. A package whose
descriptor is unreadable or that has published nothing keeps the old two-column shape: enrichment is best-effort display, never
a new failure path, and never an input to resolution. `mcpp add`'s cross-namespace did-you-mean suggestions carry versions too.
WARNING: the versions come from the **local** index copy, so they are as fresh as the last refresh - and a script parsing
`mcpp search` by column now sees a third field.

### `mcpp publish`
`--dry-run` (print `xpkg.lua`, no upload), `--allow-dirty`. **The pipeline is entirely local** (no credentials, no upload, no
network writes) [src/publish/pipeline.cppm:69-186]: find root -> git cleanliness check -> manifest parse -> module graph scan ->
`git archive` -> `sha256sum` -> derive the GitHub Release URL from `[package].repo` -> generate `target/dist/<name>.lua` ->
**print the manual PR steps**. **Checks it does not do**: version conflicts / duplicate names in the index, licenses,
package-name conventions (the last lives in `mcpp xpkg parse`, run by index CI).

### `mcpp pack [target]`
| Flag | Short | Meaning |
|---|---|---|
| positional `target` | | **a target name from `[targets.*]`, not a triple**; its `kind` decides what gets packed |
| `--mode` | | `system` \| `vendored` (default) \| `self-contained` \| `static` |
| `--target TRIPLE` | | **repeatable**, one leg per triple |
| `--format` | | `tar` (default; Windows targets produce `.zip`) \| `dir` \| **any format the resolved graph provides**. **Unrelated to machine output** |
| `--output PATH` | `-o` | bare filename -> lands in `target/dist/`; contains a directory -> literal path |
| `--profile NAME` | | defaults to `[build] default-profile`, otherwise **release** |
| `--release` / `--dev` | | (2026.9.16.1+) shorthands, `--profile` wins over them. *changed*: on 2026.9.15.2 and earlier `mcpp pack --release` was `error: unknown option`, exit 2 |
| `--toolchain SPEC` | | build with this toolchain for one invocation |
| `--features LIST` | | applies to **every build pass of the pack** (each `--target` leg, both passes of a dispatched format); accepts `<dep>/<feature>` |
| `--message-format FMT` | | (2026.9.16.1+) `human` (default) \| `json`: **one** `mcpp.pack` envelope on stdout after the command finishes, every human line (including build programs' output) on stderr |
| `--no-strip` | | ship exactly as built |
| `--debug-symbols DIR` | | write separated `*.debug` here (discarded by default) |

*changed in 2026.9.16.1*: **what gets stripped**. On every row whose images carry debug info (i.e. not Mach-O, not MSVC PE),
the program (as a shared library on Android), every shared library a link unit of **this graph** produced, and the staged copy of
the toolchain's own runtime (e.g. NDK `libc++_shared.so`) are stripped (`--strip-unneeded` for libraries). Libraries from the
store, the host or a prebuilt a package deployed are never touched (their bytes are the publisher's, and may be signed). The
`Packing` line says "stripped" only where something was. A packaging member reads the decision through `mcpp::pack_strip()` and
`mcpp::pack_debug_symbols_dir()`.

WARNING: **the two targets** (positional = target name, flag = triple) are the single easiest thing to get wrong in the whole
CLI.
WARNING: **`--format` is an open value set.** `tar` and `dir` are engine-owned archive shapes; any other name is looked up among
the packages in the **resolved** graph, which declared it with `mcpp::provides_pack_format("<name>")`. Consequences: an unknown
value is refused **after** resolution (so a typo costs a full prepare, including network and toolchain work) but **before**
anything is compiled, and the refusal names the formats actually available in this build rather than a fixed list. An empty
`--format=` is its own error, and a dispatched format on a **library** target is refused (a library has no single staged tree).
A dispatched format runs `prepare` **twice**; budget for it on a throttled machine.
WARNING: what gets reported as `Packed` is the **terminal** artifact - the output of a requested artifact action that no other
introduced action consumes - not the first output of a chain. `mcpp run --format` refuses a format that ends in more than one.
The staged tree's `.stage-manifest` is a readable, assertable artifact: a `closure = walked | not-walked` line (with a reason on
`not-walked`), `needs<TAB><name><TAB><path|platform|unresolved>` lines, and one line per staged file. `tar`/`dir` still refuse an
incomplete closure; a dispatched format receives the tree with the status recorded.
WARNING: **`--mode` and `[pack] default_mode` are two different vocabularies, by design** [docs/10-pack-and-release.md]: the manifest key
**only accepts** `static` | `bundle-project` | `bundle-all`; `bundle-project`/`bundle-all` are compatibility aliases for
`vendored`/`self-contained`; **`system` cannot be written in the manifest at all**.
WARNING: **tarball suffixes are a frozen wire format and do not follow mode renames** [docs/10-pack-and-release.md]: `vendored` -> no
suffix, `self-contained` -> `-bundle-all`, `static` -> `-static`, `system` -> `-system`.

### `mcpp emit <xpkg|sbom|build-database>`

`mcpp emit` is "generate a document describing this project". Three subcommands:

| Subcommand | Flags | Notes |
|---|---|---|
| `xpkg` | `-V/--version VER`, `-o/--output FILE`, `--namespace NS` | the index descriptor. Selectors naming **only** an operating system (`cfg(linux)`, `cfg(os = "windows")`, `cfg(macos)`, `cfg(unix)`) map into the descriptor's platform blocks; every other selector keeps its warning |
| `sbom` | `-o/--output FILE` | CycloneDX 1.5 read out of `mcpp.lock`. **Resolves nothing, builds nothing, no network.** Unknown licences are written `NOASSERTION` rather than omitted; purls are `pkg:mcpp/<ns>/<name>@<ver>`. There is no `-p`: it reports the **project root's** recorded resolution |
| `build-database` | `--spec s1\|compile-commands`, `--format json`, `-o FILE`, plus build's full selector set (`--target --toolchain --accel --no-accel --static -p --profile --release --dev --features --cap --strict --workspace`) | plans like `build --configure-only` **without writing into the project** |

`emit build-database` produces an S1 "C++ Build Database: IDE Profile" 0.2.0 document (a profile of WG21 P2977R2), or with
`--spec compile-commands` the entries `compile_commands.json` would contain. Rules: SPEC-005 `docs/specs/build-database.md`.
Planning happens under `$MCPP_HOME/cache/build-database/<key>` - a pure cache, safe to delete, managed by neither
`mcpp clean --stale` nor `mcpp cache gc`. `mcpp.lock` is read from the project and **never written back**; a disagreement is
reported as `MCPP_LOCK_WOULD_CHANGE`, which is a free staleness signal worth surfacing in a gate.
```
mcpp emit build-database                                    # S1 document to stdout
mcpp emit build-database --spec compile-commands -o compile_commands.json
mcpp emit build-database --format json -o bd.json           # mcpp.build-database envelope, atomic write
mcpp emit build-database --workspace --target x86_64-linux-musl --profile release
```
WARNING: its declared effects are `init-mcpp-home, read-project, network, write-global-cache, exec-build-script` - **no
`write-project`, which is the command's whole reason to exist**, but network and build-program execution are both on the list.
Read-only with respect to the project, not with respect to the machine. An invalid `--spec` or `--format` exits 2; a failure
emits an envelope with diagnostics and **no `data`**, exit 1.

### `mcpp xpkg parse <file.lua>`
The positional is **not declared with `.arg()`**; it is taken as positional(0), so `--help` does not show it. Flags: `--json`
(legacy bare payload, **kept forever**), `--format json` (with envelope), `--allow-unknown` (unknown mcpp-section keys error ->
warning), `--all-os` (validate every per-OS section), `--allow-split-name` (**OBSOLETE**, exists only to keep 0.0.105-era index
CI running).

### `mcpp toolchain <sub>`
| Subcommand | Positionals | Flags |
|---|---|---|
| `list` | - | `--format json` |
| `install` | `compiler` (`gcc`\|`llvm`\|`msvc`\|`emsdk`\|`android-ndk`, or `gcc@16.1.0`), `version` (may be partial) | `--target TRIPLE` |
| `default` | `spec` (required), `version` (optional) | `--target TRIPLE` (omitted = host) |
| `remove` | `spec` (required) | `--target TRIPLE` |

`install`/`default` accept **both forms** (`gcc 16.1.0` and `gcc@16.1.0`), and the version may be partial. With `--target`, the
family may be omitted entirely (taken from the target row's convention pin): `mcpp toolchain install --target
x86_64-windows-gnu`. WARNING: `mcpp toolchain install --help` does **not** print the positional's vocabulary; `emsdk` and
`android-ndk` are only visible in the source [src/cli.cppm:732]. `ndk` is **not** an accepted alias - the only spelling is the
one the index uses.
The only namespace a spelling may carry is `xim:` - `mcpp toolchain install xim:gcc@16.1.0` is the same as `gcc@16.1.0`, another
prefix is refused with `'<ns>:' is not a toolchain namespace`, and `xim:<family>@system` is refused naming `<family>@system` and
`xim:<family>@<version>` (outside msvc only the second is valid, see troubleshooting §L1)
[src/toolchain/registry.cppm:539-550,574-581 @ b4824697]. For msvc the prefix matters: `mcpp toolchain default msvc@<toolset>`
on Windows accepts a toolset the machine already has without installing anything (`Default set to msvc@<toolset> (installed: <cl.exe
path>; ...)`), while `xim:msvc@<toolset>` always goes to the payload [src/toolchain/lifecycle.cppm:1177-1200 @ b4824697]. On
Windows `mcpp toolchain list` follows the detected MSVC line with `installed toolsets (pin one as msvc@<toolset>):`, one line per
complete toolset with its product and `(default)` on the instance default (human output only; `--format json` does not list them)
[:548-600 @ b4824697].
**The Targets block of `mcpp toolchain list` is the authority on "can this machine build this"**, and it is the same table as
`docs/21-the-target-triple.md`. Tier words are now **`verified` / `preview` / `planned`**; a `planned` row is refused rather
than attempted, and a target absent from the block cannot be built here at all. The row count moves as platforms land (29 at
this baseline), so **re-read it rather than asserting a number**.
WARNING: `toolchain` and `pin` are not two passes over the same field: `toolchain` = what this row is associated with, `pin` =
can only be the target table's convention. Selecting "the row whose convention is a particular gcc" **requires reading `pin`**.
A resolution line now names the **payload** separately from the family, because families absorb ecosystem toolchains (`emsdk`
normalises into the llvm family, and `Resolved llvm@6.0.9` would otherwise be indistinguishable from the real `xim:llvm`).

### `mcpp cache <sub>`
`dir` / `list` (`--json`, `--format json`) / `info <pkg>` (the declared positional is `pkg`: `mcpp cache info --help` prints
`mcpp cache info <pkg>`, and omitting it gives `error: required argument 'pkg' missing`, exit 2; whether a `pkg@ver` suffix is
also parsed is **not verified here** - it needs a populated cache) / `prune --older-than N{s|m|h|d}` / `gc --max-size N{MiB|GiB}
--older-than ...` (excludes std entries) / `clean [--deps(default)|--std|--all|--legacy]` / `verify`. This surface is unchanged
from the previous baseline, as is the on-disk layout
`$MCPP_HOME/build-cache/v1/pkg/<index>/<pkg>@<ver>/<key16>/entry.json`.
WARNING: `mcpp cache list` is **not sorted by last use** - `cache_list` does not sort at all. And the key inputs reported by
`mcpp cache info` renamed one field (`macos_deployment_target` -> `min_platform_version`), which both breaks a script matching
the old name and, by construction, misses every entry written before the rename.

### `mcpp index <sub>`
`list` / `add <name> <url>` / `remove <name>` / `update [name]` / `status` (**offline**) / `pin <name> [rev]` (defaults to the
current lock rev) / `unpin <name>`.
WARNING: the filter argument of `update [name]` **only affects project-level custom indices**; global repos are always synced as
a whole, because `xlings update` has no per-index mode to call. The help text says so now
(`Refresh local registry clones (global repos always sync in full)`), so this is a documented limitation, not a bug - and
`mcpp index update <name>` is never the cheap targeted operation it looks like.
WARNING: the index **only refreshes when dependencies cannot be resolved locally**; it never refreshes just because time has
passed [docs/05-dependencies.md]. `^1.2` is resolved against the version set known to the **local** index, so a version
published since the last refresh is invisible. Controls, in precedence order: `--offline` on the command, then
`MCPP_OFFLINE=1`, then `[index] auto_refresh = false` in `config.toml` (which stops automatic refresh but still allows
downloads). `MCPP_NO_AUTO_INSTALL=1` is the older, **narrower** spelling and gates only toolchain auto-install.
WARNING: do not confuse `[cache] search_ttl_seconds` with refresh policy - it bounds how stale `mcpp search` and
`mcpp index status` may be, and the generated config comments say so because people get this wrong.

### `mcpp self <sub>`
`init [--force]` (delete the registry and initialize from scratch) / `doctor` / `env [--format json]` / `config [--mirror
CN|GLOBAL]` / `version` / `explain <code>`.
WARNING: **`explain` takes the engine's own `E00NN` codes, not the `MCPP_*` diagnostic codes of machine output.** The two vocabularies
are disjoint. `mcpp self explain MCPP_MANIFEST_UNKNOWN_KEY` (and the `mcpp explain` / `mcpp --explain` aliases) is `error: unknown error
code ...` / `known codes: E0001..E0006`, **exit 2** - the error message is itself the enumeration, and `--help` states no vocabulary at
all. **There is no lookup command for the `MCPP_*` codes** in §5.2 [verified on 2026.9.15.2].
WARNING (stale-claim retired): `mcpp self doctor` no longer has a device section, and `mcpp.toolchain.devicehost` is gone.
Those readings moved out of the engine to rule packages, which state them with `mcpp::fact` / `mcpp::floor`. Any note telling
you to check CUDA or accelerator state with `self doctor` is describing a removed feature.
`mcpp self doctor --offline` is genuinely offline now (it no longer bootstraps an empty home first), which makes it safe to run
inside a restricted sandbox.
`mcpp self doctor` also runs `Checking gcc include-fixed headers` on every host: each installed gcc-family payload (native,
musl-gcc, MinGW, cross) is scanned for `include-fixed/` headers carrying the `auto-edited by fixincludes` banner - frozen copies of the
build machine's C library headers that sit ahead of the C library the project resolves. A hit is a warning, not an error, and
names the files, the frozen source path and the remedy: `mcpp index update`, then `mcpp toolchain remove gcc@<v>` and
`mcpp toolchain install gcc@<v>` (plus `--target <t>` for a cross payload). With no hit it prints `no fixincludes-frozen headers in
installed gcc payloads` or `no installed gcc-family payloads to check` [src/doctor.cppm:116-164,618-691 @ b4824697]. Any warning
makes `mcpp self doctor` exit 1 (2 if it also reports an error) [src/doctor.cppm:757 @ b4824697], so a CI step gating on doctor
turns red on a home with an affected payload.

## 4. Exit codes

Since `2026.9.1.1` this is a written contract, SPEC-003 [docs/specs/exit-codes.md §2], not just observed behaviour.

| Code | Scenario | Notes |
|---|---|---|
| 0 | success; `--help`/`--version`/`mcpp help`/no arguments | "the command completed what it promised" |
| 1 | ran, the request was legal, the result is failure | **can arrive together with an envelope on stdout** |
| 2 | usage error (parse failure, missing subcommand, unsupported `--format`, manifest/scan errors) | the spec requires it to precede any side effect |
| **4** | **environment not ready** - global config load or first-time init failed (`$MCPP_HOME` unwritable, `config.toml` corrupt, xlings bootstrap failed) | doctor.cppm:87,1280; pm/index_management.cppm:32,78,… |
| 70 | internal error (uncaught exception, `EX_SOFTWARE`) | worth an upstream issue |
| 127 | unknown top-level subcommand | cli.cppm:1112-1115 |
| passthrough | `__action-stamp` forwards the child exit code | |

Rules the spec adds on top of the table: the classification **must not** change across versions; a client **must not** use exit
codes for capability detection (the only cross-version test is parsing stdout); every non-zero exit leaves a reason on stderr.
=> In a gate, **4 means this machine's mcpp home is broken**, not "this build failed". Do not retry it as a build failure. With
a project-local `MCPP_HOME`, a permissions or sandbox problem lands here rather than on 1.

WARNING: **SPEC-003 v1.0 is dated 2026-09-01 and its table is no longer complete.** Three commands widened the space afterwards:
- `mcpp run` passes the program's own status through for `0`-`124`, and uses `125`-`127` for "the spawn was attempted and
  refused".
- `mcpp test` uses **`2`** for "a test was built and never run", which the table calls usage error.
- `mcpp emit build-database` uses **`1`** where every sibling project command uses `2`: a missing or unloadable manifest is an
  enveloped failure with no `data`, exit 1, not a usage error. Only an invalid `--spec` or `--format` exits 2 there. Measured in a
  directory with no `mcpp.toml` on 2026.9.15.2: `emit build-database` -> `1` (`error: no mcpp.toml found in current directory or any
  parent`), while `emit sbom` / `emit xpkg` / `build` / `test --list` / `why deps` / `clean` all -> `2`. => A gate reading that `1` off
  this table treats "this directory is not an mcpp package" as a build failure worth retrying.
=> **Give exit codes per command.** Do not quote the SPEC-003 table as if it covered everything; it covers the enveloped
commands.

The cmdline library originally `println`-ed parse errors to **stdout** and returned 1, so `mcpp cache list --format json | jq`
received `Error: unknown option: --format`. mcpp now takes the `ParseResult` itself, sends everything "mcpp says about itself"
to **stderr**, and exits 2 on every usage error.
=> **When parsing machine output, stdout contains only the payload.**

## 5. Machine-readable output

### 5.1 Three switches (not equivalent to one another)

| Invocation | Shape | Commands |
|---|---|---|
| `--format json` | **with envelope** | `self env` / `xpkg parse` / `cache list` / `toolchain list` / `why toolchain` / `emit build-database` (**6**) |
| `--json` | **bare payload** | `xpkg parse`, `cache list` (**2**) |
| `--message-format json` | NDJSON stream | `mcpp test` (hand-concatenated, no schemaVersion) |
| `--message-format json` | **one envelope**, printed after the command finishes | `mcpp pack` (2026.9.16.1+; kind `mcpp.pack`) |
| `--protocol-version` | static capability document | global, **answered before any parsing** |

`--message-format` is the spelling for a command whose `--format` already names its **product** (`test`, `pack`); the shape
follows the kind - tests stream because they finish over time, a pack has one result.

WARNING: `json` is the **only** value `--format` accepts; `ndjson` is reserved and **rejected** - "asking for it is an error,
not a silent fallback". A bad `--format` goes to **stderr, exits 2, and leaves stdout empty**: `error: unsupported --format
'yaml'; expected: json`.
WARNING: `--json` is **not deprecated and prints no warning** - `--json` keeps its payload for ever; a warning would land in the
middle of the payload.
WARNING: `mcpp pack --format` / `mcpp run --format` name a **distributable** format, **not machine output**; giving either
`json` is rejected. **Only the ten invocations in the table above produce machine output; every other command has none** -
`emit sbom` and `emit xpkg` included, as well as `publish`, `index *` (`index status` too), `build`, `run`, `clean`, `new`,
`stage`, `add/remove/update/search`, `toolchain install/default/remove`, `cache dir/info/prune/gc/clean/verify` and
`self init/config/version/explain/doctor`. Verified: `mcpp emit sbom --format json` -> `error: unknown option: --format`, exit 2;
`mcpp emit sbom --help` lists only `-o, --output <FILE>`, so **`emit sbom` writes CycloneDX to stdout or `-o`, not an envelope** -
a gate step that reaches for `emit sbom --format json` gets a usage error. `--porcelain` / `--machine` do not exist anywhere in the
repository.

### 5.2 Envelope fields [src/wire.cppm; docs/50-machine-output.md]

```
schemaVersion  int      = kEnvelopeVersion = 1   (bumped only when the envelope shape changes)
kind           string
kindVersion    int                               (independent per kind; all 7 current kinds are 1)
effects        string[]   <- always present; [] means "nothing", absent means "unknown"; different claims
mcpp           {version, protocol:{min,max}}
data           object     <- OMITTED when the command failed
diagnostics    object[]
```

WARNING: **a failure is one envelope with diagnostics and no `data`, exit 1.** `data` is not an empty object in that case, so
`jq .data.x` yields `null`. Test for `data`'s presence before reading through it.

**Full effects set (6)** [docs/50-machine-output.md:162-167]: `init-mcpp-home` / `read-project` / `write-project` /
`write-global-cache` / `network` / `exec-build-script`. Gating advice: most gates only care about `exec-build-script` and
`write-project`, and can ignore `init-mcpp-home`.
*changed in 2026.9.16.1*: an envelope's `effects` are what **this run did**; `network` is observed (listed when the run started an
index refresh, an install or a git remote operation, even one that failed or hit its bound; never under `--offline`). The
`--protocol-version` table (§5.5) is what the command **may** do.

**Diagnostic object**: `code` (**always present**, e.g. `MCPP_MANIFEST_UNKNOWN_KEY`; WARNING: these are **not** the codes
`mcpp self explain` accepts - that command knows only `E0001`..`E0006`, and feeding it an `MCPP_*` code exits 2, see §3) /
`severity` (error|warning|note) /
`source` (always `"mcpp"`) / `message` (**never parse it**) / `path` (**omitted** when absent) /
`range{start{line,column},end{line,column}}` (omitted when absent). Positions are **1-based** and `column` counts **UTF-8
bytes**. Omission beats zero: "`line: 0` would point at a position that does not exist".
Three codes worth knowing by name, all attached to commands that plan without writing:
`MCPP_LOCK_WOULD_CHANGE` (the resolution differs from the project's `mcpp.lock`, which this command does not write),
`MCPP_GENERATED_FILE_NOT_MATERIALIZED`, `MCPP_BUILD_DATABASE_STD_UNIT_UNDESCRIBED`. Failure codes of `emit build-database`:
`MCPP_BUILD_DATABASE_NO_PROJECT`, **`MCPP_OFFLINE_DOWNLOAD_REQUIRED`** (2026.9.16.1+: an offline plan needs a toolchain, package, git
revision or index download - one online run removes it, so do not report it as a project defect) and
`MCPP_BUILD_DATABASE_PLAN_FAILED`. `mcpp pack --message-format json` fails with `MCPP_PACK_FAILED` and the command's own exit status.

### 5.3 `data` of the seven kinds

| kind | Command | data fields |
|---|---|---|
| `mcpp.env` | `self env --format json` | `initialized, mcppHome, registry, xlingsHome, xlingsBinary, config, buildCache, mcppVersion` |
| `mcpp.xpkg` | `xpkg parse --format json` | `namespace, name, versions, standard, import_std, sources, include_dirs, generated_files, generated_contents, targets, unknown_keys`; a descriptor with no inline `mcpp` table reports `"form": "A"` |
| `mcpp.cache` | `cache list --format json` | `{root, entries[]}` |
| `mcpp.toolchain.list` | `toolchain list --format json` | `{host, toolchains[], targets[]}`; toolchain rows `{family,version,default}` (VS-installed ones carry `source:"system"`); target rows `{target,note,toolchain,pin,status,default}` |
| `mcpp.why.toolchain` | `why toolchain --format json` | `requested{target,toolchain}` / `status` (ok\|refused) / `reason` / `compiler{family,version,driver,chosenBy{origin,requiredBy,replaced}}` / `triple{requested,toolchain,llvm}` / `cLibrary{mode,path,origin,suppliesTarget}` / `layers[]{layer,interface,impl,origin,subset}` |
| `mcpp.build-database` | `emit build-database --format json` | `spec{name,version}` / `database` (the S1 document, or the compile-commands entries) / `watch` (the inputs whose change can change the document) / `inputs-fingerprint` (`fnv1a:<16 hex>` over those inputs, the mcpp version and the selectors) |
| `mcpp.pack` | `pack --message-format json` (2026.9.16.1+) | `artifacts[]{path (absolute), type (file\|directory), format (the --format value, tar when omitted), targets[] (canonical triple of every leg that went into it)}` / `stage{dir, manifest, closure (walked\|not-walked)}`, `stage` is `null` for a library package or when no tree was staged. Per-run effects `read-project`, `write-project`, `write-global-cache`, plus `exec-build-script` when a build program ran |

`compiler.chosenBy.origin` is one of five constructed status phrases: `[toolchain] in mcpp.toml` / `your default` / `target
default` / `required by the dependency graph` / `first-run default`.
WARNING: `layers[].interface` **changed value** for the `c-abi` layer - it reports the C library name, so a payload-supplied
glibc reads `glibc` rather than `gnu`, and the Windows MinGW form reads `ucrt`. `musl`, `picolibc` and `libSystem` are
unaffected. A script matching the literal `gnu` needs updating.

**Full `reason` token set (19)** [docs/50-machine-output.md:378-398]: `unknown-target`, `ambiguous-request`,
`compiler-requirement-conflict`, `tier-planned`, `host-cannot-serve`, `capability-pin`, `convention-unreplaced`, `os-mismatch`,
`layer-requirement`, `layer-ordering`, `exclusive-capability`, `version-floor-unmet`, `accel-mismatch`,
`accel-backend-undeclared`, `device-source-unconsumed`, `host-module-missing`, `tool-version-conflict`,
`shared-library-cxx-runtime`, `other`. Added at 2026.9.16.1-2026.9.20.1 [docs/50-machine-output.md at `b30e70c4`]:
`offline-download-required`, `package-cycle`, `program-cxx-runtime-split`, `static-package-in-two-images`, `c-env-unrealisable`,
`c-env-verification-mismatch`, `platform-dependency`, `interface-not-provided`, plus four the engine had been emitting without a
table row - `apple-sdk-absent`, `lld-required-absent`, `host-tool-toolchain`, `std-module-precompile` - for **31** in all. Since
2026.9.20.1 CI (`.github/tools/check_reason_tokens.sh`) keeps the table and `src/build/refusal.cppm` equal in both directions, so
the table is now a reliable enumeration. `interface-not-provided` is also printed in brackets inside `mcpp build`'s own refusal
message. **Read this for machine-readable classification; do not parse the English sentence** -
before these tokens existed, a machine consumer could only separate such refusals from any other by matching prose.
Of the eight new ones, two are the likely arrivals for an ordinary multi-member workspace: `tool-version-conflict` (two
declarations name one xlings package at versions that cannot both hold) and `version-floor-unmet`.

### 5.4 NDJSON events of `mcpp test --message-format json`

WARNING: **hand-concatenated strings, not routed through `wire.cppm`; no schemaVersion, no envelope.**

| Event | Fields |
|---|---|
| single test result | `member, test, status(pass\|compile_fail\|run_fail\|`**`not_run`**`\|`**`built`**`), exit_code, signal, duration_ms, timed_out, compile_output, run_output, `**`reason`** (`built` is 2026.9.21.3+, only under `--no-run`) |
| `--list` entry | `member, test, main` |
| `--list` summary | `summary{total}` |
| no match | `error:"no-tests-matched", filter` |
| package-level build failure | `error:"package", compile_output` |
| member summary | `summary{member,passed,failed,`**`not_run,not_run_reason`**`,`**`built`**`,elapsed_ms,build_ms,run_ms}` |
| workspace summary | `workspace_summary{members,passed,failed,`**`tests_not_run`**`,`**`tests_built`**`,failed_members[],`**`unrunnable_members[]`**`,not_run[],elapsed_ms}` [src/cli/cmd_build.cppm:643-649 at 2026.9.15.2; `built`/`tests_built` per docs/50 at `b30e70c4`] |

WARNING (2026.9.21.3): **`built` and `not_run` are different answers - never add them.** `not_run` = mcpp tried and could not
(question open, exit 2); `built` = `--no-run` said not to execute (the build was the whole question, exit 0).

WARNING: the `status` vocabulary went from three values to four, and `not_run` carries `exit_code: 0`. Two consequences:
a consumer counting "anything that is not `pass`" as failure now over-counts (safe direction, wrong numbers), and one counting
only `run_fail` **under-counts** (unsafe). In `workspace_summary`, `not_run` keeps its original meaning (members stopped by
`--workspace-timeout` that never started) while `tests_not_run` and `unrunnable_members` are the new per-test quantities - a
member whose tests were all built and never run is invisible to the old fields.

In JSON mode `ui::set_quiet(true)` guarantees stdout carries only NDJSON (a line once leaked out because the muting happened too
late, breaking strict parsers).

### 5.5 Measured `--protocol-version` output of the 2026.9.15.2 binary

```json
{
  "commands": {
    "cache list":           { "effects": [] },
    "emit build-database":  { "effects": ["init-mcpp-home","read-project","network",
                                          "write-global-cache","exec-build-script"] },
    "self env":             { "effects": ["init-mcpp-home"] },
    "toolchain list":       { "effects": ["init-mcpp-home"] },
    "why toolchain":        { "effects": ["init-mcpp-home","read-project","network",
                                          "write-global-cache","exec-build-script"] },
    "xpkg parse":           { "effects": [] }
  },
  "envelope": { "max": 1, "min": 1 },
  "kind": "mcpp.protocol",
  "kinds": { "mcpp.build-database":1, "mcpp.cache":1, "mcpp.env":1,
             "mcpp.toolchain.list":1, "mcpp.why.toolchain":1, "mcpp.xpkg":1 },
  "mcpp": { "version": "2026.9.15.2" },
  "schemaVersion": 1
}
```
Note that `emit build-database` deliberately omits `write-project` while keeping `network` and `exec-build-script` - the exact
shape of "read-only with respect to the project, not with respect to the machine".
*changed in 2026.9.16.1* (from source at `b30e70c4`, not from a binary run): the table gains
`"pack": ["init-mcpp-home","read-project","write-project","network","write-global-cache","exec-build-script"]` [src/cli.cppm:1092-1094]
and `kinds` gains `"mcpp.pack": 1` [src/wire.cppm:72-93], seven kinds in all.
WARNING: the illustrative sample inside `docs/50-machine-output.md` lists fewer kinds than the real output - **read the real
output, do not copy the sample**. This document is also the only cross-version capability test that is allowed: SPEC-003 §3.3
forbids using exit codes for it.

### 5.6 Detection rule (follow it; nothing else works)

> "**Detect the protocol by parsing stdout. Never by exit code, and never by 'the command did not fail'.**"
> [docs/50-machine-output.md]

Parse stdout as JSON and **require both `schemaVersion` and `kind` to be present**. Reason: on any mcpp older than
`--protocol-version`, that flag is itself an unknown option, and unknown options used to **print human text to stdout, exit 1,
and leave stderr empty** - success and failure on the same channel. `--protocol-version` is only an **optimization** (one fewer
spawn), not the basis of detection. SPEC-003 §3.3 states the prohibition side of the same rule: **a client must not use exit
codes to decide whether this mcpp supports a feature.**

**Stability guarantee** (per kind, within one kindVersion): fields are **only added, never removed**; field meanings **never
change**; breaking changes bump the version, and overlapping `protocol.min`/`max` keep both readable.

### 5.7 One ambiguity in `self env` (take the conservative reading)

The docs say `mcpp self env --format json` is **deliberately read-only and does not create `$MCPP_HOME`**, while the human
version does create it; the comments and implementation in `src/cli/cmd_self.cppm` support this. The static table behind
`--protocol-version`, however, marks `self env` as `init-mcpp-home` **as a whole** [src/cli.cppm:1046-1048, whose comment says
"on a fresh machine it does create $MCPP_HOME -- measured: six entries"]. **Both can hold** (the table is per command, the doc
is per sub-form). => **Gate against the more conservative table**; but to ask for paths on a fresh machine without touching
disk, use the `--format json` branch (it reports `initialized: false`). Use it rather than reimplementing home resolution
yourself - the `mcpp` on `PATH` may be an xlings shim rather than the real binary.

## 6. Cleanup hierarchy cheat sheet

| Means | Scope cleared |
|---|---|
| `--cache off` (`--no-cache` is the deprecated spelling; the two are equivalent) | **only this run's `target/<triple>/<fp>/`**; sibling fp directories untouched |
| **`mcpp clean --stale`** | **only the `target/<triple>/<fp>/` directories no recorded build considers current**, per member, reporting each one's size |
| `mcpp clean` | the whole `target/` |
| `mcpp clean --bmi-cache` | additionally deletes all of `$MCPP_HOME/build-cache/v1` (both `pkg/` and `std/`) |
| `mcpp cache clean` / `--deps` | `build-cache/v1/pkg/` |
| `mcpp cache clean --std` | `build-cache/v1/std/` |
| `mcpp cache clean --all` | both of the above |
| `mcpp cache clean --legacy` | `$MCPP_HOME/bmi` (pre-v1) |
| `mcpp cache gc --max-size … --older-than …` | LRU reclaim inside `build-cache/v1`, excluding std entries |
| *(nothing)* | `$MCPP_HOME/cache/build-database/`, `$MCPP_HOME/cache/tool/` - pure caches, **managed by no command**; delete by hand |

`mcpp clean --stale` output shapes, so a script can read them:
```
would remove target/<triple>/<fp>  (123.4 MiB)
removed target/<triple>/<fp>  (123.4 MiB)
kept    target/<triple>/<fp>  (not in the record, but written 12h ago; see --older-than)
Removed 3 directories (1.2 GiB)
Nothing stale under <target>: every fingerprint directory is recorded as current
```
Three refusals, all exit 2: `--stale` combined with `--bmi-cache`; a negative `--older-than`; and **no build record at all**
(it refuses rather than guessing, naming `target/.build_cache`). Remember that `mcpp test` writes no record, so a tree where
only tests have run has none.
WARNING: the record is an **8-entry LRU** keyed per `(target, profile)`. A member built across more than eight axis
combinations loses its oldest entries, and those directories then fall back to age protection - one extra rebuild, expected.
WARNING: **there is no `--force` and no `--rebuild`** (`--force` belongs to `mcpp self init` only).

## 7. Operational conclusions an agent can use directly

1. **`mcpp test --list [--message-format json]` is a zero-cost enumeration** - it returns before toolchain resolution and
   building, and works even for tests that currently do not compile. First choice for CI sharding.
2. **A gate run can only be shortened with `-p`, not with the filter** (the plan always contains every test); **but `-p` turns
   off the fast path** - the trade-off does not stack. To change *which* tests exist at all, use `[test] discover`.
3. **The only two correct ways to force a rebuild**: `mcpp clean` then rebuild; or `mcpp build --cache off` (plus
   `mcpp cache clean --all` to exclude the global cache). To reclaim space *without* forcing a rebuild, use
   `mcpp clean --stale`, `--dry-run` first.
4. **`mcpp emit sbom` is the safest command that reads the resolution** (no resolution pass, no network, no build), so it is safe
   in a restricted sandbox and safe as a non-blocking gate step. Its honesty is exactly `mcpp.lock`'s - pair it with `--locked`.
   It is not, however, the only effect-free command: the engine's own capability table declares exactly two entries with an empty
   effects set - **`cache list` and `xpkg parse`** (§5.5) - and unlike `emit sbom` those two are enveloped, so their success is
   machine-detectable. `emit sbom` is absent from that table and therefore carries no declared effects either way.
5. **Put `--locked` on gate legs only.** It turns the lock into a drift assertion, and it costs the fast path on every run.

## 8. Commands never to run

```bash
find $MCPP_HOME/registry -mindepth 1 -maxdepth 1 ! -name data -exec rm -rf {} +
```
`data/xpkgs` sits at **depth 2** and is not named `data`, so one careless second pass **deletes the entire payload store
(roughly 800 MB of toolchains)** [docs/11-publishing-a-library.md]. Recovery: `mcpp self doctor` (re-provision), then
`mcpp update`.

And the general form of the same mistake: **`mcpp clean` without `--stale`**. It is the full wipe of `target/`, and the reason
nobody used to run it is exactly that. If the goal is disk space, the command is `mcpp clean --stale --dry-run` first.
