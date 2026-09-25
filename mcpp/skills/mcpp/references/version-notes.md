# Reference: version history and upgrade notes

> Baseline: mcpp source `main @ b4824697` (version **2026.9.24.1**, tag `v2026.9.24.1`), dated 2026-09-24, verified against
> source and docs only (the diff `b30e70c4..b4824697`, the English docs and `docs/specs/toolchain-management.md`); no release
> binary was run. Previous baselines of this skill: `2026.9.21.3` @ `b30e70c4` (2026-09-23, source and docs only), `2026.9.15.2` @
> `2fc7b5b0` (2026-09-16, cross-checked on its release binary) and `2026.8.30.2` @ `aef5191`.
> The first-release-containing-it for every commit named below was taken from `git tag --contains`, not from the CHANGELOG.

## 0. One sentence

**`2026.9.24.1` is one release on top of `2026.9.21.3`: it makes the MSVC toolset the sysroot of a clang `*-windows-msvc` row,
lets `msvc@<toolset>` use an installed toolset, decides `macos_deployment_target` by target instead of host, teaches `mcpp self
doctor` to find frozen fixincludes headers in gcc payloads, and refuses toolchain namespaces other than `xim:`; the CLI is
unchanged.**

**Between `2026.9.15.2` and `2026.9.21.3` mcpp shipped twelve releases (`2026.9.16.1`, `.16.2`, `.17.1`-`.17.3`,
`.18.1`-`.18.3`, `.20.1`, `.21.1`-`.21.3`); the command word list did not change, but a C-environment layer, a graph
document for build programs, `test --no-run`, `pack --message-format json` and bounded offline-aware planning arrived, and
three changes (cache epoch, lock hash, host-header isolation) are visible on the first build after upgrading.**

Earlier window, kept for readers of older manifests: **between `2026.8.30.2` and `2026.9.15.2` mcpp shipped roughly
thirty-five releases, and the CLI grew for the first time in a while.** Nothing was removed or renamed at the CLI level: the top-level word list is the same 28, and every
option that existed still exists. What is new is `emit sbom` / `emit build-database`, a global `--locked`, `clean`'s
stale mode, an accelerator axis, named runners, and `--toolchain` / `--features` landing on the commands that build
before they act. Underneath, the manifest grew a target-side ABI axis, per-package link-form defaults and a `[test]`
section, and the entire `docs/` tree was renumbered.

## 1. The `docs/` renumbering (do this mapping first)

`docs/` moved from a flat `00`-`17` list to bands, and `docs/spec/` became `docs/specs/`. **The two halves landed at different
times, and neither is 2026.9.4.** The renumbering is one commit, `9a71c9a6` ("docs: three trees, three audiences", #590,
2026-09-08), first contained in **`v2026.9.9.1`** - so **every** citation written against 2026.9.4 through 2026.9.8.1 uses the old
flat numbering and is a dead link in today's tree. (Those paths were correct in the tree their document was written against; that
makes them historically accurate, not usable.) The `docs/spec/` -> `docs/specs/` rename is `91ab128e` (2026-09-07), first contained
in **`v2026.9.6.4`** - that half really does leave 2026.9.6.4-and-later `docs/specs/` citations alone.
Every pre-**2026.9.9.1** citation of the form `docs/NN-name.md` is a dead link, and a few resolve to a **different, real** document — `docs/11` used to
be machine output and is now publishing-a-library, which is worse than a 404. Map before you cite:

| old | new |
|---|---|
| `00-getting-started` | `01-getting-started` |
| `01-examples` | `03-examples` |
| `02-pack-and-release` | `10-pack-and-release` |
| `03-toolchains` | `20-toolchains` |
| `04-build-from-source` | `90-build-from-source` |
| `05-mcpp-toml` | **split**: `04-mcpp-toml` + `05-dependencies` (+ `06-features-and-capabilities`, `08-testing`) |
| `06-workspace` | `07-workspace` |
| `07-build-mcpp` | `30-build-mcpp` |
| `08-toolchain-internals` | `91-toolchain-internals` |
| `09-release` | `92-release` |
| `10-publishing-a-library` | `11-publishing-a-library` |
| `11-machine-output` | `50-machine-output` |
| `12-binary-distribution` | unchanged |
| `13-baremetal` | `40-baremetal` |
| `14-target-side` | `22-target-side` |
| `15-openkal-cross` | `24-openkal-cross` |
| `16-the-target-triple` | `21-the-target-triple` |
| `17-the-project-environment` | `23-the-project-environment` |
| `18-devices` † | `41-devices` |
| `19-supported-versions` † | `51-supported-versions` |
| `20-heterogeneous-builds` † | `42-heterogeneous-builds` |
| `21-commands-by-scenario` † | `09-commands-by-scenario` (rewritten, not renamed: the old 211-line page was deleted and a 417-line one added in the same commit) |
| `docs/spec/` | `docs/specs/` |

† These four are **late** pre-renumbering pages, which is why the 2026.8.30.2-based half of this map does not carry them: none of the
four exists before `2026.9.4.2`, and all four are present from `2026.9.6.1` through `2026.9.8.1`. A citation naming one of them was
written against a tree in that window, and it does map - do not read "no predecessor" and conclude nothing does.

New pages with no predecessor: `00-what-mcpp-is`, `02-scenarios`, `05-dependencies`, `06-features-and-capabilities`,
`08-testing`, `31`–`34-authoring-*`. New specs: `docs/specs/exit-codes.md` (SPEC-003), `manifest-semantics.md` (SPEC-004),
`build-database.md` (SPEC-005), and `toolchain-management.md` (SPEC-006, draft v0.2, 2026.9.24.1).

**`docs/zh/` was renumbered in the same commit, so the table above is the mapping for BOTH trees.** There is no separate
Chinese numbering axis: `docs/zh/` mirrors the English tree file for file, same band numbers, same basenames (verified:
`ls docs/*.md` and `ls docs/zh/*.md` differ in nothing at `main @ 2fc7b5b0`; `docs/zh/` carries no `specs/` subtree - the specs
exist once, under `docs/specs/`, and are written in Chinese, SPEC-006 included). So a `docs/zh/NN-name.md` path written before **2026.9.9.1** is dead exactly as its English twin is, and it is
mapped by the same rows:

| a zh path you will be handed | today |
|---|---|
| `docs/zh/13-baremetal.md` | `docs/zh/40-baremetal.md` |
| `docs/zh/20-heterogeneous-builds.md` | `docs/zh/42-heterogeneous-builds.md` |
| `docs/zh/18-devices.md` | `docs/zh/41-devices.md` |
| `docs/zh/14-target-side.md` | `docs/zh/22-target-side.md` |

Both of the first two **return 404 on `main`** (GitHub contents API, 2026-09-16), and both are still live in upstream
conversation — `mcpp#403`'s maintainer comment links `docs/zh/13-baremetal.md`. Map before following such a link, and cite the
English page per the standing rule in §7.
Two pages worth knowing by name: **`docs/09-commands-by-scenario.md`** is upstream's "which command for this
situation" lookup, and **`docs/README.md`** now carries a "Look it up" reverse index from a manifest key, a command or
a concept to its chapter. Prefer aligning with those over inventing a parallel index.

## 2. Version history, `2026.9.1.1` to `2026.9.24.1`

Read this when something is new and you want the spelling to type. Each entry names the version that introduced the
behaviour; `changed in <ver>` marks a case where the **old** behaviour was different rather than absent.

Two sourcing warnings before you go looking for more detail:
- **The GitHub Releases page is not a source.** Twelve of the releases in this window (`2026.9.6.3`–`.5`, `2026.9.12.3`,
  `2026.9.12.4`, `2026.9.13.1`, `2026.9.13.2`, `2026.9.14.1`–`.3`, `2026.9.15.1`, `2026.9.15.2`) publish with no
  release notes at all; their content lives only in the merged pull request and in `CHANGELOG.md`.
- **The CHANGELOG has blind spots**, historically and still. Several versions ship capabilities with no entry, and
  releases are not always under their own `##` heading: at `2026.9.21.3` the file has `## [2026.9.21.3]` .. `## [2026.9.18.1]`,
  but everything from `2026.9.12.3` through `2026.9.17.3` is `###` subsections **inside** the `## [2026.9.18.1]` section. To
  decide whether a capability is in a given version, read `git tag --contains <commit>` and the source. The CHANGELOG body is
  written in Chinese; the English docs are the citable text.
