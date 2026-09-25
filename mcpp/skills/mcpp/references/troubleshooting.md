# Reference: mcpp troubleshooting, indexed by symptom

> Baseline: source `main @ 2fc7b5b0` (version `2026.9.15.2`), cross-checked on the `mcpp 2026.9.15.2` release binary,
> dated 2026-09-16; §K and the rows it adds to §J cover `2026.9.16.1`-`2026.9.21.3` and were read from source at
> `main @ b30e70c4` (2026-09-23), not reproduced on a binary; §L and K9 cover `2026.9.24.1`, read from source and docs at
> `main @ b4824697` (2026-09-24), not reproduced on a binary either. Each entry gives: symptom -> root cause -> how to tell -> what to do. Entries describe the
> **current** engine; where an older one behaved differently and you may still meet it, that is stamped inline, and the
> per-version history is in `version-notes.md` §2.

## A. The build "succeeds" but did nothing

### A1. `Finished dev in 0.00s`, but I did change the code
That line is the signature of a fast-path hit. The test is whether `Compiling` appears in the output.
Possible root causes, most likely first:

1. **The change was rolled back or restored with `tar` / `cp -p`**, so mtime was restored to the old
   value. All three of mcpp's staleness layers (the fast path's `sources_newer_than`, ninja, and
   `ArtifactStamp{exists,size,mtime}`) are mtime-based, and tar preserves size as well, so **all three
   are fooled**.
   Fix: always roll back with something that updates mtime (`sed -i`, an editor write,
   `git checkout --`); if you already used a tar-like tool, `touch` first. [field-tested 2026-08-30]
   The same trap reaches **host tools** built from a `path` dependency: their store key is a stat imprint
   of the tree that includes mtime, so a restored older tree can re-hit the old entry.
2. **An axis changed that the fast path cannot see.** The record in `target/.build_cache` compares a
   named set — target triple, profile, cache mode, feature set, toolchain request — and replays the last
   build that matches [src/build/execute.cppm:100-127]. Anything outside that set is invisible to it.
   Historically each omission produced exactly this symptom in turn: switching features, switching
   `--toolchain`, switching `--accel` / `--no-accel`, and changing a file declared through
   `rerun_if_changed`. All four are covered now, so on `2026.9.15.2` this cause should be rare — but it
   is the first thing to suspect on an older engine, and the shape to keep in mind if a new axis appears.
   Fix on an older engine: `mcpp clean` before switching axes.
3. You assumed the fast path honors some flag. **It does not**: any non-empty
   `--profile`/`--features`/`--strict`/`--target`/`--static`/`--cap`/`-p`/`--cache`/`--accel`/`--no-accel`
   **bypasses** the fast path, and `-p` is the common one. So does `--locked`, and so does declaring an
   active `[hooks]` table.
4. **You upgraded the engine and the first build after that was rejected once.** A `.build_cache` entry
   written by an older engine lacks the newer comparison lines, so it is rejected and rewritten — one
   extra full build, expected, not a regression.

**The only two correct ways to force a rebuild**: `mcpp clean` then rebuild; or `mcpp build --cache off`
(deletes only this one `target/<triple>/<fp>/`). Add `mcpp cache clean --all` to exclude the global
cache too. **There is no `--force` / `--rebuild`, and no "force rebuild but keep the directory" switch.**
=> To reclaim disk **without** forcing a rebuild, that is a different command: `mcpp clean --stale`
(`--dry-run` first), per member. See `commands.md` §6.

### A2. A static library builds fine, but consumers are all undefined symbols
**Empty link unit.** The dependency's `install()` was skipped because of a package identity conflict, so
the version directory holds no sources, yet mcpp still plans its library as usual. With no members,
`ar rcs` **exits 0 and writes an 8-byte archive**, so the build **reports success**.
mcpp **rejects input-less link units at plan time and names the target** (since 2026.8.30.1).
The shared-library side has a different symptom: `/bin/sh: 1: -shared: not found`.