- Since `2026.9.18.2` the release workflow **refuses to publish a version whose CHANGELOG has no `## [<version>]` heading**
  (`6bb2ffd9`, #670) instead of shipping the placeholder "(no CHANGELOG entry found for …)" - which is exactly what
  `v2026.9.18.1`'s release page says. From `2026.9.18.2` on, the Releases page body is the CHANGELOG section; before it, the
  warning above stands.

### 2026.9.1.1
- **`[target.'cfg(<layer> = "…")'.build]` works.** The five layer names `compiler` / `compiler-runtime` / `kernel-abi`
  / `c-abi` / `c++-abi` became predicate keys, combinable with triple keys under `all`/`any`/`not`.
  *changed in 2026.9.1.1:* such sections were previously parsed and **silently dropped**, so a package could build
  successfully against the wrong C library. A layer predicate still cannot select dependencies; that is reported and
  ignored.
  ```toml
  [target.'cfg(c-abi = "musl")'.build]
  defines = ["USE_MUSL"]
  ```
- *changed in 2026.9.1.1:* the `c-abi` layer reports the **library name** (`glibc`, `musl`, …) rather than the triple's
  env segment, so machine output's `layers[].interface` changed value on gnu rows and on Windows.
- *changed in 2026.9.1.1:* an unknown `cfg` key is now **reported**. It used to evaluate to false, which reads exactly
  like "this section correctly did not match".
- `[build] std-module` / `std-compat-module` / `std-module-flags` stopped being reported as unsupported keys while
  working, and `std-module-flags` / `private_include_dirs` became conditionable.
- `[features]` got an unknown-key sweep — it was the last structured section with none.
- `[xlings] deps` provisioning learned to notice its own failures, to honour `MCPP_OFFLINE` / `MCPP_NO_AUTO_INSTALL`,
  and to key its idempotency stamp by the dependency list inside the registry instead of a project-local file.
- SPEC-003 (`docs/specs/exit-codes.md`) wrote the exit-code classes down as a contract.
- `mcpp build --help` / `test --help` stopped claiming the default profile is release.

### 2026.9.2.1
- **`[target.<triple>].runner` is honoured on hosted cross targets**, not only freestanding ones, and the runner
  program is located in the declared payloads' `bin/` first, then `PATH`.
  *changed in 2026.9.2.1:* a declared runner used to be ignored on such rows, so `mcpp run` executed the artifact bare
  and a kernel `ENOEXEC` became a silent `127`. It is now an error when the runner program is missing.
  ```toml
  [target.aarch64-linux-musl]
  runner = ["qemu-aarch64"]        # a program name, not a path
  ```
- **`--no-runner` on `run` and `test`** — the escape hatch for a host that executes the artifact natively.
- **`mcpp test` gained a fourth state, `NOT RUN`, and exit code 2.** `0` = every test ran and passed, `1` = a test ran
  and failed, `2` = built and never run. JSON gained `status: "not_run"` and `reason`; the summary gained `not_run` /
  `not_run_reason`; `--workspace` gained `tests_not_run` and `unrunnable_members`.
  *changed in 2026.9.2.1:* such tests were reported as `FAIL (exit 127)`.
- `[xlings]` values may be given per host platform; `[target.<triple>]` unknown-key sweeping covers array keys.

### 2026.9.3.1 / 2026.9.3.2
- **`[xlings.workspace]` is the one table.** An entry yields both an install address and a resolution pin. The
  recommended spelling puts the namespace on the key, which therefore needs quotes.
  ```toml
  [xlings.workspace]
  "xim:picolibc-riscv" = "1.8.12"
  "xim:qemu-user"      = { linux = "9.2.4", default = "" }   # "" = present, any version
  ```
  *changed in 2026.9.3.1:* `[xlings] deps` still works but warns (an error under `--strict`), naming one package in
  both tables at different versions is a hard error, and **`[xlings.envs]` went from ignored to a hard error**.
- `mcpp emit xpkg` started emitting the install-time edge `xpm.<platform>.deps` from the unresolved declaration.

### 2026.9.4.1
- The bare-metal target table grew to eleven rows (seven M-profile rows, because an object built for `thumbv7em` uses
  instructions a Cortex-M0 does not have).
- *changed in 2026.9.4.1:* freestanding links enable `--gc-sections`, so **a board's linker script must `KEEP` its
  vector table** (`KEEP(*(.vectors))`) — nothing references it, so it is collected.
- Exceptions, RTTI and `import std` are available on bare metal when a package in the graph supplies a hosted standard
  library; the older blanket limitation is withdrawn.

### 2026.9.4.2 (a large one)
- **`mcpp emit sbom`** — CycloneDX 1.5 read straight out of `mcpp.lock`. It resolves nothing, builds nothing and makes
  no network request, so it is safe in a sandbox and safe as a non-blocking gate step. Its honesty is exactly the
  lock's: pair it with `--locked`.
  ```
  mcpp emit sbom -o sbom.cdx.json
  ```
- **`--locked` / `--frozen` / `MCPP_LOCKED=1`** turned the lock into an assertion, and deliberately refuses the fast
  path so the assertion actually runs.
  *changed in 2026.9.4.2:* the lock was written after resolution and never read back.
- **Named runners**: `mcpp run --runner <name>`, `mcpp run --list-runners`, `mcpp why runners`. The engine knows no
  runner names; packages supply them with `mcpp::runner("<name>", …)`. Write a **program name, not a path**.
  `mcpp::runner_longlived(name)` declares whether it terminates; `mcpp::run_exclusive()` declares that runs of a target
  cannot overlap, and `mcpp test` serialises them.
- **`mcpp run` takes `--features` / `--profile` / `--release` / `--dev`.**
  *changed in 2026.9.4.2:* `run` could only execute whatever the last `build` happened to leave behind.
- **`when = "build" | "run" | "dev"` on `[xlings.workspace]` entries**, and provisioning extended to the whole graph.
  Omitting `when` is exactly the old behaviour, so nothing has to migrate.
  ```toml
  [xlings.workspace]
  "xim:qemu-arm"  = "9.2.4-1"                              # every build, as before
  "xim:probe-rs"  = { version = "0.24.0", when = "run" }   # only run/test; propagates
  "xim:clang-tidy" = { version = "20", when = "dev" }      # only as root; does not propagate
  ```
- *fix:* the build-cache entry records the **feature set**, so `build --features loud` followed by a plain `build` no
  longer replays the feature build in 0.00s.

### 2026.9.4.3
- **`mcpp run` passes the program's own exit code through**: `0`–`124` verbatim, `125`–`127` = the spawn was attempted
  and refused (`127` not found / `126` not executable / `125` other), `2` = mcpp refused before attempting anything.
  *changed in 2026.9.4.3:* every non-zero status was folded to `1`. `mcpp test` is unaffected.
- *fix:* build subprocesses enter their own process group and the group is `SIGKILL`ed when mcpp is signalled — a
  `timeout`-wrapped mcpp used to leak a spinning ninja per timeout.
- **`MCPP_NINJA_DEBUG=explain`** appends `-d <topics>` to ninja. The direct way to ask "why did this edge rebuild".

### 2026.9.5.1 – 2026.9.5.4 (the accelerator batch, plus two fast-path fixes)
- **`[build] accel`, `--accel <SPEC>`, `--no-accel`, `[package] accelerators`.** `--no-accel` is an explicit request
  for *no* accelerator, not merely the absence of `--accel`. Device sources (`.cu`, `.hip`, shader stages, …) are never
  scanned for imports and never produce a BMI, and device extensions are deliberately **not** in the default source
  glob.
  Separator rule worth memorising: a comma separates entries in the set, a space separates modifiers **within** one
  entry — `"cuda12.9+{sm_89}, vulkan1.2"` selects both; with a space only, only cuda.
- A `sources` entry may carry its own constraint, which also makes a CPU-only variant expressible:
  ```toml
  [build]
  sources = ["src/*.cppm", { glob = "src/kernels/**/*.cu", accel = "cuda12.9+{sm_89}" }]
  ```
  A constraint matching no file is **refused by name** — an empty match is a typo, not a no-op.
- **`--accel` / `--no-accel` on `run` and `test`**; giving either bypasses that command's fast path.
- **`[[runtime.requirements]] kind = "version-floor"`** plus `mcpp::fact` / `mcpp::floor` (protocol v7): a build program
  states the machine fact it measured and the floor it needs, and the engine compares, refusing with both values
  (`version-floor-unmet`). No vendor name appears in the engine.
  ```toml
  [[runtime.requirements]]
  kind  = "version-floor"
  value = "cuda.driver >= 12.0"
  ```
  *removed in 2026.9.5.2:* `mcpp self doctor`'s device section and `mcpp.toolchain.devicehost` — the same readings now
  come from rule packages. Delete any note that says doctor reports device state.
- **`MCPP_TOOLCHAIN_SYSROOT` / `MCPP_TOOLCHAIN_BINUTILS_DIR`** state the `--sysroot` and `-B` mcpp hands its own
  compiler — required by any action that drives a second compiler mcpp did not resolve.
- *fix:* `--offline` skips the first-use sandbox bootstrap. On an empty home, measured 26 s / 126 MB -> 0.3 s. It now
  really is offline, which also means it fails rather than quietly installing.
- *fix (2026.9.5.3):* a variant switch is no longer replayed by the fast path; `build.ninja`'s header line records
  `accel=default|override`.
- *fix (2026.9.5.4):* the fast path compares the build program's **declared** inputs — glob path sets, the content hash
  of declared files, and declared environment values. Changing a data file named by `rerun_if_changed` used to produce
  `Finished dev in 0.00s` and the previous bytes.
- The device-extension table grew to 18 (CUDA, HIP, GLSL stages, HLSL, OpenCL C, Metal), later `.sycl`. **Do not work from this
  count** - the complete, current list (and the "an extension outside this table is refused by name" rule) is the table at
  **[docs/42-heterogeneous-builds.md:101-112]**, which has since gained Ascend C `.asc`/`.cce`. Official build
  plugins consolidated into one package `mcpp:plugins`, with the naming convention `mcpp.rules.<x>` /
  `mcpp.tools.<x>`. **`MCPP_DEVICE_SOURCES` is newline-separated.**

### 2026.9.6.1 – 2026.9.6.6
- **`mcpp clean --stale` / `--dry-run` / `--older-than <DUR>`.** See `../SKILL.md` §8 for the three rules that matter.
  ```
  mcpp clean --stale --dry-run
  mcpp clean --stale
  mcpp clean --older-than 3d      # implies --stale
  ```
- **`mcpp search` shows published versions; `--all-versions` shows all of them.** Latest 3 by default, truncation
  marked `, ...`; `mcpp add`'s did-you-mean suggestions carry versions too. WARNING: the versions come from the
  **local** index copy, so they are as fresh as the last refresh.
- **`[target.<sel>.xlings.workspace]` and `[target.<sel>.feature-xlings.<f>]`** — the target resolution axis for tools.
  Decision test: *does the produced code compile or link against it?* Then target axis. Does it merely execute on the
  build machine? Host axis. On a native build the two name the same platform, which is why a project on the wrong axis
  is right by accident until it cross-compiles.
- **One package, one version.** A tool's identity is `(namespace, name)`; the version is always a constraint. Which
  version installs is decided in two steps: **adjudication** (the declaration closer to the artifact wins — project
  over dependency; a version-less declaration abstains; the outcome is reported) then **validation** (the winner must
  satisfy every losing *requirement* `>=` / `^` / `~` / comma combinations, else the build is refused naming both sides
  and the way out, `tool-version-conflict`). A bare version is a *selection*, not a requirement, so two exact pins go
  to adjudication rather than refusal. This is one comparison, not a search: there is no constraint solver.
  *changed in 2026.9.6.6:* two declarations of one tool at different versions used to install **both** (multiple GB
  each) while `xpkg_dir` answered only one. Check a long-lived registry for duplicate versions of one `xim:` package.
- `mcpp::xpkg_dir` answers range expressions; `mcpp::cxx_stdlib()` / `MCPP_CXX_STDLIB` tell a build program which
  standard library (`libstdc++` / `libc++` / `msvc-stl`) — `compiler()` cannot answer that.
- `[targets.<n>] exports` restricts a shared library's published symbol set (a pattern file or an inline array,
  rendered per platform as a version script / `-exported_symbols_list` / `.def`). It is a link-time property only.
- `mcpp:link-flag=` / `mcpp::link_flag()` (protocol v8) passes a computed link flag through verbatim. It reaches
  consumers, like `[build] ldflags`.
- `cfg(accelerator = "none")` — true exactly when the accelerator set is empty, so a CPU fallback need not be written
  as `not(any(...))` over an open vocabulary.
- Rule packages belong in **`[build-dependencies]`**: the section says whether the package itself reaches the target,
  the edge's request (`tools = [...]`, `host-module = true`) says which build-time product you want. Writing one in
  `[dependencies]` also works, which is exactly why the distinction has to be stated.

### 2026.9.7.1
- **`mcpp::action` gained `depfile`.** Without it, a command that discovers its inputs by reading source produces no
  rebuild when one of those files changes, and `mcpp build` stays green on a stale artifact.
  WARNING: do not also declare the depfile as an `output()` — `deps = gcc` makes ninja consume and delete it, so the
  edge is dirty for ever.
- **A rule package declares its own device language**: `[features.<f>] device_extensions` + `rule_module`, which must
  appear together. `rule_module` implies `host-module = true`. The engine holds no package name, feature spelling or
  module name — the criterion is that `.slang` was removed from the built-in table while its consumer still builds.
  ```toml
  [features.rules-slang]
  sources           = ["rules/slang.cppm"]
  device_extensions = [".slang"]
  rule_module       = "mcpp.rules.slang"
  ```
- A project that declares `[rules]` **need not write a `build.mcpp`**; mcpp synthesises one into the build directory
  and stops as soon as you copy it to the project root.
- `MCPP_LANGUAGE_MODULES`, `MCPP_PKG_NAME`, `MCPP_PKG_NAMESPACE`. => Stop deriving a package name from the last
  segment of `MCPP_MANIFEST_DIR`; that is a directory name and they differ whenever packages sit under a shared
  directory.
- Documented limitations: on macOS 14 a build program cannot use `std::print`/`std::println` (use `std::format`, which
  is header-only), and **dependencies cannot be conditioned on a layer predicate**.

### 2026.9.8.1 / 2026.9.9.1
- *fix:* a package's host modules compile in **import topological order**; previously path order, so a rule unit could
  be compiled before the unit it imports.
- *fix:* `device_extensions` / `rule_module` stopped being reported as unsupported keys — a message that told package
  authors to delete the two lines that make their rules work.
- *withdrawn:* `mcpp::recompile_if_changed` (a protocol-9 draft). Express that dependency with an `mcpp::action` whose
  declared inputs include the payload. Protocol 9 was later taken by `mcpp:pack-format=`.
- *fix:* **`module : private;` is accepted again** — a regression that shipped in `v2026.8.18.1` and persisted through
  `2026.9.8.1` rejected it at scan time.
- *fix:* source files **and `mcpp.toml`** are read as UTF-8 with the BOM consumed. Diagnostic worth memorising: on an
  older engine, `1:1: error: expected key` on a manifest is almost always a UTF-8 BOM.
- *fix:* a file with a module extension need not provide a module — implementation units are legal `.cppm` residents.
  The same project used to build under GCC and fail under clang.
- *fix:* a conditional block containing **only** `[target.<pred>.runtime]` is no longer dropped. If you added an
  unrelated `defines` line to make such a block take effect, delete it — it now enters the fingerprint for nothing.
- `[runtime]` and `[target.<pred>.runtime]` report unknown keys.

### 2026.9.10.1 / 2026.9.10.2
- **The dlopen surface is walked separately and published** in `resolution.json` under `runtime.dlopen_surface`, with
  three readings: resolved (silent), present in the farm but dangling (silent — the machine has no driver), nowhere at
  all (warning — a packaging gap). Two denominators, `members` / `walked`.
  ```
  jq '.runtime.dlopen_surface' target/<triple>/<fp>/resolution.json
  ```
- *fix:* when a second C++ runtime lands on the link line, only one unwinder survives the process. The symptom it fixes
  is exit code **134 with nothing printed** — one throw handled by two unwinders. Builds with no second runtime on the
  link line are byte-identical.
- *fix:* duplicate-symbol checking splits by symbol binding, so vague-linkage definitions stop counting as a second
  provider, and the count is printed — otherwise "clean" reads the same as "did not look".
- *fix (2026.9.10.2):* the inapplicable passes of the dlopen check publish a record with a reason instead of being
  indistinguishable from "never checked", and do not overwrite a real reading.

### 2026.9.11.1
- **`mcpp pack --format <name>` dispatches to a package.** `tar` and `dir` are engine-owned; every other name is looked
  up among the packages in the resolved graph (`mcpp::provides_pack_format("<name>")`). An unknown value names the
  formats **actually available in this build**, and the refusal happens before anything is compiled.
  *changed in 2026.9.11.1:* `--format` was the closed set `tar|dir`, validated in the CLI.
  Authoring rule that is easy to get wrong: **declare unconditionally, submit conditionally** — an author who always
  passes their own format never notices a gated declaration.
  WARNING for cost: `pack --format` runs `prepare` **twice**.
- `${mcpp.stage_dir}` exposes the bundle tree pack always computed (`bin/`, `lib/`, relocatable). It is a **refusal**
  rather than an empty expansion outside the `artifact` role or outside a packing build, and an action naming it gains
  a dependency on the sibling `.stage-manifest`.
- The rest of `[package]` reaches build programs: `MCPP_PKG_VERSION` / `_DESCRIPTION` / `_LICENSE` / `_AUTHORS` /
  `_REPO` and `mcpp::package_*()`. Protocol -> v9.
- `build.ninja`'s header line gained a fourth field `dist=`; the fast path requires it to read `none`.

### 2026.9.11.2
- **`[build] default_jobs` finally has a reader**, and it is the only rung that can carry a machine fact:
  `MCPP_JOBS` > `[build] jobs` (per package) > `[build] default_jobs` (per machine) > 0. **It also bounds
  `mcpp test`'s concurrency**, whose fallback is otherwise the whole machine.
  ```toml
  # $MCPP_HOME/config.toml
  [build]
  default_jobs = 4
  ```
  *removed in 2026.9.11.2:* `[build] default_backend` — it promised a choice that does not exist.
- *fix:* the module scanner walks three mutually exclusive states in one pass (code / block comment / raw string).
  Before this, an `export module y;` inside a block comment made an ordinary `.cpp` the recorded producer of that
  module, and a `// R"(` put the raw-string pass into a state it never left, hiding later `import`s from the scanner
  while the compiler still saw them — a **missing dependency edge**, i.e. an order race under parallelism.
  => If your sources contain commented-out module or import lines, or comments containing `R"(`, your dependency graph
  was wrong on older engines, and intermittent parallel-build failures may date from there.
- *fix:* stage failure for a **dispatched** format is now a warning that lets the command continue, with
  `${mcpp.stage_dir}` refusing at the expansion point carrying that reason. `tar`/`dir` still fail.
  => A gate that treats any warning as failure needs to distinguish this one.
- Windows: host-module flag collection stopped deduplicating by token (which broke MSVC's two-token `/reference`), and
  `import std`'s level requirement asks the **STL**, not whichever compiler reached it.

### 2026.9.11.3 / 2026.9.11.4
- **`wasm32-emscripten` reached `verified`**, and the two Android rows and three iOS rows landed. Tier words are
  `verified` / `preview` / `planned`.
  ```
  mcpp build --target wasm32-emscripten
  mcpp build --target aarch64-linux-android
  ```
- **`[target.<triple>] min_api_level`** is mandatory on Android rows — bionic refuses an unversioned triple. The level
  rides the effective triple and **enters the fingerprint**; the canonical triple is unchanged.
- **Capability pins**: some rows can only be emitted by their own toolchain (wasm, Android, PE+musl). Declaring another
  family is refused before resolution.
- Four-segment triples are accepted and normalised (`wasm32-unknown-emscripten` -> `wasm32-emscripten`); an effective
  triple with an API level parses back; a bare `aarch64-linux` is **never** completed to Android.
- *fix:* a per-target scan that was machine-scoped stopped being paid per target — 17948 ms -> 4 ms on a 108-binary
  `mcpp test`.
- A toolchain payload may describe itself in `.mcpp-toolchain.json` (schema 1): `frontend`, `platform_floor`,
  `std_module_defines`, and from 2026.9.12.2 `runner`. Absent is compatible; present but malformed is refused by name.
  WARNING: an already-installed payload only gains the file via `index update` + `toolchain remove` + `install` —
  reinstalling alone does not.

### 2026.9.12.2
- **`[target.<sel>.abi] threads`** (and from 2026.9.12.3 `exceptions`). Thread support is a property of the whole
  artifact — prebuilt std modules, dependency scanning, every TU and the link must agree — so it is an axis, not a
  flag, and it enters the dependency cache key. Only the **root** manifest may state it; a dependency's own
  `[target.<sel>.abi]` is reported (`abi/dependency-table`) and ignored. A dependency declares its need with
  `[package] requires_abi` or `[features.<f>] requires_abi`, and an unmet need is refused **before compilation**.
  ```toml
  [target.'cfg(target_os = "linux")'.abi]
  threads = true

  [package]              # in the dependency
  requires_abi = { threads = true }
  ```
  => On a musl static line, declare `threads` here rather than putting `-pthread` in `cxxflags`; mixing them yields
  inconsistent BMIs.
- **`[targets.<n>] windows_subsystem` / `windows_entry`** — fields, not link flags, because the correct flag depends on
  the ABI. They render nothing on ELF/Mach-O/wasm (byte-identical artifacts) and are refused on library targets.
  Protocol -> v10.
- **`[runtime] deploy = [{ from, to }]`** places a runtime file in a **subdirectory** next to the executable, which
  `deploy_files` cannot express. `to = "."` is the executable's own directory; paths are `/`-separated, never absolute,
  no `.`/`..` segments, and two sources landing on one destination are refused.
  *changed in 2026.9.12.2:* `mcpp pack` now stages `deploy_files` **and** `deploy` next to the packed executable —
  previously packing read neither list, so a packed smoke test may now contain more files than before.
- A dependency's install hook receives `MCPP_TARGET` / `_OS` / `_ARCH` / `_ENV`. `MCPP_COMPILER` and `MCPP_CXX_STDLIB`
  are always written but **empty at dependency-install time** (the toolchain is resolved after the graph) — do not
  read them there. A package building a static library from source declares its target standard library with
  `requires = ["mcpp:c++-abi=<stdlib>"]`, per platform.
- *fix:* an xlings invocation's environment is decided in one place, and on failure xlings' own error output (up to the
  last 20 error-level lines) is appended to mcpp's diagnostics. Dependency-install failures went from "no reason
  visible" to "twenty lines".
- *fix:* **the fast path compares the toolchain request** (`--toolchain` / `MCPP_TOOLCHAIN` / the machine default).
  Building with gcc and then running `mcpp build --toolchain llvm@22.1.8` used to print `Finished dev in 0.00s` and
  keep the gcc artifacts. Entries written before the `toolchain=` line are rejected once and rewritten.

### 2026.9.12.3
- **`[targets.<n>] kind = "app"`** — a fourth value meaning "the thing a user launches". Identical to `bin` on
  ELF/PE/Mach-O and wasm; a shared object on `*-linux-android`. `mcpp pack` treats it as a program target.
  *compatibility:* engines at or below 2026.9.12.2 reject the value by name.
- **`mcpp::deploy(from, to)`** and the `mcpp:deploy=` directive (protocol **11**) let a build program deploy files it
  generated — `[runtime] deploy` can only name files that already exist in the package. Persisted into the build cache
  like runners and warnings, so a cache hit replays it. *compatibility:* a `build.mcpp` calling it fails to **compile**
  on an older engine.
- `MCPP_TARGET_MIN_PLATFORM_VERSION` / `mcpp::min_platform_version()`; `[target.<sel>] requires_abi` and
  `[target.<sel>.feature-requires-abi].<feature>`; `[target.<sel>.runtime] frameworks`.
  WARNING: `[target.<sel>] requires_abi` is **silently ignored** by 2026.9.12.2 — a package relying on it for
  protection must state its own engine floor rather than expect older clients to complain.
- **`[package] platforms` accepts six values**: `linux | macos | windows | ios | android | emscripten`. A platform name
  is the triple's `os` unless an `env` names one itself — so **`linux` does not cover Android**, and the Web row is
  `emscripten`, not `web`.
- **`mcpp run --format <name>`** runs the distributable a `pack --format` would produce. Refused together with
  `--no-runner`.
- wasm artifacts are `bin/<name>.js` with `bin/<name>.wasm` as an implicit output of the same link edge; `pack` stages
  the whole stem family and refuses when the `.wasm` is absent. `kind = "shared"` is refused on that row.
  *This is the one deliberate artifact rename in this window.*
- *fix:* `mcpp pack --format` reports the **terminal** artifact — the output of a requested artifact action that no
  other introduced action consumes — rather than the first output of a chain. `mcpp run` refuses a format that ends in
  more than one. [`22cedfa9`, first contained in `v2026.9.12.3`]

### 2026.9.12.4
- *fix:* under a cross target, the build program's **host** toolchain is resolved properly (previously overwritten by
  the target row's pin, so any project with a build program failed under `--target wasm32-emscripten`), including its
  own C library. => A project-local fresh `MCPP_HOME` whose first command is a cross build was the exact repro; a
  developer machine hid it behind existing state. [`13f5a8a9`, first contained in `v2026.9.12.4` — **not** 2026.9.12.3;
  an engine floor stated for this fix is `2026.9.12.4`.]

### 2026.9.13.1 / 2026.9.13.2
- **`${mcpp.self}` and `mcpp stage` became a contract.** An action's command is argv with no shell, so there was no
  portable way to copy a file: `${mcpp.self} stage --verify content --output <dst> <src>`. `--verify` defaults to
  `content`.
- *changed in 2026.9.13.1:* an action's lists have **no length limit** (previously 8 KiB of serialised JSON per list,
  and an overlong declaration was refused as "arguments did not fit"). The command-length guard now measures literal
  command text rather than the ninja build line.
- **Two declarations of one dependency identity have a stated decision table** [docs/05-dependencies.md]: identical
  kind and reference is silent; two version constraints are AND-combined and an unsatisfiable pair is refused naming
  both; differing `git`/`path` declarations resolve to the **root's** when the root is one of the requesters, always
  with a `dependency/source-override` warning naming both sides; two non-root declarations of different kinds are still
  refused, now suggesting you declare the identity in the root to settle it.
  *changed in 2026.9.13.1:* no field was compared at all — whichever declaration was dequeued first survived.
- *fix:* the host-tool store key carries the source — a `git` tool by resolved commit, a `path` tool by a stat imprint
  of its tree. Editing a path-dependency tool without bumping its version used to serve the stale binary.
  WARNING: that imprint includes **mtime**, so the tar/cp rollback trap applies here too.
- `mcpp emit xpkg` maps OS-only selectors (`cfg(linux)`, `cfg(os = "windows")`, `cfg(macos)`, `cfg(unix)`) into the
  descriptor's platform blocks. Every other selector keeps its warning.
- *fix:* `min_api_level` is a known `[target.<triple>]` key (it had been reported unsupported, a hard error under
  `--strict`).

### 2026.9.14.1 / 2026.9.14.2 / 2026.9.14.3
- **`--toolchain` is a declared option on `run`, `test` and `pack`** (and on `emit build-database`). The value always
  reached them through `MCPP_TOOLCHAIN`; only the spelling was refused.