### A3. A `role = "source"` action never runs and the compiler reads an empty file
**Generated headers have no ordering edge.** A generated `.cpp` is an input to an edge; a generated `.h`
is not — headers arrive through `-I`, never appear as an edge input, and the depfile that would record
them does not exist until after one successful compile.
So an action whose outputs are **all headers** becomes a node in `build.ninja` that **nothing can reach**,
and it never runs. It looks like an intermittent race (because `prepare_actions` writes a **zero-byte
placeholder** for every declared Source output, so the file is always on disk), but it is
**deterministic** and reproduces identically five runs in a row.
Fixed in 2026.8.30.1 (#536): every package that declares a gating action gets a phony, and **every
compile edge** of that package takes it as an order-only prerequisite; **non-TU outputs no longer get
placeholder files**. The same batch made `check`'s `blocking` field **actually read** for the first time
(previously it was typed, emitted, parsed, documented in two languages and given examples, with no code
reading it).

### A4. A `role = "check"` keeps "passing" but was never satisfied
WARNING: **a missing stamp does not fail the build** — ninja just reruns that edge forever, "which looks
like a passing check that is quietly never satisfied" [docs/30-build-mcpp.md]. The build stays green; the
only symptom is work being redone repeatedly.
mcpp writes the stamp on the action's behalf via the internal command `__action-stamp` (**only when rc=0**).

### A4b. A generated artifact is stale and the build is green
The action's declared inputs are what mcpp compares. A command that discovers the rest by **reading** source
(a compiler resolving its own `#include` graph) reports nothing back, so changing one of those files
triggers no rebuild at all. Declare `depfile` on the action: mcpp then emits `depfile =` and `deps = gcc`
for that edge and ninja folds the listed files into the dependency set.
WARNING: do **not** also declare the depfile as an `output()` — `deps = gcc` makes ninja consume and delete
it, so an edge promising that output is dirty for ever.

### A5. `mcpp test -p <member>` is green, but that member has no tests at all
WARNING: **it exits 0 for a member with no tests** — "no tests" and "tests passed" look identical in CI
output.
Fix: run `mcpp test -p <member> --list --message-format json` first and read `summary.total`.
Related and newer: a member whose tests were **built and never run** exits **2**, not 0, and reports
`status: "not_run"` with a `reason`. A gate asserting "not 1" or `failed == 0` passes that; require
`rc == 0`, and under `--workspace` read `tests_not_run` / `unrunnable_members` rather than the older
`not_run` list (which still means "members stopped by `--workspace-timeout` before they started").

### A5b. `mcpp test` reports NOT RUN on a target this machine can execute
`[target.<triple>].runner` is honoured on hosted cross targets. If any manifest declares a runner for that
triple and the program is missing, mcpp **fails with a message** rather than executing the artifact bare —
which is the fix for an older silent `127`, but surprising the first time you meet it on a host that could
have run the binary natively.
Diagnose with `mcpp run --list-runners` or `mcpp why runners` (both run `prepare`, so neither is free).
Fix: `--no-runner` on the host that executes the artifact natively. That is the documented exit, not a way
of bypassing a check — "this host can execute this artifact" is a fact about the host, and the manifest has
no host axis to state it on.

### A6. Adding `std-freestanding-nolibc` next to a project that has a C library
It "fails **silently** rather than loudly" [docs/40-baremetal.md]: that package's objects enter the link
unconditionally and define `memcpy` **first**, so the libc archive members are never pulled in; the
byte-at-a-time implementations replace the optimized ones **with no report at all**.
Correct approach: `features = ["nolibc"]`.

### A7. A commented-out `import` or `module` line changed the build
The module scanner walks three mutually exclusive states in one pass (code / block comment / raw string).
Before `2026.9.11.2` it did not: an `export module y;` inside a block comment made an ordinary `.cpp` the
recorded **producer** of that module (so the real provider was never looked for, and importers were told
`imports must be built before being imported`), and a `// R"(` put the raw-string pass into a state it
never left, hiding every later `import` from the scanner while the compiler still saw them — **a missing
dependency edge**, which under parallelism is an intermittent ordering failure rather than a clean error.
=> If your sources contain commented-out module or import lines, or comments containing `R"(`, an old
unexplained flaky-build history may date from exactly here. On the current engine this is fixed; there is
nothing to work around.

## B. Configuration written but not taking effect

| Symptom | Root cause | Evidence |
|---|---|---|
| A key you wrote is reported as unsupported and it **used to be silent** | Unknown-key sweeps were added to `[features]`, `[runtime]`, `[target.<pred>.runtime]` and the `[target.<sel>]` sub-table set, and an unknown `cfg` key is reported rather than evaluating false. **These are real defects surfacing, not regressions** — but a `--strict` leg goes red until cleaned up | toml.cppm:879-905, :2405-2418, :3160-3170, :2914-2950 |
| `[build] linkage = "dynamic"` has no effect | **The key does not exist**; it is reported, not ignored in silence - you get `[build] has unsupported key 'linkage' (ignored)`, a schema warning that `--strict` promotes to a hard error. `x86_64-windows-gnu` defaults to static; the only opt-out is **`[target.<triple>] linkage`** | modules/manifest/src/toml.cppm:2173-2215; docs/20-toolchains.md |
| `cfg(feature = "x")` always false | cfg **cannot** reference features. The key-value predicate keys are `os`/`arch`/`family`/`env`/`accelerator`, plus the five resolved layers `compiler`/`compiler-runtime`/`kernel-abi`/`c-abi`/`c++-abi` | prepare_inputs.cppm:175,197 |
| `cfg(musl)` / `cfg(gnu)` / `cfg(msvc)` always false | There are exactly 4 bare-word predicates: `windows`/`linux`/`macos`/`unix`. musl must be written `env = "musl"` | prepare_inputs.cppm:266-269 |
| A `cfg(<layer> = …)` section **suddenly started taking effect** after an upgrade | It was parsed and silently dropped before `2026.9.1.1`, so a package could build against the wrong C library and look fine. It is live now. => **Re-read the contents of every such section written against an older engine** | version-notes.md §2 |
| A dependency written in **both** `[dependencies]` and `[target.<sel>.dependencies]` resolves differently than it used to | On matching rows the conditional declaration **replaces** the unconditional one (`2026.9.14.2+`); it used to lose, silently dropping options written only in the conditional table. Nothing errors either way | version-notes.md §2 |
| A `path` dependency warns about its identity on every build | A `path`/`git` dependency takes the identity **its own manifest declares**; a key normalising to a different one warns once per declaring edge. Fix the key (or add a `namespace` to that manifest) | mcpp-toml.md §8.1 |
| A dependency's `[targets.*] required_features` never takes effect | Target gating exists in exactly one place and tests the **root's** active feature set. WARNING: for `kind="shared"` targets, if a package contains any shared target at all, **all** of its objects are taken out of every consumer's link | |
| A dependency's own `[toolchain]` has no effect | **It is ignored entirely.** The only legal channel is `requires = ["mcpp:compiler=<family>"]` | reads the root manifest |
| A dependency's own `[target.<sel>.abi]` has no effect | Deliberate: the ABI is one property of the whole artifact, so **only the root manifest may state it**. A dependency's table is reported as `abi/dependency-table` and ignored; a dependency states its *need* with `requires_abi` | docs/22-target-side.md |
| `mcpp index update <name>` did not refresh that index | The `[name]` filter applies **only to project-level custom indices**; global repos always sync in full because `xlings update` has no per-index mode. The help text now says so — **documented limitation, not a bug to report** | src/pm/index_management.cppm |
| `[index.repos.<name>]` in `config.toml` did nothing | It used to seed only a home that did not yet exist. It reaches an existing home from `2026.9.14.2`; removing the table restores the previous entry. => **A table you added earlier and gave up on will start working after the upgrade** | src/config.cppm:405-413 |
| `MCPP_INDEX_MIRROR=...` has no effect | **The variable does not exist in mcpp** | whole-repo grep, still 0 hits |
| `[xlings] deps` warns, or `[xlings.envs]` fails the whole manifest | `[xlings.workspace]` is the one table. `deps` is superseded (warning; **error under `--strict`**) and **`envs` is a hard parse error** — the one manifest change in this window that stops a build outright | toml.cppm:2153-2156 |
| `1:1: error: expected key` on a manifest that looks fine | On an engine before `2026.9.9.1`, that is the signature of a **UTF-8 BOM** (MSVC writes one by default; `std::isspace` is false for those three bytes so the marker stayed on the first token). Both manifests and sources consume the BOM now, and UTF-16/32 markers are refused by name | version-notes.md §2 |

**Stale claims retired from this table** — if you find them in an older copy, they are wrong: `[features]` being the only
section with no unknown-key check; `[build] std-module*` warning the opposite of the truth; a bare integer `standard = 26`
being silently ignored; `cfg(c-abi = "musl")` being constant false; `[target.<p>.build] std-module-flags` not being
conditionable; `[hooks]` / `[workspace.build]` / `[workspace.package]` not existing. All fixed or shipped.

## C. Headers, symbols, linking

### C1. `reference to 'space' is ambiguous` (inside istream), or a clang frontend **SIGSEGV**
**A dependency unit picked up a cross-contaminated set of headers.** Two directions:

- **Different targets sharing one cache entry — fixed (three layers of coverage)**: the full triple
  (including the env field) enters the dependency cache key [cache_key.cppm:325, field at :84, JSON mirror at
  :276], the **C library header set** enters the key [:327, field at :130], and both the build directory
  and the fast path are slotted per target.
  The necessity of layer 2 is recorded from measurement [cache_key.cppm:101-120]: `driverIdentity`
  **by design cannot cover** the C library (`normalize_driver_output` deliberately erases `/home/`,
  `/tmp/` and `/var/` paths so entries can be shared across homes), so one clang sitting on two
  different glibc payloads produces the same key, and **the symptom is a clang frontend SIGSEGV**
  (`ASTReader::FindExternalVisibleDeclsByName`), not a readable diagnostic.
  => A local discipline of "clear the cache before switching between host and musl" can be retired.
- **A dependency unit picking up the wrong header set — only half fixed**: `[build] private_include_dirs`
  (2026.8.27.1) is **opt-in**, and without it the whole set is still published; and **`includeDirsAfter`
  has no corresponding private axis** (`pkg.publicUsage.includeDirsAfter =
  pkg.privateBuild.includeDirsAfter` [prepare.cppm:6268], the exact shape of the line that was fixed).
  => Keep the "clear the cache first" advice, and during the build temporarily move any other mcpp homes
  ($MCPP_HOME, plus any stale project-local `.mcpp`) out of the way (restore via trap).
- **Remaining boundary**: **two identically named subos under different homes are still one key** - a
  consequence, not a quoted fact. Derive it: the `<home>` tier deliberately factors the home *out* of the
  `--sysroot=<home>/registry/subos/default` token so entries stay shareable between homes
  [cache_key.cppm:432-444], which leaves the subos *name* as all that distinguishes them; what does separate
  them is the whole-project fingerprint, whose 11 inputs live elsewhere
  [modules/toolchain-model/src/fingerprint.cppm:116-129].

WARNING: another root cause in the same family: **`readdir` order is not a decision procedure** (the old
rule took the first glibc; a dependency carrying `xim:glibc@>=2.38` installed a second one, so the
compile side took 2.44 while the artifact's interpreter was still 2.39, linking `GLIBC_2.42` against a
runtime without those symbols; the failure surfaced on an **unrelated package**) [docs/91-toolchain-internals.md].

### C2. musl internal headers resolve to an old version (three safeguards for hand-written per-triple cfg)
**Symptom**: you bump the openkal version, yet the resulting binary's signature is "bit-for-bit identical".
**Root cause**: when rebuilding the clang per-triple cfg, `-I` entries were extracted from
`compile_commands.json`, **and that file accumulates across configurations rather than being a snapshot
of this build** — in one file 0.3.1 appeared 15077 times, 0.4.0 15095, 0.6.0 14862, 0.7.0 14874; after
`sort -u`, 36 lines interleaved two versions, and the old version's `musl/src/include` and
`musl/src/internal` **came before** the new one's, and the first `-I` match wins.
=> **What was built was the old version. "Bit-for-bit identical signature" is not evidence that the fix
did not work; it is evidence that this is the same binary.**
**Three safeguards** (miss one and you can repeat it) [field-tested 2026-08-30]:
1. **Delete all `compile_commands.json` before extracting `-I`** (measured: 36 entries dropped to 18,
   exactly half).
2. After extracting, **filter by the version currently resolved**, and assert "each package appears at
   exactly one version" before writing the cfg.
3. **Prove the version before running tests** (have the library print its own version line), and attach
   `mcpp.lock`.

**Two more**: write **only `-clang++.cfg`** — the bare-triple spelling poisons C compilation (mbedtls
hits musl internal headers, field-tested); and **the per-triple cfg is hand-written** — mcpp itself only
rewrites `bin/<driver>.cfg`, and **only rewrites files that already exist, it does not create them**
[src/toolchain/post_install.cppm:276,366-376], so **it is lost when the mcpp home is reinstalled**.

### C3. A static-archive consumer reports `archive has no index; run ranlib to add one`
`--strip-all` removes the archive symbol index. mcpp applies only `--strip-debug
--enable-deterministic-archives` to static archives; `--strip-all` to executables; `--strip-unneeded` to
shared libraries (keeping `.dynsym`, which **is** the export table) [docs/10-pack-and-release.md].

### C4. `undefined reference` to a module's mangled symbol
`sources` matched a file that is neither in the built-in extension set nor in `module_extensions`. mcpp
will **reject** it and name the file, extension and key — if you do not see that rejection, your mcpp is
too old (`module_extensions` **does not** degrade cleanly: old mcpp warns, ignores, and then **compiles
those files as ordinary TUs**, so module interfaces produce no BMI) [docs/11-publishing-a-library.md].

### C5. `import bar;` sits inside `#ifdef FOO` and `FOO` is right there in `defines`
WARNING: **`defines` cannot make a macro-guarded `import` legal** — mcpp's lexical prescan rejects
**any** `import` inside `#if`/`#ifdef` and **does not evaluate the condition**. Put the condition around
an `#include` in the global module fragment instead (mcpp#421) [docs/04-mcpp-toml.md].

### C6. The clang 20+ module landmine: any `x * y` SIGSEGVs the compiler frontend
A module that exports a **replacement operator template** **poisons name lookup for that operator in
every importer**: any TU that imports it and uses that operator **on any type at all** crashes. GCC 16
and Clang 18 are unaffected.
"The crash is **name-keyed**: one poisoned `operator*` declaration makes every `x * y` in every importer
crash, for entirely unrelated types. The function body is irrelevant."
**Rule of thumb: every template parameter should be pinned by the first function parameter.** Workaround:
deduce the whole operand type and add constraints.
Tracking number mcpp#256; the canary is `tests/e2e/150_clang_module_operator_template.sh`
[docs/20-toolchains.md].

### C7. `x.cppm` + `x.cpp` with the same basename produce a duplicate-symbol link error
They generate duplicate obj entries (the rsp file lists `obj/x.m.o` twice). **Independent upstream bug
candidate; not reported.** `[unverified]` at the 2026.9.15.2 baseline — field-tested on an older engine and
not re-tested. Note that object addressing changed in `2026.9.15.2` for sources outside the declaring
package (`obj/<declaring>/__pkg/<owner>/<path>`, or `__ext/<dir hash>/`), so re-test before reporting.

### C8. Exit code 134 with nothing printed at all
Two C++ runtimes reached the link line — typically a device-compiler lane configured for libstdc++ while the
artifact statically links libc++ — so a single `throw` was handled by two unwinders and the process aborted
before any message. Fixed in `2026.9.10.1` (such links use `--unwindlib=libgcc` and `--exclude-libs` for the
static archive's exports; a link with no second runtime is byte-identical). The duplicate-symbol warning now
says so explicitly when the duplicate set contains `_Unwind_*`.
=> If you see this on an older engine, look at the link line for a second C++ runtime, not at your own code.

## D. The artifact will not start, or will not ship

| Symptom | Root cause | What to do |
|---|---|---|
| Copying it by hand to another machine will not run | `mcpp build` output **is not a deliverable**: the loader and RUNPATH are tied to the build sandbox, and `PT_INTERP` points at the build machine's payload | Use `mcpp pack`; what survives a manual copy is `--target …-musl` or `--mode self-contained` [docs/10-pack-and-release.md] |
| Blank GUI text or a missing `assets/` inside a self-contained bundle | **`/proc/self/exe` is broken under self-contained** (the kernel sets it to the **loader**), and it fails **silently** | Read `MCPP_BUNDLE_DIR` as exported by `run.sh`; if you cannot change the app, use `--mode vendored` [docs/10-pack-and-release.md] |
| `error while loading shared libraries: libstdc++.so.6` | **One ELF rule**: an object carrying any `DT_RUNPATH` makes the loader **skip the entire inherited `DT_RPATH` chain** for that object's own dependencies. Measured matrix: stale absolute RUNPATH -> fails; **no tag at all -> works**; `$ORIGIN` -> fails; `""` -> fails. **It is whether the tag exists, not what it contains** | `mcpp pack` removes that entry. WARNING: the path string stays in `.dynstr` with nothing referencing it, so **a guard must read dynamic entries and must never `grep` the file bytes** [docs/12-binary-distribution.md] |
| A library the program **`dlopen`s** is missing at run time although the build was green | A library published through `runtime.library_dirs` is by construction **outside** the `DT_NEEDED` closure, so the ordinary check never walked it. `mcpp build` now walks that surface separately and publishes the result | `jq '.runtime.dlopen_surface' target/<triple>/<fp>/resolution.json`. Three readings: resolved (silent), present in the farm but dangling (silent — the machine has no driver), **nowhere at all (warning — a packaging gap)** |
| A program needing host capabilities (OpenGL and the like) is rejected at pack time under `self-contained`/`static` | "a bundle that carries its own libc cannot consume a library the host supplies" — a private glibc meeting an object the host already loaded "dies during relocation, before `main`" | Use `vendored`; it writes `HOST-REQUIREMENTS` at the bundle root [docs/10-pack-and-release.md] |
| After a plain `mcpp build`, `mcpp pack` cannot see the DLL or data file I placed by hand | **pack falls back to `release` while build falls back to `dev`**, so the two write to **different** `target/<triple>/<fp>/` | Set `[build] default-profile`, or pass `--profile` on both sides. The declarative channels `[runtime] deploy_files` and `[runtime] deploy` are unaffected [docs/10-pack-and-release.md] |
| A packed bundle suddenly contains **more** files than it used to | Deliberate fix: `mcpp pack` stages `deploy_files` **and** `deploy` beside the packed executable from `2026.9.12.2`. Packing read neither list before | Re-baseline any smoke test that asserts on bundle contents |
| On Windows, the glob `*.lib` finds no static library | `x86_64-windows-gnu` produces `libfoo.a` (GNU); only `-msvc` produces `foo.lib`. **Before 2026.8.3.3**, mingw builds on a Windows host produced `foo.lib` | Change the glob to `*.a` [docs/20-toolchains.md] |
| Consuming a prebuilt library package reports `'interface' does not match what was packaged` | The interface-digest gate. Its motivation was measured: swap two `int` members of a struct (the Itanium ABI does not mangle field order) and the consumer **compiles, links, runs and prints transposed data, with no tool issuing a single diagnostic** | Re-pack [docs/12-binary-distribution.md] |
| An old mcpp client can link a prebuilt package but runs neither gate | "the gate protects new clients only" | Mixed-version audiences must be called out in the release notes [docs/12-binary-distribution.md] |
| `mcpp pack --format <name>` succeeded but printed a **warning** about staging | For a **dispatched** format, a staging failure is a warning that lets the command continue (`${mcpp.stage_dir}` then refuses at the expansion point carrying that reason). `tar`/`dir` still fail outright | A gate that treats any warning as failure must distinguish this one |
| The artifact `--format` reported is not the one you wanted | It reports the **terminal** artifact — the output of a requested artifact action that no other introduced action consumes — not the first output of a chain. `mcpp run --format` refuses a format ending in more than one | |

WARNING: **Mach-O programs are rejected for packing on every host, including macOS** —
`LD_TRACE_LOADED_OBJECTS` is a glibc thing and dyld does not honor it; without that rejection the command
would **actually run the program** and parse its stdout as a dependency list.
`kind = "lib"`/`"shared"` **can** be packed normally on macOS [docs/10-pack-and-release.md].
WARNING: Windows -> Linux/macOS cross-packing **does not work**; Linux/macOS -> Windows **does** (the PE
closure is readable from the import table).

## E. Toolchains and targets

| Symptom | Root cause / what to do |
|---|---|
| `[toolchain] linux = "system"` is rejected | An explicit rejection with a pasteable alternative. **There is no escape hatch that replaces `system`** — you must write `<family>@<version>` or use `mcpp toolchain default`; on Windows `msvc@system` is the sole exception. (On engines before 2026.8.29.1, and with a `build.mcpp` present, the same manifest died with `posix_spawnp('') failed (error 2)` instead) |
| `gcc@system` reports "not a toolchain spelling" | A **separate, long-standing** rejection path [src/toolchain/registry.cppm]. Do not confuse it with the previous row |
| `--target aarch64-linux-gnu` is rejected | That row's tier is **planned**. **Writing the env field is itself an opt-out of completion**, so shortening it to `aarch64-linux` completes to `musl` and works — but note a bare `aarch64-linux` is **never** completed to Android. The escape hatch is an explicit `[target.<triple>] toolchain` |
| A target is refused even with an explicit `[target.<triple>] toolchain` | Some rows are **capability-pinned**: nothing else can emit WebAssembly, and Android's headers, per-API-level stubs and loader paths all live in the NDK. Declaring another family is refused **before** resolution. `mcpp toolchain list` is the denominator |
| An Android build is refused naming `min_api_level` | It is **mandatory** on Android rows — bionic refuses an unversioned triple (`sys/cdefs.h: Unversioned target triples are not supported!`), so a guessed level would produce an artifact that links here and fails to load on the device. The level enters the fingerprint; two levels never share a build directory |
| A build program fails under `--target wasm32-emscripten` (or any cross target) with a compiler-internal assertion, or `features.h: No such file or directory` | Before `2026.9.12.4` the **host** toolchain for `build.mcpp` was resolved from a value already overwritten by the target row's pin, and its own C library was not passed along. The exact repro is a fresh project-local `MCPP_HOME` whose first command is a cross build — an existing home hides it |
| Link-time `crtbeginT.o (bare name — the linker cannot resolve it)` | Symptom of **before 2026.8.26.1**: naming a compiler that supplies no C library for that target ran the entire build before dying. It is now rejected early: `error: target 'x86_64-linux-musl' takes its C library from the 'gcc@16.1.0' payload, and 'llvm@22.1.8' has none here.` Fix by adding the `openkal-llvm-runtime` dependency plus `[toolchain] default = "llvm@…"` |
| On a machine with a system gcc, the build **silently** reaches into `/usr/lib/gcc/x86_64-w64-mingw32/…` | Same as above, before 2026.8.26.1 |
| PT_INTERP is x86-64 firmware on a RISC-V build (links fine, reports success) | The llvm payload's `clang++.cfg` contains an **unconditional** `-Wl,--dynamic-linker=…`, which is inherited unless you pass `--no-default-config` [src/build/flags.cppm] |
| `std.pcm` and ordinary TUs disagree on target features | WARNING: `--no-default-config` **itself changes target features** — documented upstream in the spec, **unfixed** |
| The target I want is missing from `mcpp toolchain list` | "**A target absent from this block cannot be built here at all**" [docs/20-toolchains.md; the row table is `docs/21-the-target-triple.md`]. Tier words are `verified` / `preview` / `planned`. WARNING: the row count moves as platforms land (29 at this baseline) — **re-read the table rather than asserting a number**, and note that a host-serving bug used to delete rows on non-Linux hosts, so "unknown target" on macOS was not always the truth |
| `msvc@19.44` errors out | The MSVC toolset version is **the directory name, not the cl banner**: `14.44.35207`. The `19.x` spelling is now an error (it used to mean "verify the banner", which `mcpp toolchain default` checked while **the build silently ignored it**) [docs/20-toolchains.md] |
| `LNK1104: cannot open file 'kernel32.lib'` only at the very end of the build | An SDK root counts only if it has **both** `Include\<v>\ucrt\corecrt.h` **and** `Lib\<v>\um\<arch>\kernel32.lib`; otherwise a partially extracted payload drags on to the end [docs/20-toolchains.md] |
| `import std;` is rejected on a bare-metal target | Rejected at configure time: "a freestanding target has no hosted standard library". WARNING: **but `import std` does work on bare metal when a package in the graph supplies a hosted standard library** — the two chapters describe different systems and must never be conflated [docs/40-baremetal.md vs docs/24-openkal-cross.md]. Exceptions and RTTI are available on the same condition, so the older blanket limitation is withdrawn |
| A freestanding image boots into nothing after an engine upgrade | Freestanding links enable `--gc-sections` from `2026.9.4.1`, and **nothing references an interrupt vector table**. The board's linker script must `KEEP(*(.vectors))` |
| `command -v` finds the wrong tool during a cross build | "`command -v` answers a question about this machine, not about this build" — what is on PATH is a shim that reports "is not installed in this subos", and the usable copy lives in the project's own environment [docs/30-build-mcpp.md] |
| An installed payload never gains `.mcpp-toolchain.json` | A payload describes itself to the engine in that file (schema 1: `frontend`, `platform_floor`, `std_module_defines`, `runner`). An **already-installed** payload only gains it via `index update` + `toolchain remove` + `install` — reinstalling alone does not |
| A host build is suddenly contaminated by openkal dependencies | **openkal dependencies must be target-scoped**: putting them in a plain `[dependencies]` pulls the **host graph** into openkal as well. The correct form is `[target.x86_64-linux-musl.dependencies]` (configure evidence: host graph openkal=0, musl graph openkal=4) [field-tested 2026-08-27] |

WARNING: **`llvm-musl` does not exist in the mcpp source** — a whole-repo grep hits only unimplemented
design documents. The only shipped musl routes are the **payload route (gcc)** and the **graph route
(`openkal-musl` + `openkal-llvm-runtime`)**.

## F. Slow

| Symptom | Root cause | What to do |
|---|---|---|
| `mcpp test` has a long silent stretch every time | **Two distinct causes, both fixed** — re-measure before reasoning. (1) Two post-link ELF passes re-read every image and the memo never hit across processes because `resolution.json` was rewritten fresh each run; fixed in `2026.8.30.2`, records moved to `.mcpp-runtime-verdicts.json`, measured 3.15s -> 0.36s. (2) The dlopen-surface scan ran a full ELF inspection of every linked artifact **before** discovering the surface was empty, and `mcpp test` pays it once per target; fixed in `2026.9.11.3`, measured 17948 ms -> 4 ms on a 108-binary run | **Any "test is an order of magnitude slower than build, that is normal" note predates these.** Re-measure |
| Trying to shorten a gate with `mcpp test <pattern>` | **Filtering saves nothing** — the plan always contains every test, and the filter only selects at build/run time (so that `build.ninja` and `compile_commands.json` stay complete; clangd depends on the latter) | Only `-p` helps. To change *which tests exist*, use `[test] discover` |
| Still no fast path after adding `-p` | **`-p` disables the fast path** [src/cli/cmd_build.cppm:207] | The two are a trade-off, not additive |
| `--workspace` is extremely slow | **Each member runs a full `prepare_build` of its own with zero reuse between members**; the fan-out is **serial** | Split into per-member runs and sum them |
| Every build is slow after adding `--locked` | By design: `--locked` **refuses the fast path**, because otherwise the assertion never runs | Keep it on gate legs only, not on the daily `mcpp build` |
| `--cache local` is 3x slower instead of faster | It **does not touch the global cache at all**; every dependency is compiled from source in this project — that is "what every build looked like before this cache worked" | Use it only for diagnosis |
| Full rebuild after switching mcpp versions | **`MCPP_VERSION` is input 7 of the 11 whole-project fingerprint inputs**, so a new version means a brand-new empty directory | Pin the mcpp version when doing timing comparisons; afterwards reclaim with `mcpp clean --stale` |
| The **global** dependency cache misses wholesale after an upgrade | A key label was renamed (`macos_deployment_target` -> `min_platform_version`, because Android's API level is the same quantity), and the label is part of the hashed string. Old entries are not deleted, just never hit again | `mcpp cache gc`, or the home carries two generations |
| A test leg saturates a machine a build leg does not | `mcpp test`'s test-process concurrency falls back to the **whole machine** unless bounded. `[build] default_jobs` in `$MCPP_HOME/config.toml` bounds both | Set it once per machine; `MCPP_JOBS` still outranks it |
| A `timeout`-wrapped mcpp leaves a ninja spinning on a core | Fixed in `2026.9.4.3`: children go into their own process group (a job object on Windows) and mcpp `SIGKILL`s the group on `SIGINT`/`SIGTERM`/`SIGHUP`. `SIGTERM` alone was not enough — ninja records the signal in a flag it only checks while waiting on a child, so an idle ninja never reaches the check | On an older engine, collect the orphans by hand |
| A whole-project no-op build prints nothing | Including warnings, which target was built and which sources were inferred. Touch a source file and it comes back [docs/30-build-mcpp.md] | — |
| "Why did this edge rebuild?" | Do not compare mtimes | `MCPP_NINJA_DEBUG=explain mcpp build` — ninja says so itself, and it does not raise parallelism |

Note [field-tested 2026-08-29]: when a full run exceeds your runner's foreground limit, the root
`mcpp test` line `workspace result ok` cannot be obtained and per-member totals are the strongest
evidence available. Directions ruled out at the time for that delay: BMI invalidation (a repeat invocation
recompiled **not one line** — a marker experiment showed one run writes 5 json files and 1 ninja file,
zero `.pcm`/`.o`/binaries), `--profile dev` (no difference), and `--cache local` (3x slower). Those
exclusions still hold; what has changed is that both of the causes they were pointing at have been fixed.

## G. Index and dependency resolution

| Symptom | Root cause / what to do |
|---|---|
| `dependency 'asio': no package found`, though it really is in the index | **A bare name can only mean `mcpplibs`.** Write `"chriskohlhoff.asio" = "1.38.1"` or `[dependencies.chriskohlhoff] asio = ...`. WARNING: the did-you-mean scan runs **only on an already-failed path**, and its result **goes only into the error text** |
| `gtest` not found | It must be written `compat.gtest`. WARNING: the bare-name fallback ramp is documented as "removed in 2026.9" but is **still present** on `2026.9.15.2` — deprecated and warned about, not gone |
| A dependency resolves to a different source than you expected, and there is a `dependency/source-override` warning | Two declarations of one identity disagreed. The **root's** declaration wins across kinds when the root is one of the requesters; two non-root declarations of different kinds are still refused, suggesting you declare it in the root to settle it. Before `2026.9.13.x` no field was compared at all and whichever was dequeued first survived. Read `mcpp why deps`: it shows every request with the key as written and the table that declared it |
| The project-local registry is far larger than the packages in it (one measured package directory held **1.6 GB** of *other* packages' downloads) | The bundled xlings before **2026.9.14.1** gave a package with no `install()` the entire download directory instead of its own archive. mcpp `2026.9.15.1` bundles the fixed xlings, but **an already-polluted registry stays polluted**: run read-only `XLINGS_HOME=<registry> xlings self doctor` on any long-lived project-local home, then `--fix` to reinstall the affected package directories. Upgrade-time disk symptom; see `version-notes.md` §4 |
| Two versions of one `xim:` tool are on disk | Before `2026.9.6.6`, two declarations of one tool at different versions installed **both** (multiple GB each) while `xpkg_dir` answered only one, silently. Identity is now `(namespace, name)` with the version always a constraint, and the conflicting case is refused with `tool-version-conflict`. Check a long-lived registry for leftovers |
| `install path missing after fetch` | The version constraint was written as `"0.0"`. **Write `"^0.3.0"`**, not `"0.3"` or `"0.3.x"`. WARNING: this is worse inside `[feature-deps]` — a project developed against a `path` dependency never consults the index, so the failure only appears after publishing, on someone else's machine |
| A just-published `1.3.0` will not resolve | **The index refreshes only when a dependency cannot be resolved locally**, never merely because time passed. `^1.2` resolves against the version set the **local** index already knows |
| It is merged to the index's `main` and consumers still cannot get it | **The index is an artifact, not a git clone**: `publish-artifact.yml` must finish, and clients still have a refresh TTL. **Hand-editing `pkgs/**` in the cache does nothing** |
| `xlings: version 'X' not found for 'mcpp' — available: Y` (listing only one version) | WARNING: **do not conclude from this that "the index dropped it"** — the docs record the same misdiagnosis **twice**. An `available:` list with one version is the shape of an **installed-versions** view, not an index listing. The rule: "**before concluding 'the index dropped it', read the index.**" One `curl` of `pkgs/m/mcpp.lua` settles it [docs/92-release.md] |
| Wanting a local index over `file://` or `http://127.0.0.1` | **mcpp's build sandbox is network-isolated and cannot fetch it** — seeding the cache is the only way. WARNING: **delete the seeded copy before believing the real thing works**; a seeded copy is indistinguishable from a published one as far as the build is concerned, and it survives a silently failed publish |
| A `branch`-style git dependency does not follow tip | **`mcpp.lock` pins it** — the lock is authoritative, not a cache hint. Use `mcpp update <pkg>` to move it |

## H. Sandbox and side effects

| Risk | Trigger | Mitigation |
|---|---|---|
| **Writes into `$MCPP_HOME/registry/data/xpkgs/`** | Tool provisioning for `[xlings.workspace]`, on the build that needs it, **across the whole dependency graph** (not just the root project) | `--offline` / `MCPP_OFFLINE=1` / `MCPP_NO_AUTO_INSTALL=1` all refuse it and name what would have been installed. Still **set `MCPP_HOME="$PWD/.mcpp"`** so it is your disk. Move run-only tools to `when = "run"` so a build-only leg does not pay |
| Installing gcc into a shared home and making it the default | Building an **external project that does not pin a toolchain** under the same `MCPP_HOME` | Give external projects their own home; a project that pins its own toolchain does not consume the default [field-tested 2026-08-29] |
| Building a freshly cloned project runs its shell commands | `[hooks]`. "A hook is code, and `mcpp.toml` is part of the repository." | Read someone else's `mcpp.toml` once before building |
| `mcpp why` / `--configure-only` have write and network side effects | See `../SKILL.md` §1.4 and §3 | Run them only in a trusted workspace |
| `mcpp emit build-database` looks read-only but reaches the network | It declares no `write-project` — that is the point — but it **does** declare `network` and `exec-build-script`, and it plans under `$MCPP_HOME/cache/build-database/<key>` | Read-only with respect to the project, not the machine. Treat it like `build` for sandbox purposes |
| `$MCPP_HOME` grows and no clean command shrinks it | `cache/build-database/` and `cache/tool/` are managed by **neither** `mcpp clean --stale` (which owns `target/<triple>/<fp>/`) nor `mcpp cache gc` (which owns `build-cache/v1`) | Pure caches; delete by hand |
| In-project writes (acceptable) | `.mcpp/.xlings.json`, `target/dist/`, `mcpp.lock` | All under ownerRoot / workRoot |
| A sandbox-only invocation still touched the network | On an engine before `2026.9.5.2`, `--offline` did **not** skip the first-use bootstrap: on an empty home it cloned the index and installed ninja and patchelf first (measured 26 s / 126 MB). It does skip it now, printing one line | This also makes `mcpp self doctor --offline` genuinely safe inside a restricted sandbox |

WARNING: **a runner that kills a foreground command on a timeout skips the `EXIT` trap** — a hidden
mcpp home really is left in its hidden state.
=> Run such scripts in the background with restore bound to `EXIT TERM INT HUP`, and **always check
afterwards** with `ls -d` on the home you hid. [field-tested 2026-08-29]

## I. Cold verification and negative verification, done right

1. **Cold verification must clear the global build cache too**: `rm -rf $MCPP_HOME/build-cache`, so the
   output reads `Compiling <pkg>` rather than `Cached` — only then was anything really compiled.
   [field-tested 2026-08-30]
2. **Negative verification can itself be a no-op** (six distinct causes recorded so far). Before choosing
   a negative assertion, ask whether it would **really** go red once the implementation is deleted. The
   sixth cause is "the build never happened" (see A1).
3. **Deciding that some capability was not compiled in requires actually calling it**, not merely
   asserting that instantiation fails — for example WAMR only warns about unresolved imports rather than
   refusing instantiation, and throws only at **call** time. [field-tested 2026-08-30]
4. **`mcpp test -p <package>` runs that package only** (tens of seconds to a few minutes depending on
   the package), so negative verification does not need a full run.

## J. Quick triage table

| What you see | Check first |
|---|---|
| `Finished ... in 0.00s` | A1 |
| Build green but symbols missing, or a stale generated artifact | A2, A3, A4b, C4 |
| `mcpp test` exits 2 | A5 (built but never run) or a usage error — read stderr, or the JSON's `not_run` |
| `NOT RUN` on a host that could run it | A5b (a declared runner; `--no-runner` is the exit) |
| Configuration looks ignored, or **suddenly stopped being ignored** | B |
| A new schema warning after an upgrade | B, first row — real defect being surfaced, not a regression |
| Compiler crash / wrong header version | C1, C2, C6 |
| Exit 134 with no output | C8 |
| Artifact will not start on another machine, or `dlopen` fails at run time | D |
| Slow | F (but both known causes of the `mcpp test` stall are fixed — re-measure) |
| `no package found` / version will not resolve / an unexpected source won | G |
| Something was written outside the working directory | H |
| Everything recompiles after an upgrade, dependencies included | K1 |
| `mcpp.lock` changed and nobody touched a dependency | K2 |
| `file not found` for a libc/SDK header on an openkal-style target, or a GCC `degraded` warning there | K3 |
| `build/flag-words` warning, or a macro now carries quotes | K4 |
| `program-cxx-runtime-split` / `static-package-in-two-images` / `build/static-placement` / `std::bad_cast` at startup | K5 |
| `interface-not-provided` / `c-env-*` refusal / `undefined reference` with an explanatory note | K6 |
| `offline-download-required` / `MCPP_OFFLINE_DOWNLOAD_REQUIRED`; a refresh "stopped" after two minutes | K7 |
| `compile_commands.json` gone after a no-op build; colour despite `--no-color`; a missing module export not reported | K8 |
| A cross build for `aarch64-macos` ignores the deployment target | K9 |
| Code under `#ifdef __CYGWIN__` / `__openkal__` / `__mcpp_target_*__` stopped being compiled | K10 |
| `'<ns>:' is not a toolchain namespace`, or `'xim:<family>@system' names the ecosystem package and this machine's installation at once` | L1 |
| `<mutex>` / `<memory>` fail inside `pthread.h` with a gcc payload; `mcpp self doctor` warns about `include-fixed` | L2 |
| `[target.<t>].sysroot = '...': on an MSVC-ABI row the sysroot is an MSVC toolset`, or a Windows build picked a different MSVC toolset / SDK than before | L3 |

## K. New in `2026.9.16.1` - `2026.9.21.3`

### K1. The first build after upgrading recompiles every dependency
Cause: the global dependency cache epoch went 2 -> 3 in 2026.9.18.1 [src/build/cache_key.cppm:95] (its key had missed the realised
C environment), on top of the usual whole-project fingerprint change (`MCPP_VERSION` is one of its inputs). Expected once. Afterwards
run `mcpp cache gc` to drop the orphaned generation; old entries are never hit again but are not deleted.
Inferred from source, not measured: since the key folds in the engine's broadcast flags, crossing **2026.9.21.1** (every
target-side unit gained `-D__mcpp_target_<os>__=1`) and **2026.9.21.2** (respelt `__MCPP_TARGET_<OS>__`) should each miss every
dependency entry as well, so an upgrade from 2026.9.18.x-2026.9.20.1 is not a warm one either.

### K2. `mcpp.lock` shows a diff of `hash` lines only
Cause: 2026.9.20.1 made the lock digest FNV-1a on every host; Linux/macOS used to write MurmurHash values under an `fnv1a:` label.
Commit the diff once. `--locked` compares versions, not hashes, so it stays green; each `git` dependency is cloned once more because
its cache directory key (`$MCPP_HOME/git/<hash>`) moved to the same function.

### K3. `file not found` on a target whose C library comes from the graph
Cause: since 2026.9.17.3 a graph-supplied `c-abi` adds `-nostdlibinc` and a graph-supplied `c++-abi` adds `-nostdinc++` (Clang). The
package used to compile because the host had a header the graph does not supply - and the artifact mixed two C libraries'
declarations. How to tell: the failure carries mcpp's advice naming the C library (`name` and `package@version`). Fix: adapt with
`cfg(c-abi = "<lib>")` in the manifest, or bring the platform dependency in through the graph under `[feature-deps.<f>]` with
`visibility = "private"`. **Do not** try to re-open the host include path. With GCC the command line is unchanged; you get a
`degraded` warning instead, which `--strict` turns into an error - Clang is the family that can isolate.

### K4. `build/flag-words` warning, or a define now contains quotes
Cause: 2026.9.17.1 reads each `cflags`/`cxxflags`/`asmflags` element with one fixed word syntax (SPEC-004 §8) and treats a `defines`
entry as one value. The warning appears on the first plan and names the old and new readings. Typical cases: a hand-escaped
`"-DNAME=\\\"x\\\""` (now a real string literal - check the generated code), `-I` paths with backslashes (now preserved), a `$` that
used to be expanded by the host shell (now literal). `compile_commands.json` lists the new words exactly.

### K5. C++ runtime and static-placement refusals
- `program-cxx-runtime-split`: an ELF program or test that **states** `cxx_runtime = "self-contained"` loads a C++ shared library of
  this build coupled to a shared runtime. Remove the statement, or give the library `cxx_runtime = { shared = "self-contained" }`.
  (Unstated programs now take the library's contract automatically - that is what fixed the `std::bad_cast`, exit 134, upstream measured
  with llvm.)
- `static-package-in-two-images` (Mach-O, PE, Android `app`) / `build/static-placement` warning (other ELF, error under `--strict`): a
  static package is reached by more than one image. Give it `linkage = "shared"` on the root's edge or as its own default.
- `build/cxx-runtime-identity` (macOS, informational): exceptions and `std::error_code` categories do not match across dylibs under the
  default per-image `libc++.a`; state `cxx_runtime = "host-coupled"` for every role if objects cross that boundary.

### K6. Refusals from the target-side declarations
- `interface-not-provided`: a package's `[kernel-abi] requires-interfaces` names something the resolved implementation's
  `provides-interfaces` lacks. The message names all three parties; pick another implementation or drop the requirement.
- `c-env-unrealisable` / `c-env-verification-mismatch`: the C library's `[c-abi]` cannot be realised for this target/compiler, or the
  `-E -dM` probe disagrees with it (declared and measured columns are printed). Before 2026.9.20.1 the probe measured the **host** on
  freestanding targets, so a mismatch reported by an older engine on a Windows host may be spurious; upgrade before debugging it.
- An `undefined reference to 'fork'` followed by a sentence explaining it: the C library's `[c-abi-absent]` table names that function
  as intentionally absent. The program needs a different facility on this target, not a missing library.
- `platform-dependency`: `[build] platform-dependencies = "refuse"` and some package declares `provides = ["platform-sdk"]`; the
  `Target` report's `platform-deps` line names it.

### K7. Offline and bounded network
- `MCPP_OFFLINE_DOWNLOAD_REQUIRED` / `offline-download-required`: the plan needs a toolchain, package, git revision or the index. One
  online run fixes it; it is not a project defect.
- A warning naming `[index] refresh_timeout`: a refresh exceeded its bound (default 120 s) and the build continued on the local index.
  Raise the value in the home's `config.toml` on a slow link rather than disabling refresh.
- An install aborted after five silent minutes: the xlings child printed nothing, not even a heartbeat, for 300 s.
- A project with a custom index that stops and asks for `mcpp index update`: `[index] auto_refresh = false` now also forbids its first
  implicit sync (2026.9.16.1).

### K8. Three long-standing defects still open at 2026.9.21.3 (upstream triage mcpp#677)
- **`compile_commands.json` is missing after `mcpp build` printed `Finished dev in 0.00s`**: the database is written only by the ninja
  backend, which a fast-path hit never enters. `git clean -fd` removes it (the default `.gitignore` does not cover it). Recover with
  `mcpp emit build-database --spec compile-commands -o compile_commands.json` or by touching a source.
- **Colour escapes despite `--no-color`** on a terminal: the flag is lost on first output. Use `NO_COLOR=1` (any value) or
  `MCPP_NO_COLOR=1`.
- **A module missing from `[modules].exports` is not reported** when the package has a `namespace`: the check compares qualified
  against bare names and sees an empty set. The consumer's "module not found" is the first signal.

### K9. `aarch64-macos` from a Linux or Windows host was always `minos 14.0` (before 2026.9.24.1)
Engines before 2026.9.24.1 (mcpp#685): the deployment target was resolved only on an Apple host; elsewhere both
`MACOSX_DEPLOYMENT_TARGET` and `[build] macos_deployment_target` were discarded and changing them did not rebuild. From 2026.9.24.1
the value is resolved on every host and applied whenever the target is macOS. If an artifact still reads `minos 14.0`, check the
engine version first, then whether `MACOSX_DEPLOYMENT_TARGET` is set in the build environment (it outranks the manifest). Read
`LC_BUILD_VERSION` with `llvm-objdump --macho --private-headers`.

### K10. Macro-guarded code silently switched branches
- `__openkal__` -> `__OPENKAL__` and `__mcpp_target_<os>__` -> `__MCPP_TARGET_<OS>__` in 2026.9.21.2 (no alias). A `#ifdef` on the
  lower-case name is now always false.
- `__CYGWIN__` / `__CYGWIN32__` are undefined for Windows graphs whose C library presents POSIX (2026.9.21.2). Test
  `__MCPP_TARGET_WINDOWS__` instead. An installed header that still reads only `__CYGWIN__` falls into its `#else` with no error -
  for openkal-musl that is `bits/setjmp.h` below 0.19.0 (wrong `jmp_buf` size on Windows targets), so do not pin it exactly to an
  older version on these engines.

## L. New in `2026.9.24.1`

Citations in this section are `@ b4824697`.

### L1. A toolchain spelling is refused for its prefix
`'<ns>:' is not a toolchain namespace; the one namespace a toolchain spelling accepts is xim: ...`: some manifest key, `--toolchain`,
`MCPP_TOOLCHAIN` or a `mcpp toolchain` argument writes a prefix other than `xim:` [src/toolchain/registry.cppm:539-550]. Older
engines dropped any prefix silently, so the spelling may have worked for a long time. Delete the prefix, or write `xim:`. The
message is prefixed by where prepare read the value, which is the place to edit.
`'xim:<family>@system' names the ecosystem package and this machine's installation at once` [:574-581]: pick one - `msvc@system` for
the machine's Visual Studio, `xim:<family>@<version>` for a payload. (`gcc@system` / `llvm@system` stay refused for their own reason,
§E.)

### L2. `<mutex>` or `<memory>` fails inside `pthread.h` with a gcc payload
Cause: the gcc 13.3.0, 15.1.0 and 11.5.0 `x86_64-linux-gnu` payloads were published with fixincludes copies of the build machine's
glibc headers in `lib/gcc/<triple>/<version>/include-fixed/`. mcpp puts the C library after them (`-idirafter`), so a frozen
`pthread.h` from an older glibc wins over the glibc 2.44 the build resolves [CHANGELOG.md:72-82]. How to tell: `mcpp self doctor`
prints a warning under `Checking gcc include-fixed headers` naming the files and the frozen source path
[src/doctor.cppm:618-691]. Fix: `mcpp index update`, then `mcpp toolchain remove gcc@<v>` and `mcpp toolchain install gcc@<v>`
(add `--target <t>` for a cross payload). The index recipe now removes those files at install (openxlings/xim-pkgindex#870), but an
index update alone does not re-run the install of a payload already on disk. Upstream's impact notes measured 13.3.0 and 15.1.0 as
affected, the musl-gcc 13.3.0 / 15.1.0 / 16.1.0 payloads clean and the llvm payloads free of build-machine paths; gcc 11.5.0 and
9.4.0 were not measured there [.agents/docs/2026-09-24-685-687-msvc-stl-and-toolchain-payloads.md:163-167] (the CHANGELOG
and SPEC-006 §4.2 list 11.5.0 as affected all the same); run the doctor check rather than assuming either is clean.

### L3. MSVC toolset selection (Windows)
- `[target.<t>].sysroot = '...': on an MSVC-ABI row the sysroot is an MSVC toolset, written "msvc@system", "msvc@<toolset>" ... or
  "xim:msvc@<toolset>"` [modules/manifest/src/toml.cppm:676-701]: on `*-windows-msvc` the key no longer takes a C library package or
  `""`. Use one of the three spellings, or delete the key (`msvc@system` is the default).
- `... is not an xpkg reference` for `sysroot = "msvc@..."` on a *non*-MSVC row, or from an engine older than 2026.9.24.1 on an MSVC row:
  the msvc spellings exist only on MSVC-ABI rows and only from 2026.9.24.1.
- `... matches no toolset on this machine, and the package could not be provided`: a pinned toolset is neither installed nor
  installable; the message lists the installed ones, and `mcpp toolchain list --available msvc` lists the packages
  [src/build/prepare.cppm:1455-1474].
- `... names a different toolset than the compiler (...). With cl.exe the compiler is its own sysroot`: on the cl.exe row, pin the
  toolset in `[toolchain]` (`msvc@<toolset>`) and drop `sysroot`, or build with clang [src/build/prepare.cppm:1542-1563].
- A build now uses a different toolset or SDK than before: `msvc@<toolset>` prefers an installed toolset of that version with the
  machine's SDK (write `xim:msvc@<toolset>` for the payload and its pinned SDK), and `msvc@system` honours `VCToolsInstallDir` and the
  instance's default toolset. `note:` lines name ignored variables and skipped incomplete toolsets; on the clang row the
  `Resolved sysroot ...` line and `resolution.json` `msvc_toolset` / `windows_sdk` say what was used.
- `import std` became unavailable with a cl.exe toolset: that toolset has no `modules\std.ixx`, and another toolset's is no longer
  borrowed [src/toolchain/msvc.cppm:1516-1526]. Pin a toolset that ships `modules\std.ixx`; `mcpp toolchain list` shows the
  installed ones.