- **`[test] discover`** selects where tests come from, using the `[build] sources` vocabulary including `!`:
  ```toml
  [test]
  discover = ["checks/**/*.cpp", "!checks/fixtures/**"]
  ```
  `discover = []` finds nothing; duplicate test names are refused naming both files. WARNING: `mcpp test --list` falls
  back to `tests/**/*.cpp` when the manifest cannot be loaded, and some downstream consumers still read that default.
- **A conditional dependency declaration replaces the unconditional one of the same identity** on matching rows
  (`dev-`/`build-dependencies` and `feature-deps` likewise; later matching sections win).
  *changed in 2026.9.14.2:* the unconditional declaration survived, so options written in a conditional table — a
  `linkage = "shared"`, for instance — were silently dropped on exactly the rows they were written for.
- **A `path` or `git` dependency takes the identity its own manifest declares.** A key normalising to a different
  identity warns once per declaring edge; when the manifest declares no namespace, two differently-namespaced keys over
  one source are refused before scanning.
- **`resolution.json` gained `graph`**, and `mcpp why deps` prints it: every package, every request with the key **as
  written** and the table that declared it, and each library's link form with its reason. This is the intended test
  surface for a resolution rule — assert against the record, not against a warning's wording.
- Each runner receives **`MCPP_RUNTIME_FILES`** (deployed files and linked shared libraries, TAB-separated).
- **`config.toml [index.repos.<name>]` reaches an already-initialised home.** What mcpp wrote is recorded in
  `.mcpp-index-overrides.json` beside `.xlings.json`, so deleting the table restores the previous entry — while the
  file still holds what mcpp wrote.
  *changed in 2026.9.14.2:* the table only seeded a home that did not yet exist, so adding it to a home that had ever
  run did nothing and said nothing. => Entries written earlier and ignored will **start taking effect** on upgrade.
- Platform floors are engine facts a dependency can require (`android.api-level`, `ios.deployment-target`,
  `macos.deployment-target`); `mcpp::pkg_config_libdir()`; ELF shared libraries default their SONAME to the file name.
- *fix (2026.9.14.3):* mcpp never passes `XLINGS_ACTIVE_SUBOS` to its bundled xlings. A shell that ran
  `xlings subos use <name>` redirected mcpp's registry into a same-named other SubOS — bootstrap tools in the wrong
  place, an empty pkg-config view. The symptom is indistinguishable from a broken registry, so **do not re-bootstrap on
  that evidence alone**.

### 2026.9.15.1
- **`mcpp emit build-database`.** Plans the way `mcpp build --configure-only` does, using the same selectors, and
  prints the plan as an S1 "C++ Build Database: IDE Profile" 0.2.0 document (a profile of WG21 P2977R2) — **without
  writing into the project**. Planning happens under `$MCPP_HOME/cache/build-database/<key>`. `mcpp.lock` is read from
  the project and never written back; a disagreement warns with `MCPP_LOCK_WOULD_CHANGE`. Rules: SPEC-005.
  ```
  mcpp emit build-database                                  # S1 document to stdout
  mcpp emit build-database --spec compile-commands           # compile_commands.json entries
  mcpp emit build-database --format json -o db.json          # mcpp.build-database envelope, atomic write
  mcpp emit build-database --workspace --target x86_64-linux-musl --profile release
  ```
  WARNING: it declares `network` and `exec-build-script` — read-only with respect to the **project**, not to the
  machine. Its planning directory is a pure cache neither `mcpp clean --stale` nor `mcpp cache gc` manages.
- **Envelope convention: `data` is omitted when the command failed** (exit 1), rather than being an empty object. A
  script doing `jq .data.x` now gets `null`.
- Bundled xlings moved to **2026.9.14.1**. Before it, a package with no `install()` received the *entire* download
  directory instead of its own archive — one measured package directory carried 1.6 GB of other packages' downloads.
  `xlings self doctor` reports such directories and `--fix` reinstalls them:
  ```
  XLINGS_HOME=<registry> xlings self doctor --fix
  ```
  => Worth running read-only `self doctor` once on a long-lived project-local registry.
- *fix:* a target entry source not matched by any `sources` glob is read by the **scanner**, so an `import` inside a
  comment or a raw string is no longer planned as real.

### 2026.9.15.2 (previous baseline)
- **`[targets.<n>] linkage = "static" | "shared"`** states a package's **default** link form — not a constraint, which
  is what `kind = "shared"` is. Precedence, most specific first: the root's `linkage` on the dependency edge, then the
  root's `dependency_linkage`, then the package's `linkage`, then `static`. Overriding the package default is not a
  degradation (`--strict` accepts it) and prints one `Linkage` information line. `kind = "shared"` and `linkage` in one
  table are refused, as is `linkage` on a program target. `mcpp why deps` reasons gained `package-default`.
  ```toml
  [targets.mylib]
  kind    = "lib"
  linkage = "shared"        # what a consumer who says nothing receives
  ```
  WARNING: on a fully static image the default is dropped **with no warning** — nobody asked for it. And an engine
  before 2026.9.15.2 reports the key as unsupported (silently, for a dependency) and links static, so a package using
  it must state an engine floor.
- **`MCPP_DEP_<NAME>_LINKAGE` / `mcpp::dep_linkage(name)`** — dependency link forms are computed once before the root
  build program runs, so the root can read them. A dependency's own build program cannot: only the root decides.
- **`mcpp pack --features <LIST>`** applies to **every** build pass of the pack (each `--target` leg, both passes of a
  dispatched format); `mcpp run --format` hands its own features to the pack it performs.
- **`cxx_runtime = { shared = "self-contained" }`.** In a graph whose C++ runtime is a package, a dependency's C++
  shared library previously had no C++ runtime at all; it is now refused before compilation
  (`shared-library-cxx-runtime`), and this key opts into a private copy per image. Measured consequence stated in the
  refusal: with one copy per image, a `std::runtime_error` thrown by the shared library is not caught by that class in
  the program.
- A C++-layer provider that declares `[package] standard` compiles its own non-module implementation units at that
  level while module units stay at the graph's level, so a `c++20` program can use `llvm.libcxx`. The level enters the
  dependency cache key.
- *changed in 2026.9.15.2:* object addresses for sources outside the declaring package moved to
  `obj/<declaring>/__pkg/<owner>/<path>` (or `__ext/<dir hash>/`), and host-tool sub-build scratch to
  `<cache>/tool/.build/<16 hex>`. => Any script asserting on specific paths under `target/` needs re-reading, and those
  objects rebuild once after the upgrade.
- `!` exclusions now also apply to the p1689 scanner (`hasSources` comes from the scanner's exported source list), so a
  member with exclusion globs can see different scan results.
- *fix:* a required compiler family's version comes from pins on rows using that **payload**, so on a fresh home
  `requires = ["mcpp:compiler=llvm"]` no longer resolves to the NDK's llvm.

### 2026.9.16.1 (mcpp#646-#649, one large merge)
Images and runtimes:
- *changed:* on ELF, a program or test that loads a C++ shared library **this build made** takes that library's C++ runtime
  contract when nobody stated one (previously a self-contained program over a toolchain-coupled library carried two runtimes in
  one process; upstream measured `std::bad_cast`, exit 134, with llvm and 900 interposed libstdc++ symbols with gcc).
  `resolution.json` records the result under `runtime.cxx_runtime_by_role`. A program that **states** `self-contained` in that
  situation is refused before compiling: `program-cxx-runtime-split`. Ways out: drop the statement, or give the library
  `cxx_runtime = { shared = "self-contained" }`.
- *changed:* a static package reached by exactly one shared library (and not by the root) is linked **into that library**, not
  the program. A static package reached by **several** images is refused on Mach-O, PE and the Android `app` row
  (`static-package-in-two-images`) and warned about on other ELF rows (`build/static-placement`, an error under `--strict`); the
  remedy is `linkage = "shared"` on the root's edge or as the package's `[targets.<n>] linkage`.
- The duplicate-symbol check stops reporting definitions shared by construction (`STB_GNU_UNIQUE`, one object linked into two
  images such as the `std` module initialiser, and that initialiser against GCC 16's own runtime).
- On Mach-O the default (each image embeds a hidden `libc++.a`) is unchanged, but a build whose program loads its own C++ dylib is
  told once, `build/cxx-runtime-identity`: exceptions and `std::error_code` categories do not compare equal across such images
  unless every role states `cxx_runtime = "host-coupled"`.
- The llvm row of `x86_64-windows-msvc` now **records** what it always did: the static CRT (`libcmt`), i.e. `self-contained` whatever
  `cxx_runtime` says; an explicit `host-coupled`/`toolchain-coupled` there prints that the row cannot deliver it. Use `msvc@system`
  for the dynamic CRT.

Graph, build programs and packing:
- `MCPP_GRAPH_FILE` / `mcpp::graph_file()` for the root build program, and `[package.metadata.<tool>]` kept verbatim for it.
  *changed:* unknown `[package]` keys are now reported like `[build]`'s (warning, error under `--strict`).
- `mcpp pack --release` / `--dev`, and `--profile` wins over a shorthand on `build`/`run`/`test`/`pack` (*changed on `run`*, where
  the shorthand used to win).
- `mcpp pack --message-format json` -> one `mcpp.pack` envelope (`data.artifacts[]` with absolute `path`, `type`, `format`,
  `targets`; `data.stage`), failure code `MCPP_PACK_FAILED`.
- *changed:* `mcpp pack` strips what the graph built on every row that carries debug info in the image: the program (as a shared
  library on Android, which it is there), graph-built shared libraries and the staged copy of the toolchain runtime, with
  `--strip-unneeded`. Store, host and prebuilt libraries are never stripped. `MCPP_PACK_STRIP` / `MCPP_PACK_DEBUG_SYMBOLS_DIR`
  carry the decision to a packaging member.
- Android rows link from a macOS host (the link line is chosen by host **and** target object format).

Features, tools, git:
- `--features <dep>/<feature>` on `build`/`run`/`test`/`pack`/`emit build-database`/`why deps`: applied as a forward of the root,
  never a root feature, never a macro; a token naming no dependency warns (error under `--strict`).
- Forward validation reads every dependency table on every row; a key declared only for another row is no longer reported.
- *changed:* a `[feature-deps]` restatement with a different source is refused (was ignored); the restatement must spell a source.
- `dep_bin` / `dep_dir` / `dep_linkage` share one naming derivation (`MCPP_DEP_NS_X_*` now exists for `namespace = "ns"`,
  `name = "x"`).
- *changed:* a dependency whose targets are all programs is not part of the consumer's graph; package cycles are refused
  (`package-cycle`); a tool that requests itself is refused at the first repetition.
- A `git` key whose identity is a member of the repository's workspace selects that member at the same commit; a second
  declaration of one dependency by one consumer merges its `tools`/`features`/`host-module`/`reexport`; the compile line of a git
  dependency carries its commit instead of an empty version.

Editors planning in the background (#648):
- The refresh decision walks the same deprecated bare-name rung the resolver does, so `ftxui = "6.1.9"` (really `compat.ftxui`) no
  longer triggers a network `xlings update` on every plan.
- Planning subprocesses do not inherit the caller's stdout pipe; xlings children are bounded (`[index] refresh_timeout`, default
  120 s; 300 s of silence for an install) and die with mcpp.
- `effects.network` is observed, not declared; *changed:* `[index] auto_refresh = false` covers every implicit refresh.
- `MCPP_OFFLINE_DOWNLOAD_REQUIRED` / `offline-download-required` when an offline plan needs a download.
- The default `mcpplibs` index `artifact` is `{ GLOBAL = github, CN = gitcode }` and existing homes are upgraded in place;
  under `mirror = CN` the refresh goes to GitCode first (with the xlings pinned from 2026.9.16.2 on, GLOBAL is the next
  candidate and git the last, rather than git directly).

### 2026.9.16.2
- Bundled xlings pinned to **2026.9.16.1** (openxlings/xlings#601): a region object is an ordered candidate list, so a CN 403 now
  falls to GLOBAL before git; one index refresh is bounded (git low-speed abort, index HTTP 10 s / 120 s, 300 s per update), with
  `XLINGS_GIT_NETWORK_TIMEOUT` / `XLINGS_INDEX_HTTP_TIMEOUT` / `XLINGS_UPDATE_TIMEOUT` as overrides. No mcpp code change.
  This is still the pin at 2026.9.21.3; xlings 2026.9.20.1 exists but mcpp does not run it.

### 2026.9.17.1 (#655)
- *changed:* the compile-flag element word syntax of SPEC-004 §8 (see `../SKILL.md` §5). `defines` entries and `mcpp:cfg=` are
  single values (`N="x"` keeps its quotes). A changed reading warns once per plan as `build/flag-words`.
- `compile_commands.json` / `emit build-database` `arguments` are the words the compiler receives, executable without a shell
  (SPEC-005 v1.2 R3.7). This is what broke libarchive/bzip2/lz4/xz/zlib/zstd consumers of the database before.
- Windows `shell_quote_arg` doubles backslashes before quotes the MSVCRT way.
- `import std` builds on macOS 27 (the SDK's `INFINITY`/`NAN` are restated for clang 22 on Apple targets).

### 2026.9.17.2 (#660)
- *changed:* the glibc a gcc/llvm payload's runtime binding declares is **installed by mcpp** before the first fixup needs it
  (`ensure_declared_runtime`: Linux only, `glibc` provider only, gcc/llvm payloads only; a system, musl or PE toolchain downloads
  nothing). Lookup is exact: `glibc@2.44` means `xim-x-glibc/2.44`, never a neighbouring revision. A home missing it downloads
  about 40 MB once; offline, the error names `xim:glibc@<version>`. This closed the "toolchain post-install fixup: selected
  RuntimeBinding glibc@… requires payload …" failure on CI caches that restore `registry/data/xpkgs` only.
- *changed:* the xlings released with this mcpp (`<prefix>/registry/bin/xlings`) is preferred over the one on PATH.

### 2026.9.17.3 (#662)
- *changed:* a graph-supplied `c-abi` adds `-nostdlibinc`, a graph-supplied `c++-abi` adds `-nostdinc++` (Clang family), each on
  its own layer's origin. Payload-supplied and native builds are byte-identical to before. GCC plus a graph C library: unchanged
  command line, `degraded` warning (error under `--strict`). A build failing with `file not found` in this configuration gets advice
  naming the C library. Flags fingerprint changes -> one rebuild.
- Documented (not new): `visibility = "private"` on `[feature-deps.<f>]` entries keeps a platform SDK's headers off consumers.

### 2026.9.18.1 (C environment design)
- `[c-abi]` (`presents` / `data-model` / `wchar` / `builtins`), only in a package that provides `mcpp:c-abi=<impl>`, realised by
  the engine and verified with a `-E -dM` probe (`c-env-unrealisable`, `c-env-verification-mismatch`). A package without the block
  produces byte-identical command lines.
- `[package] c-environment = "platform"` opts a package's own units out; it is **inferred** for any `mcpp:kernel-abi=<impl>`
  provider.
- `provides = ["platform-sdk"]` + `[build] platform-dependencies = "refuse"` (`platform-dependency`); the `Target` report gains a
  `platform-deps` line.
- `__openkal__` (lower case in this release) for every target-side unit when `kernel-abi` resolves to `openkal`.
- *changed:* **global dependency cache epoch 2 -> 3** - the first build after upgrading recompiles every dependency. The realised
  environment enters both the build fingerprint and the cache key; assembly units get the same realisation through a new
  engine-only `asmflags` broadcast channel.

### 2026.9.18.2
- Three fixes to 18.1's rule: GCC is accepted when the realisation is empty (openkal-musl on Linux); macOS and freestanding
  realise `presents = "posix"` with one `-D__unix__` (they used to be wrongly assumed satisfied, or refused).
  Known trade-off: `#ifdef __unix__ ... #elif defined(__APPLE__)` now takes the Unix branch on macOS for such graphs.

### 2026.9.18.3
- On a freestanding target the `wchar` declaration is now always realised with an explicit `-fno-short-wchar` /
  `-fshort-wchar` (a Windows-hosted clang defaults to 16-bit even for `riscv64-none-elf`); hosted targets still add it only when
  the declaration differs from the triple's native width. A `hostStripMacros` list was also added to the probe - **withdrawn in
  2026.9.20.1** as a misdiagnosis.

### 2026.9.20.1
- *fix:* the `[c-abi]` verification probe now selects the target on freestanding builds (it used to measure the build host, which
  passed for the wrong reason on Linux and failed on Windows). `cenv_probe::assemble_argv` refuses a freestanding argv with no
  target.
- `[kernel-abi] provides-interfaces` (providers only) / `requires-interfaces` (anyone): a set difference at resolution, refused
  before compiling with reason `interface-not-provided`, which is also printed in brackets inside the message.
- Top-level `[c-abi-absent]` (`form = "link" | "enosys" | "accepted-no-effect"`, optional `note`): read back when a link fails on
  a `link`-shaped name, so the undefined-reference error carries the explanation. `absent` inside `[c-abi]` is refused.
- `presents` is frozen at three values and answers no capability question.
- *changed:* `nasm` comes from the pinned xlings package first; the host's is used only when that cannot serve, and the build then
  says `degraded: the assembler for this build is the host's (...)`.
- *changed (#676):* `mcpp.lock` hashes and the git cache directory key are FNV-1a on every host (they were `std::hash`, i.e.
  MurmurHash on libstdc++/libc++). One lock diff after upgrading on Linux/macOS.
- `docs/50`'s reason-token table is now checked against `refusal.cppm` in CI; `apple-sdk-absent`, `lld-required-absent`,
  `host-tool-toolchain` and `std-module-precompile` joined it.

### 2026.9.21.1 / 2026.9.21.2
- Engine macros became a tested contract (`src/toolchain/predefines.cppm`): `__MCPP_TARGET_<OS>__` on every target, always.
- *changed in 2026.9.21.2:* owned macros are upper case - `__mcpp_target_<os>__` -> `__MCPP_TARGET_<OS>__`, `__openkal__` ->
  `__OPENKAL__`. No alias was kept.
- *changed in 2026.9.21.2:* under Windows `presents = "posix"` the compile line adds `-U__CYGWIN__ -U__CYGWIN32__`; the substitute
  `--target=x86_64-pc-cygwin` stays. Installed headers that sized records on `__CYGWIN__` moved first (openkal-musl 0.19.0,
  openkal-llvm-runtime 0.14.0 read `__MCPP_TARGET_WINDOWS__ || __CYGWIN__`). WARNING, residual window upstream names: a project
  that pins openkal-musl **exactly** at 0.18.0 or older while running an engine at 2026.9.21.2 or newer gets the silent `#else` in
  `bits/setjmp.h` (wrong `jmp_buf` size on Windows targets).
- A provider that states no `provides-interfaces` while a consumer states requirements now prints
  `note kernel-abi interfaces: <impl> states none, N requirements unchecked`.

### 2026.9.21.3
- **`mcpp test --no-run`** (see `../SKILL.md` §4): status `built`, summary `built`, workspace `tests_built`, exit 0; refused with
  `--no-runner`.
- *changed:* `[c-abi] builtins = "iso"` emits `-fno-builtin` on Apple targets (the old `-fno-builtin-memset_pattern16` was a silent
  no-op: clang accepts any `-fno-builtin-<name>` and that libfunc is not in its builtin table). Measured cost on one libarchive TU:
  +1.8 % object size.
- Measured and recorded, not fixed: the Windows cygwin substitute triple makes LLVM reject `__builtin_thread_pointer()`
  (mimalloc fails in the backend) - the first substitute-triple cost that is not about macros.

Commits after the `v2026.9.21.3` tag, up to `b30e70c4` (no engine change, no new version): the Chinese README and manual were
retranslated, and a PyPI channel was added - `pip install mcpp-bin` (or `pipx install mcpp-bin`) installs the release binary for Linux x86_64/aarch64, macOS 14+
arm64 and Windows x86_64; data still lives in `~/.mcpp`. The PyPI name `mcpp` belongs to an unrelated project.

### 2026.9.24.1 (this baseline; mcpp#685, #687, merged as #688)
One commit, `b4824697`, tagged `v2026.9.24.1`; its CHANGELOG section is `CHANGELOG.md:6-88 @ b4824697`. Citations in this
section are all `@ b4824697`. `src/cli.cppm` did not change, so every command and flag is as at 2026.9.21.3.

Toolchain spelling:
- *changed:* `xim:` is the only namespace a toolchain spelling accepts. Any other `<ns>:` prefix used to be stripped silently; it is
  now refused with `'<ns>:' is not a toolchain namespace` wherever a spelling is parsed, and so is `xim:<family>@system`
  [src/toolchain/registry.cppm:539-550,574-581]. `xim:gcc@16.1.0` and `gcc@16.1.0` remain the same toolchain.

MSVC toolset (both the cl.exe row and clang on `*-windows-msvc`), one selection for both rows [src/toolchain/msvc.cppm:855-970]:
- `msvc@system` takes the first complete toolset of: `VCToolsInstallDir`; the default toolset of the instance `VSINSTALLDIR` (or
  `VCINSTALLDIR`) names; the toolset of the first `cl.exe` on `PATH`; the default toolset of the newest instance with the C++ tools
  (`vswhere -all -prerelease`); without vswhere, the conventional `Program Files` paths [docs/20-toolchains.md:381-397]. A toolset
  is complete with `include\`, `lib\x64\` and, for the cl.exe row, `cl.exe`; an instance's default toolset is the one
  `VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt` names.
  *changed:* on the cl.exe row `msvc@system` used to take the highest-named toolset directory of the chosen instance and did not read
  `VCToolsInstallDir`.
- *changed:* `msvc@<toolset>` takes a complete installed toolset of that version, searched across every instance, before the payload
  (a partial version matches component by component, `14.4` matches `14.4.x` but not `14.44`, and the highest match wins); the
  environment takes no part, and a `VCToolsInstallDir` naming another toolset is reported in a `note:` [src/toolchain/msvc.cppm:883-913;
  src/build/prepare.cppm:3607-3630]. The SDK follows the origin: an installed toolset uses the machine's SDK, a payload toolset the
  `windows-sdk` payload beside it. It used to mean the payload unconditionally; that meaning is now spelled `xim:msvc@<toolset>`.
- *changed:* a cl.exe toolset without `modules\std.ixx` no longer borrows another toolset's; `import std` is unavailable for it
  [src/toolchain/msvc.cppm:1516-1526].
- `mcpp toolchain list` on Windows prints `installed toolsets (pin one as msvc@<toolset>):` [src/toolchain/lifecycle.cppm:591-600],
  and `mcpp toolchain default msvc@<toolset>` accepts an installed toolset without installing the payload [:1177-1200].

Clang on the MSVC ABI - the toolset is the row's sysroot:
- `[target.<triple>].sysroot` on a `*-windows-msvc` row takes `msvc@system` (the default when absent), `msvc@<toolset>` or
  `xim:msvc@<toolset>`; any other value is refused at parse time naming the three spellings. On every other row the key keeps its
  xpkg-reference grammar, so `msvc@...` there is refused as `not an xpkg reference` [modules/manifest/src/toml.cppm:676-701].
- *changed:* on a `*-windows-msvc` row, `sysroot` no longer accepts an xpkg reference or `""` (refused at manifest parse on every
  host) [modules/manifest/src/toml.cppm:679-690]. Both were accepted before, so a manifest that names a C library package or the
  zero-libc layer on that row stops parsing on Linux and macOS as well.
- prepare resolves the toolset and SDK once [src/build/prepare.cppm:1393-1535] and passes `-Xmicrosoft-visualc-tools-root`,
  `-Xmicrosoft-windows-sdk-root`, `-Xmicrosoft-windows-sdk-version` (separate words) on compile, link and the `std` precompile
  [modules/toolchain-model/src/linkmodel.cppm:120-132; src/toolchain/hostflags.cppm:345,614; src/build/flags.cppm:1769-1772]; with
  them clang reads neither `VCToolsInstallDir` nor `%INCLUDE%`. `std.ixx` comes from the same toolset; only `std` is rebound, not
  `std.compat` [src/build/prepare.cppm:1506-1522].
- The build prints `Resolved sysroot msvc@system → MSVC <version> (<origin>: <product>) · Windows SDK <version>`
  [src/build/prepare.cppm:1528-1533]. `resolution.json` gains `msvc_toolset` (`version`, `origin` = `system`|`managed`, `product`,
  `root`) and `windows_sdk` (`version`, `root`), absent on every other row [:15209-15224]. The toolset directory and SDK version join
  the dependency cache key [src/build/cache_key.cppm:502-509], `stdlibVersion` becomes the toolset version [src/build/prepare.cppm:1504],
  and the SDK version is the row's runtime identity `ucrt@<version>`.
- A pinned toolset found neither on the machine nor as a package fails naming what is installed and
  `mcpp toolchain list --available msvc` [src/build/prepare.cppm:1455-1474]. On the cl.exe row a `sysroot` that names a different
  toolset than the compiler is refused [:1542-1563].
- Older engines reading the new spelling (upstream measured 2026.9.21.3 on a Windows runner): `sysroot = "msvc@system"` and
  `"msvc@<toolset>"` get the whole manifest refused (`is not an xpkg reference`); `"xim:msvc@<toolset>"` is accepted and has no
  effect - nothing is installed and clang builds against the machine's toolset [docs/20-toolchains.md:553-559]. A project that
  depends on the toolset it names pins mcpp 2026.9.24.1 or later.

macOS deployment target (mcpp#685):
- *changed:* resolution (`MACOSX_DEPLOYMENT_TARGET` > `[build] macos_deployment_target` > `14.0`) no longer consults the host, and
  whether it applies is decided by the target's `os` for the triple, the fingerprint, `-mmacosx-version-min`, the `std` precompile
  and the `macos.deployment-target` fact [modules/platform/src/macos/macos.cppm:125-132; src/build/prepare.cppm:2111-2113,13007-13013;
  src/toolchain/hostflags.cppm:534-537]. Before it, a Linux or Windows host building `aarch64-macos` always produced `minos 14.0` and
  editing either input did not rebuild; a macOS host building a non-Apple target carried `-mmacosx-version-min` on its compile line.
  `build.mcpp`'s host compile follows its own target, the host [src/build/build_program.cppm:1215-1221].

gcc payloads (mcpp#687):
- `mcpp self doctor` has a new check, `Checking gcc include-fixed headers`: every installed gcc-family payload (native, musl-gcc,
  MinGW, cross) is scanned for `include-fixed/` files whose first 2 KiB carry the `auto-edited by fixincludes` banner, and each hit is
  a warning (not an error) naming the files, the frozen source path from the banner, and the remedy `mcpp index update`, then
  `mcpp toolchain remove gcc@<v>` and `mcpp toolchain install gcc@<v>` (with `--target` for a cross payload)
  [src/doctor.cppm:116-164,618-691]. Any warning makes `mcpp self doctor` exit 1 (2 if it also reports an error)
  [src/doctor.cppm:757], so a CI step gating on doctor turns red on a home with an affected payload. The CHANGELOG names the gcc
  13.3.0, 15.1.0 and 11.5.0 `x86_64-linux-gnu` payloads, where a frozen `pthread.h` sits ahead of glibc 2.44 and breaks `<mutex>` /
  `<memory>` [CHANGELOG.md:72-82]. The index recipe fix is openxlings/xim-pkgindex#870; an index update does not re-clean a payload
  that is already installed.

Also in this release:
- SPEC-006 `docs/specs/toolchain-management.md`, draft v0.2 (see `mcpp-toml.md` §14).
- A toolchain-derived path containing whitespace is quoted as one word on the ninja command line instead of splitting; a path without
  whitespace keeps its spelling byte for byte [src/build/flags.cppm:645-650]. The `std` precompile command is double-quoted for
  cmd.exe on Windows; POSIX keeps its single quotes byte for byte, so the `std` cache key does not move there
  [src/toolchain/stdmod.cppm:274-284].

## 3. Older version markers (consult when authoring packages or CI)

> These are historical facts about when a capability landed, and they do not move with the current release. They matter
> when you publish a package that must work on an older client, or when reading an old manifest.

| Since version | Change |
|---|---|
| 0.0.100+ | `mcpp:source=` / `mcpp:include-dir=` / `mcpp:include-dir-after=` directives |
| **0.0.106** | Descriptor identity rules (short-form descriptors give `E_NOT_FOUND` on <=0.0.105; an index that adopts the short form **must** raise `min_mcpp` in `index.toml` to this version) |
| 2026.8.3.3 | Before this, mingw builds on a Windows host produced `foo.lib`; after, `libfoo.a` => scripts globbing `*.lib` must change |
| 2026.8.5.1+ | `mcpp::action`, `mcpp::dep_bin`, `tools`/`host-module` on dependency edges, build.mcpp 600s timeout |
| 2026.8.6.2+ | `mcpp::rerun_if_changed_glob`, `reexport = true` |
| **2026.8.10.1** | Unique exact selectors; bare-name fallback ramp begins. WARNING: SPEC-004's predecessor says "removal in `2026.9`", and that **has not happened** — §4.2.1 of `docs/specs/package-identity.md` still describes the ramp and `allowLegacyBareDefault=true` is still passed on 2026.9.15.2 [src/pm/package_fetcher.cppm:724,762]. Treat it as deprecated, not gone; a build that only works because of it still emits a deprecation warning |
| 2026.8.11.1 | **the `build.mcpp` action timeout** became effective on every platform (previously POSIX only, so it was silently inert on Windows). WARNING: **upstream contradicts itself about `mcpp test --build-timeout` on Windows.** `docs/30-build-mcpp.md:1469-1475` names `--timeout` and `--build-timeout` among the three fixed by this release; `docs/08-testing.md:153`, under "Current limitations", still reads "`--build-timeout` is POSIX-only". **Take docs/08 until measured** - this skill's own `mcpp test` table and `SKILL.md` §4 say POSIX-only, and a Windows gate leaning on it leaves a hung link unbounded |
| 2026.8.16 | `cxx_runtime` was **completely inert** for MSVC before this => manifests of that era writing `cxx_runtime = "self-contained"` **silently change CRT model** after upgrade (`/MD` -> `/MT`) |
| 2026.8.18.1 | A bare `[target.'<triple>']` is no longer lazy without an explicit `--target`; a warning is now issued when the partition kind cannot be determined (previously it arrived as "it is an interface" — the answer that produces **no** warning => implementation partitions were silently published) |
| 2026.8.19+ | `mcpp:link-script=`, `mcpp::xpkg_dir` |
| 2026.8.19.2+ | `mcpp:runner=` |
| 2026.8.19.4+ | `mcpp::toolchain_dir()` / `mcpp::sysroot_dir()` |
| 2026.8.20.2 | C-library substitution "Expressible since ... **verified only for the empty value**" |
| 2026.8.21.2+ | `mcpp:warning=` (survives the build cache, replayed on every hit) |
| 2026.8.21.3+ | Declaring a C library on a zero-libc line: `[target.aarch64-none-elf] sysroot = "xim:picolibc-aarch64@1.8.12"` |
| 2026.8.24.6 | `x86_64-windows-musl` appears as a separate name (previously `x86_64-windows-gnu` was **two different C libraries**: MinGW CRT when supplied by payload, musl when supplied by the graph; artifacts differed "16.7x in size and named entirely different DLLs" while mcpp could not say which was which) |
| **2026.8.25.1+** | build.mcpp **PATH prepending** (only for projects declaring `[xlings].subos`) |
| **2026.8.25.2** | The Targets section of `mcpp toolchain list` starts listing targets **supplied by the dependency graph** (previously payload-served only => they were wrongly omitted) |
| **2026.8.26.1** | **Early rejection** when naming a compiler that does not supply the C library for that target (previously it ran the whole build and died at `crtbeginT.o (bare name)`; on machines with a system gcc it would even **silently** reach into `/usr/lib/gcc/...`) |
| **2026.8.26.2** | The tier gate now asks about the **written** value (previously it asked about the completed value, reporting a planned rejection for commands that never wrote `gnu`) |
| 2026.8.27.1 | `[build] private_include_dirs`; compile-side target predicate aligned with the link side; `targetHeaderSet` axis added to the cache key (WARNING: **does not bump `kCacheEpoch`**); removed the fourth copy of home discovery (it would reach into other homes) |
| 2026.8.27.2 | On Windows, directory names unrepresentable in the current code page make mcpp exit with an internal error (#516) — WARNING: **the trigger is broader than it looks**: globs like `include_dirs = { "*" }` that start with `*` have an empty literal prefix and will **recursively walk the entire upstream source tree without bound**; **103 of the 130** recipes in mcpp-index contain at least one |
| **2026.8.28.2** | `[build] dependency_linkage` + `linkage` on the edge (#519); symbol-provider check (the criterion is **measured**, not declared; warning by default, `--strict` raises to error); `-fPIC` enters the cache key; `mcpp pack` collects synthesized shared libraries; `soname` rejection narrowed to "non-library targets" |
| 2026.8.30.2 | `[workspace.package]` / `[workspace.build]`; `[toolchain] <platform> = "system"` explicitly rejected; bare integer `standard = 26` accepted; early rejection when a dialect flag missed the `import std` precompile; the fast-path staleness scan covers `path` dependency roots; `mcpp test` post-link records moved to `.mcpp-runtime-verdicts.json` |
| **2026.9.16.1** | `[package.metadata.<tool>]` + `mcpp::graph_file()`; `MCPP_PACK_STRIP` / `MCPP_PACK_DEBUG_SYMBOLS_DIR`; qualified `MCPP_DEP_NS_X_*` names; git member selection. A build program that calls `graph_file()` needs this floor (older bundled `mcpp` modules lack the function, so it fails at `build.mcpp` compile time). `[package.metadata]` itself needs none: older engines ignore it |
| **2026.9.17.1** | compile-flag word syntax. A descriptor or manifest that relies on the new reading of a quoted/escaped element (or on `defines` keeping quotes) builds differently below it |
| **2026.9.18.1** | `[c-abi]` (C-library packages), `[package] c-environment`, `platform-sdk` / `platform-dependencies`, `__openkal__` (lower case until 2026.9.21.1). Upstream's openkal-musl states **2026.9.18.3** as its practical floor and mcpp-index's `min_mcpp` is 2026.9.18.3 |
| **2026.9.20.1** | `[kernel-abi] provides-/requires-interfaces`, top-level `[c-abi-absent]` (both ignored, harmlessly, by older engines), the freestanding-correct `[c-abi]` probe |
| **2026.9.21.2** | `__MCPP_TARGET_<OS>__` / `__OPENKAL__` spellings; `__CYGWIN__` no longer defined for Windows `presents = "posix"`. An installed header must test `__MCPP_TARGET_WINDOWS__ \|\| __CYGWIN__` to be right on both sides |
| **2026.9.21.3** | `mcpp test --no-run` - a CI leg using it needs this floor (older engines: `unknown option`, exit 2) |
| **2026.9.24.1** | `sysroot = "msvc@..."` on a `*-windows-msvc` row (older engines refuse the manifest for `msvc@system` / `msvc@<toolset>` and silently ignore `xim:msvc@<toolset>`); `msvc@<toolset>` meaning "installed first"; `macos_deployment_target` honoured when cross-compiling to macOS from a non-Apple host. A manifest or CI script that writes a toolchain with a namespace other than `xim:` breaks at this version, not below it, and so does a manifest whose `*-windows-msvc` row sets `sysroot` to an xpkg reference or `""` (refused at parse, on every host) |

## 4. What to do when upgrading to `2026.9.24.1`

### 4.0 Coming from `2026.9.21.3`

Read from source, not measured on a binary. Coming from older than 2026.9.21.3, do §4.1 (and §4.2) as well.

1. Grep every toolchain spelling for a namespace prefix - `[toolchain]`, `[target.<t>] toolchain`, `--toolchain`,
   `MCPP_TOOLCHAIN`, CI scripts calling `mcpp toolchain install/default`. Anything other than `xim:` is now refused with
   `'<ns>:' is not a toolchain namespace`, and `xim:<family>@system` is refused too. `xim:gcc@...` / `xim:llvm@...` still work
   and mean the same as without the prefix. This and item 2 are the changes here that can stop a Linux build.
2. Check `sysroot` in every `[target.<triple>]` section whose triple ends in `-windows-msvc`. It now takes only `msvc@system`,
   `msvc@<toolset>` or `xim:msvc@<toolset>`; a C library package or `""` there, accepted before, is refused when the manifest is
   parsed, on every host (§2). Delete the key, or write one of the three spellings and pin the engine to 2026.9.24.1 or later.
3. Budget one project rebuild, not a dependency rebuild. The project fingerprint changes with the version, as always (§4.2
   item 1), so every member opens a new `target/<triple>/<fp>/`. The dependency cache epoch is still 3 and neither the dependency
   nor the `std` cache key contains the engine version; on Linux and on a macOS host building macOS, nothing else in those keys
   moved, so those entries should be hits (inferred from the diff). Reclaim the old project directories with `mcpp clean --stale`.
   Exceptions: a macOS host building a non-Apple target loses the deployment target from its command line and from the
   `min_platform_version` cache axis, and a Linux or Windows host building `aarch64-macos` gains it, so both miss once; a clang
   `*-windows-msvc` build gains the toolset and SDK in its key and misses once; on a Windows host the gcc and clang `std`
   precompile commands now double-quote their paths instead of single-quoting them, and the command is part of the `std` cache
   identity, so those `std` BMIs are rebuilt once [src/toolchain/stdmod.cppm:169,197,279-284 @ b4824697]; and on the cl.exe row a
   build whose `msvc@system` or `msvc@<toolset>` now resolves to a different toolset (item 5) runs a different cl.exe, whose version
   and identity are in both keys, so it misses once too [src/build/cache_key.cppm:400-407; src/toolchain/stdmod.cppm:156-159
   @ b4824697].
4. Run `mcpp self doctor` once on each long-lived home that has gcc payloads. A warning naming `include-fixed` files is a
   payload installed before the recipe fix; follow its reinstall line. `mcpp index update` alone does not re-clean it. Any warning
   makes `mcpp self doctor` exit 1 (2 if it also reports an error) [src/doctor.cppm:757 @ b4824697], so a CI step gating on
   doctor turns red on a home with an affected payload.
5. Windows, cl.exe row: `msvc@<toolset>` now uses an installed toolset of that version (and the machine's SDK) when there is
   one. Write `xim:msvc@<toolset>` where the payload and its pinned SDK are the point. `msvc@system` now takes the instance's
   default toolset and honours `VCToolsInstallDir`, so a developer prompt opened with `-vcvars_ver` now decides; and a toolset
   without `modules\std.ixx` no longer borrows one, so `import std` can stop being available on such a toolset.
6. Windows, clang row: the build now prints and records the MSVC toolset it compiled against (`resolution.json`
   `msvc_toolset` / `windows_sdk`). To pin one, write `[target.x86_64-windows-msvc] sysroot = "msvc@<toolset>"` - and pin the engine
   to 2026.9.24.1 or later, because 2026.9.21.3 rejects that manifest outright (§3).
7. macOS cross builds from Linux or Windows: artifacts now carry the deployment target you wrote instead of `minos 14.0`.
   Check that the value in `[build] macos_deployment_target` (or `MACOSX_DEPLOYMENT_TARGET` in the CI environment) is the one you
   want.

### 4.1 Coming from `2026.9.15.2`

Ordered by how likely each is to make a gate go red, or a working tree dirty, on the first run.

1. **Budget one cold build twice over**: the project fingerprint changes with the version (below), **and** the global dependency
   cache was orphaned by the epoch bump in 2026.9.18.1, so every dependency recompiles too. Run `mcpp cache gc` afterwards.
2. **Expect a `mcpp.lock` diff** on Linux/macOS (hash values only, 2026.9.20.1). Commit it; `--locked` legs are not affected.
   Each `git` dependency is re-cloned once (its cache directory key changed with the same hash).
3. **Openkal-style targets (graph-supplied C library)**: a package that compiled only thanks to host headers now fails with
   `file not found` (Clang) or warns `degraded` (GCC; red under `--strict`). Fix the package with `cfg(c-abi = ...)` or a
   private graph dependency - not by reverting.
4. **`--strict` legs**: new diagnostics that are warnings by default and errors under `--strict`: unknown `[package]` keys,
   `build/static-placement`, the GCC + graph-C-library warning, unknown `<dep>/<feature>` forwards.
5. **Read the `build/flag-words` warnings once.** Each names an element whose meaning changed; the usual culprit is a hand-quoted
   `-DNAME=\"x\"` or a path with backslashes. `defines = ["N=\"x\""]` now keeps its quotes, which can change generated code.
6. **Programs loading this build's C++ shared libraries** may switch C++ runtime contract (ELF) or be refused
   (`program-cxx-runtime-split`); a static package reached by two images is refused on Mach-O/PE/Android (`static-package-in-two-images`).
7. **Packaging**: `mcpp pack` now strips graph-built shared libraries and the Android program; if a downstream step expected
   debug info in them, pass `--no-strip` or `--debug-symbols <dir>`.
8. **Scripts that read `mcpp test` NDJSON**: accept the new status `built` and the fields `built` / `tests_built`; do not add them
   to `not_run`.
9. **Anything parsing `mcpp run --release --profile X`**: `--profile` now wins.
10. **Source that tests engine macros**: `__openkal__` / `__mcpp_target_<os>__` no longer exist (upper case now), and `__CYGWIN__` is
    no longer defined for Windows `presents = "posix"` graphs. Any openkal-musl pin must be **>= 0.19.0** before using an engine
    >= 2026.9.21.2 on Windows targets (see §2, 2026.9.21.1 / .2).
11. **Homes restored from a CI cache that carries only `registry/data/xpkgs`**: the declared glibc is now fetched on demand (about
    40 MB once); an offline runner must have it cached or the fixup names `xim:glibc@<version>`.
12. **`[index] auto_refresh = false` users**: a project with a custom index that has never been synced now stops and asks for
    `mcpp index update` instead of syncing implicitly.

### 4.2 Coming from before `2026.9.15.2` - the previous checklist, still valid

1. WARNING: **A full rebuild is unavoidable.** `MCPP_VERSION` is input 7 of the 11 whole-project fingerprint inputs
   [modules/toolchain-model/src/fingerprint.cppm:125], and the fingerprint hex is the directory name in
   `target/<triple>/<fp>/`. **Changing the mcpp version = a brand-new empty directory.** Gate-timing comparisons must
   pin the mcpp version or the numbers are not comparable. Afterwards, reclaim the old directories with
   `mcpp clean --stale --dry-run` then `mcpp clean --stale`, per member.
2. **`[xlings.envs]` is now a hard error.** Any manifest still carrying it fails to load. Grep for it first; this is
   the one change here that stops a build outright.
3. **`[xlings] deps` warns** and is an error under `--strict`. Migrate to `[xlings.workspace]` (§2, 2026.9.3.1).
4. **Expect new schema warnings.** `[features]`, `[runtime]`, `[target.<pred>.runtime]` and `[target.<sel>]` sub-tables
   all gained unknown-key sweeps, and unknown `cfg` keys are reported. These are real defects being surfaced — but a
   `--strict` leg goes red until they are cleaned up.
5. **Re-read every section that used to be inert and now is not**: `cfg(<layer> = …)` blocks, conditional blocks that
   contain only `[target.<pred>.runtime]`, and `[index.repos.<name>]` tables added to an already-initialised home.
   Each of these starts taking effect on upgrade; if you compensated for one (an extra `defines` line to make a
   conditional block register, say), remove the compensation.
6. **Re-check dependencies declared both unconditionally and under a selector.** The conditional declaration now
   replaces rather than loses, so the resolved variant can flip with no diagnostic.
7. **Check `path` / `git` dependency keys against the members' own `[package]` identity.** A mismatch warns once per
   declaring edge (noise in every gate run), and a no-namespace manifest reached by two differently-namespaced keys is
   refused before scanning.
8. **The global dependency cache misses wholesale across the `min_platform_version` rename.** Old entries are not
   deleted, only never hit again: run `mcpp cache gc` unless you want two generations on disk.
9. **Check test-leg exit-code handling.** `mcpp test` uses `2` for "built, never run". A gate asserting "not 1" or
   `failed == 0` is now wrong; require `rc == 0`, and read `tests_not_run` / `unrunnable_members` under `--workspace`.
10. **Check anything that parses `mcpp run`'s exit code** — it is now the program's own status for 0–124.
11. **Check anything asserting on paths under `target/`** — object addresses for out-of-package sources moved.
12. **Consider adding `--locked` to gate legs** (costs the fast path, buys a real drift assertion) and
    `[build] default_jobs` to the home's `config.toml` (a machine-level floor that also caps `mcpp test`).
13. **Any clang per-triple cfg you maintain is lost when the mcpp home is reinstalled** — rebuild it following the
    three safeguards in `troubleshooting.md` C2.
14. **Run read-only `XLINGS_HOME=<registry> xlings self doctor` once on a long-lived project-local registry**, then
    `--fix` to reinstall what it names. `2026.9.15.1` bundles the fixed xlings, but the bug it fixes (a package with no
    `install()` receiving the *entire* download directory — one measured package directory carried 1.6 GB of other
    packages' downloads) leaves **already-polluted directories polluted across the upgrade**. Disk symptom, not a red
    gate, which is why it is last; the symptom row is in `troubleshooting.md` §G.

## 5. Conflicting claims and adjudications

| # | Disagreement | Ruling | Basis |
|---|---|---|---|
| 1 | **Number of registered target rows** | **29**, in three tiers `verified` / `preview` / `planned` | The table at `docs/21-the-target-triple.md:494-525`, which is also the source `mcpp toolchain list` reads. Any count of 13/14 predates the Android, iOS, wasm, ARMv7-A and Cortex-M rows |
| 2 | **Does `self env --format json` create `$MCPP_HOME`**: the static `--protocol-version` table marks `init-mcpp-home` (source comment: "measured: six entries"), while the docs and `cmd_self.cppm` say the **JSON branch is deliberately read-only** | **Both stand**: the table is **command-level**, the doc is **sub-form-level**. **Gate on the more conservative table; to ask for paths on a fresh machine without writing anything, use `--format json`** (it reports `initialized: false`) | Each has its own file:line; different granularity is not a contradiction |
| 3 | **Total environment variables**: one count says 56 read sites including `WindowsSdkDir` / `LD_LIBRARY_PATH` / `MCPP_TOOL_<PKG>_<TOOL>`; another says 28 | **The read-site list is the more complete quantity** | The 28 came from the regex `getenv\("[A-Z_]+"\)`, which **only matches all-caps plus underscore**, missing mixed-case `WindowsSdkDir`/`WindowsSdkVersion` and the runtime-composed `MCPP_TOOL_*`. Not contradictory: read sites and literal all-caps names are two different quantities. Both numbers are from the older baseline and the set has grown since — see `env-vars.md` |
| 4 | **Does `mcpp why` do anything**: a source comment says `--target`/`--toolchain` make it a query that "builds nothing"; the side-effect table in the same file lists `exec-build-script` | **It has side effects** | The side-effect table [src/cli.cppm:1068-1070] and `docs/50-machine-output.md` both state it explicitly; "query" means it produces no build artifacts, not that it runs nothing |
| 5 | **Default profile of `mcpp test`**: commonly written up as "`mcpp test` defaults to release, `mcpp build` defaults to dev" | **Both are dev**; only `mcpp pack` falls back to release | `resolve_profile_name(..., fallback="dev")` [src/build/prepare.cppm:1014,1096-1099]; the help text now says so too |
| 6 | **Attribution of `#529`**: often recorded as "`mcpp test` re-plans the dependency closure every run" | **Corrected to**: two post-link ELF passes re-read every image in full, and the memo never hits across processes because `resolution.json` is rewritten as a fresh object each time. Fixed in 2026.8.30.2. A **second**, independent per-target cost in the same area was fixed in 2026.9.11.3 | **The observed scaling law was right; the mechanism was misattributed.** Re-measure rather than reasoning from either write-up |

### Left unadjudicated, kept marked unverified

- Whether `[resources] version-info` implies `true` when unset — the source has an unset `optional<bool>` and the
  docs do not say. `[unverified]`; this skill keeps that marker and **does not use it as fact**.
- Whether the mcpp-index-side facts in `packaging.md` (descriptor fields, lint rules, CI chain, the pinned
  `MCPP_VERSION`) still hold. They were checked on 2026-08-31 against the mcpp-index repository, which is **not part of
  this baseline**. `[unverified]` at 2026-09-16.

## 6. Known upstream defects (reportable; report first and wait for approval per policy)

| # | Defect | Status at `2026.9.15.2` |
|---|---|---|
| C1 | `--profile` help says "release (default)" while the default is dev | **Fixed.** The help reads `dev (default)` \| `release` \| `dist` \| a `[profile.*]` name |
| C2 | Unknown keys inside `[features]` are silently swallowed | **Fixed.** `kKnownFeatureKeys` [modules/manifest/src/toml.cppm:879-905] |
| C3 | The three `[build] std-module` keys are read and take effect, yet reported as "unsupported key (ignored)" | **Fixed.** They are in `kKnownBuildKeys` [:2188] |
| C4 | `cfg(c-abi = "musl")` is inert: the predicate is constant false and `std-module-flags` is not conditionable | **Fixed on both counts** (2026.9.1.1). The layer predicates evaluate, and `std-module-flags` / `private_include_dirs` are on the conditional allowlist [:3244-3252] |
| C5 | The bare-metal and project-environment pages contradict the provisioning behaviour | **Moot.** Both pages were rewritten and renumbered, and provisioning now honours `--offline` / `MCPP_NO_AUTO_INSTALL` |
| C6 | Exit code 4 (environment not ready) is undocumented | **Fixed.** SPEC-003 `docs/specs/exit-codes.md` §2 lists 0/1/2/4/70/127 as a contract. WARNING: that table is v1.0 (2026-09-01) and does **not** cover `mcpp run`'s 0–124 pass-through or `mcpp test`'s `2` — read per command |
| C7 | The filter argument of `mcpp index update [name]` only reaches project-level indices | **Documented rather than fixed**: the help now says "global repos always sync in full", because `xlings update` has no per-index mode. Not a defect to re-report |
| C8 | `docs/13-baremetal.md:40` is a broken paste | **Moot** — that file is now `docs/40-baremetal.md` and the passage was rewritten. `[unverified]` whether any comparable paste defect remains |
| C9 | The version pin for `openkal-llvm-runtime` is written four different ways across docs | `[unverified]` at this baseline => **this skill still does not hardcode that pin** |
| C10 | `specs/README.md` records a SPEC version older than the document itself | `[unverified]` at this baseline => the standing rule holds: **trust the document, not the index** |
| C11 | SPEC-002 is not linked from either user-facing README | `[unverified]`. `docs/README.md` now carries a "Look it up" reverse index and a specs section, so this may be moot |
| C12 | An `x.cppm` and an `x.cpp` with the same basename generate duplicate obj entries, causing duplicate-symbol link errors | `[unverified]` at this baseline; field-tested on the older one, unreported |

### 6.1 Open at `2026.9.21.3` (checked on GitHub 2026-09-23; source re-read where noted), re-read at `2026.9.24.1`

Upstream's own full triage, mcpp#677 (measured on 2026.9.18.3), lists three long-standing defects that still reproduce. The
source lines involved are unchanged at `b30e70c4` and again at `b4824697` (`src/ui.cppm` and `src/modgraph/validate.cppm` are not
in the 2026.9.24.1 diff; the D1 writer is still `src/build/ninja_backend.cppm:3206`), so treat them as open here too. D4 is fixed in
2026.9.24.1. D5 and D6 were not re-checked on GitHub for this pass:

| # | Defect | Practical consequence |
|---|---|---|
| D1 | A fast-path hit never rewrites `compile_commands.json`; its only writer is inside the ninja backend [src/build/ninja_backend.cppm:3206 at `b30e70c4`] (mcpp#397 C-1) | `git clean -fd` or deleting the file, then `mcpp build`, prints `Finished dev in 0.00s` and leaves no database - clangd goes blind. Touch a source or use `mcpp emit build-database --spec compile-commands` |
| D2 | `--no-color` is a no-op on a TTY: `disable_color()` clears the flag but the first output re-detects from `is_tty()` [src/ui.cppm:239] (C-3) | Use `NO_COLOR=1` or `MCPP_NO_COLOR=1`; pipes were never coloured, which is why CI never saw it |
| D3 | `[modules].exports` validation never fires for a namespaced package: it compares the scanner's qualified `ns.name` against the bare `package.name` [src/modgraph/validate.cppm:98] (C-4) | A missing export is caught only when a consumer fails to find the module |
| D4 | mcpp#685: cross-compiling to `aarch64-macos` from a non-Apple host ignores `macos_deployment_target` and `MACOSX_DEPLOYMENT_TARGET` (always `minos 14.0`, no rebuild on change) | **Fixed in 2026.9.24.1** (§2). On an older engine, check `LC_BUILD_VERSION` of the artifact or build on a macOS host |
| D5 | mcpp#674: Windows `presents = "posix"` graphs - `__unix__` is defined but 18 `compat.*` packages still fail (engine vs upstream-code assumptions, under discussion) | Do not read a green Linux column as evidence for the Windows openkal column |
| D6 | mcpp#666 / #667: self-hosting mcpp - a Clang-built mcpp SIGSEGVs in ELF runtime inspection; GCC self-host ICE importing `mcpp.targetside` under parallel build | Matters only when building mcpp itself (`contributing.md`) |

WARNING: when filing upstream, do not include your project's internal package names, file paths, test names, or
internal tracker ids if the project is not public.

## 7. docs `zh/` divergence

`docs/zh/` mirrors the English tree file for file, and CI enforces **structural parity of headings** between each pair
(`check_docs_structure.sh` plus rule 3 of `check_docs_style.sh`), so a missing section shows up as a red build rather
than as silent drift. What CI cannot check is whether the prose says the same thing.

**Standing rule, unchanged: cite the English page.** The detailed pair-by-pair divergence table this section used to
carry was measured against the pre-renumbering tree and is not re-verified at this baseline — `[unverified]`, and
therefore removed rather than left to look current.

Three things that do still hold and are worth keeping:
- **The numbering is shared, so the §1 map is the zh map too.** `docs/zh/` mirrors the English tree file for file with the
  same band numbers (only `docs/specs/` has no twin; it exists once, in Chinese). A pre-2026.9.9.1 zh link is dead the same way its English twin is —
  `docs/zh/13-baremetal.md` → `docs/zh/40-baremetal.md`, `docs/zh/20-heterogeneous-builds.md` →
  `docs/zh/42-heterogeneous-builds.md`, both 404 today (GitHub contents API, 2026-09-16). Upstream conversation still carries
  the old spellings: `mcpp#403`'s maintainer comment links the first. Map, then cite the **English** page.
- **mtime is not a staleness signal in the mcpp repo** — EN/ZH pairs share an mtime; all divergence is at content level.
- **The spec is normative, the docs are not** [docs/README.md]. "How exactly do `[dependencies]` selectors match"
  routes to `docs/specs/package-identity.md`, not to a usage page. Respect the implementation-status markers in
  `docs/specs/README.md`: a clause marked not-yet-in-effect is not a fact about the current engine.

## 8. Corrections to commonly held beliefs

| # | Original statement | Correction |
|---|---|---|
| A1 | "The default profile is release" | **It is dev**, for `build`/`test`/`run`/`emit build-database`; only `pack` falls back to release. CI and performance measurement must pass `--profile release` explicitly or pin `default-profile`. WARNING: the follow-on claim "and the `--help` text lies about it" is **itself stale** — that was fixed; do not repeat the correction |
| A2 | "mcpp has no hooks" | **Reason wrong, conclusion right.** Corrected reason: `build.mcpp` + `mcpp::action` require output filenames to be known at prepare time (content-hash artifact names cannot be declared); `[hooks]` is a notification mechanism, has no authority over build success or failure, and receives no `MCPP_*` context |
| A3 | "The root cause of #529 is re-planning the dependency closure" | See §5 row 6. Both known causes are fixed; re-measure rather than reasoning from either write-up |
| A4 | "Filtering by test name causes collisions" | **Precisely**: it is **substring containment**; cross-package collision requires `--workspace`; there is **no `--exact`**; and **filtering does not reduce planning or build cost at all**. To change *which* tests exist, use `[test] discover` |
| A5 | "Clear the cache before switching between host and musl" | **Can be retracted** (all three cache layers were fixed, with a targeted musl e2e `283_run_target_flag_owns_its_cache_slot.sh`) |
| A6 | "Clear the cache because dependency header sets get cross-picked" | **Keep** (only the opt-in half was fixed; the `includeDirsAfter` gap remains) |
| A7 | "MCPP_HOME cannot be relocated (embedded absolute paths)" | **Reason must change**: there really are four classes of absolute path, but a self-healing path exists (fixup stamps keyed by content fingerprint, re-run at every build seam that resolves a payload). The real blockers are the **patchelf bootstrap cycle (silent degradation), total cache loss, and unrecoverable symlink-inherited payloads**. Operational conclusion unchanged: install fresh in place. Upstream's position is that the home is a rebuildable cache — when it must move, drop the registry and let the next build re-fetch |
| A8 | "mtime staleness trap" | **Keep as-is**, and add two things: `Finished dev in 0.00s` is the observable signature of a fast-path hit, and the **host-tool store keys a `path` tool by a stat imprint that includes mtime**, so the same trap applies there |
| A9 | "You must prefix commands with MCPP_HOME" | **Reason updated again**: tool provisioning is now gated by `--offline` / `MCPP_NO_AUTO_INSTALL`, so the reason is no longer "there is no switch" but "otherwise it is the shared home's disk, and provisioning spans the whole dependency graph" |
| A10 | `MCPP_INDEX_MIRROR=GLOBAL` | **Drop it** — still zero hits anywhere in the mcpp source at this baseline |
| A11 | "`[build] default_jobs` in the home's `config.toml` does nothing" | **Retracted (2026.9.11.2).** It has a reader, it is the only rung that can carry a machine fact, and it **also bounds `mcpp test`'s concurrency**. `MCPP_JOBS` still outranks it, so an explicit cap on the command line is unaffected |
| A12 | "`mcpp pack --format` accepts `tar` or `dir`" | **Retracted (2026.9.11.1).** Those two are engine-owned; any other name is dispatched to a package in the resolved graph, so an unknown value is refused after resolution and names what is actually available |
| A13 | "`mcpp clean` is all or nothing, so old fingerprint directories can only be removed by hand" | **Retracted (2026.9.6.1).** `mcpp clean --stale` exists; see `../SKILL.md` §8 for the three rules |
| A14 | "The bare-name -> `compat` fallback was removed in 2026.9" | **Not true yet** at 2026.9.21.3 (`allowLegacyBareDefault=true` still passed at src/pm/package_fetcher.cppm:726,764; `docs/specs/package-identity.md` §4.2.1 still says "removed in 2026.9"). Deprecated and warned about, still present - and since 2026.9.16.1 the index-refresh decision walks it too |
| A15 | "`mcpp.lock` hashes are FNV-1a" (as the `fnv1a:` prefix says) | **Only true since 2026.9.20.1.** Before it they were `std::hash`, FNV-1a only on MSVC |
| A16 | "`mcpp build --target <t>` exits 0, so the member builds for `<t>`" | **Not for a member whose code lives in `tests/`** - `build` compiles the package, not its tests. Use `mcpp test --target <t> --no-run` (2026.9.21.3) |
| A17 | "`__CYGWIN__` identifies a PE target presenting POSIX" | **Withdrawn in 2026.9.21.2.** Use `__MCPP_TARGET_WINDOWS__`; a borrowed name means what its lender's history made it mean (upstream code reads `__CYGWIN__` as "Win32 is available") |
| A18 | "`msvc@<toolset>` always installs the payload, identically on every machine" (docs/20 before 2026.9.24.1) | **Changed in 2026.9.24.1.** An installed complete toolset of that version is used first, with the machine's SDK; `xim:msvc@<toolset>` is the payload-only spelling |
