# Cross-compilation and targets

Moved out of `SKILL.md` to keep it short; section numbers there still point here.

- **Triple syntax is `<arch>-<os>[-<env>]`, with no vendor segment. `env` means different things on different operating systems**: linux
  -> C library (`gnu`/`musl`, and **`android`, which sits in the same slot** - so `os = "linux"` predicates *do* match Android rows while
  `[package] platforms = ["linux"]` does *not* cover them); windows -> object ABI (`gnu` = Itanium / `msvc`); none -> object format
  (`elf`); ios -> device vs simulator (`sim`); **macos and emscripten carry no env segment at all** [docs/21-the-target-triple.md:41-68].
  Omitting the third segment is legal and **does not change identity** (same fingerprint; the second run is a cache hit). WARNING: but
  **writing the segment opts out of completion** - `--target aarch64-linux-gnu` still hits the refusal on rows marked `planned`, and a
  bare `aarch64-linux` is **never** completed to Android. A four-segment spelling such as `wasm32-unknown-emscripten` (what `em++` hands
  its own clang, and what rustc's table says) is accepted and normalised back to three.
- **The registered target rows are the entire vocabulary**, and there are now **29 of them** across three tiers -
  **`verified` / `preview` / `planned`** [docs/21-the-target-triple.md:494-525]; `mcpp toolchain list` is the same table.
  `planned` rows are refused rather than attempted; `aarch64-linux-gnu`, `x86_64-macos` and `riscv64-linux-musl` are the current ones.
  The escape hatch is an explicit `[target.<triple>] toolchain` - except on **capability-pinned** rows, where only that row's own
  toolchain can emit the target at all (wasm, Android, and PE+musl are such rows) and a different family is refused before resolution.
- **Two cross paths**: the **payload path** (gcc payload; `host_can_serve` decides whether this machine can serve it) and the **graph path
  / openkal** (the system layer enters the dependency graph as a source package, one Clang reaches every target, and the project side only
  writes `openkal-llvm-runtime = "..."` plus `[toolchain] default = "llvm@..."`) [docs/24-openkal-cross.md]. WARNING: **no path or package
  named `llvm-musl` exists in the source** - grepping the whole repo only hits an unimplemented design document.
- Android rows additionally need `[target.<triple>] min_api_level`: bionic refuses an unversioned triple outright, the level rides the
  effective triple handed to clang while the canonical triple stays `aarch64-linux-android`, and **the level enters the fingerprint**
  (two levels are two ABIs and never share a build directory).
  => The non-desktop rows in full - wasm, Android and iOS, with the capability-pin refusals, the `[target.<sel>.abi]`
  `threads`/`exceptions` switch, the wasm artifact contract and `pack` / `run --format` - are
  `references/heterogeneous-and-baremetal.md` §5; freestanding targets and board-support packages are its §6.
- **The macOS deployment target is a property of the target, not of the host.** Resolution is `MACOSX_DEPLOYMENT_TARGET` >
  `[build] macos_deployment_target` > `14.0` on every host, and it applies exactly when the target's `os` is `macos` - to the
  effective triple (`arm64-apple-macos11.0`), `-mmacosx-version-min`, the `std` module precompile, the fingerprint and the
  `macos.deployment-target` fact - so `--target aarch64-macos` from Linux or Windows honours it and a non-macOS target never
  carries it [modules/platform/src/macos/macos.cppm:125-132; src/toolchain/hostflags.cppm:534-537; src/build/prepare.cppm:2111-2113,
  13007-13013; docs/04-mcpp-toml.md:711-714, all @ b4824697]. Only `build.mcpp`'s own compile follows the host, because it runs there.
  A real `aarch64-macos` build still needs the macOS SDK; `--configure-only` with an explicit `[target.aarch64-macos] toolchain =
  "llvm@..."` needs none (upstream e2e `746_macos_deployment_target_is_target_keyed_not_host_keyed.sh`). Engines before 2026.9.24.1
  ignored both inputs on a non-Apple host (mcpp#685); check `LC_BUILD_VERSION` with `llvm-objdump --macho --private-headers` when the
  engine version is not pinned.
- **On an MSVC-ABI row (`*-windows-msvc`) `[target.<triple>].sysroot` names the MSVC toolset** (its STL, CRT and the Windows SDK that
  follows it): `msvc@system` (the default when absent), `msvc@<toolset>` or `xim:msvc@<toolset>`; anything else is refused when the
  manifest is parsed [modules/manifest/src/toml.cppm:676-701 @ b4824697]. With clang the choice is made once and handed to the driver
  as `-Xmicrosoft-*` on compile, link and `std` precompile; with cl.exe a sysroot naming a different toolset than the compiler is
  refused. Details and the selection order are in `references/mcpp-toml.md` §6.
- WARNING: **openkal dependencies must be target-scoped**: putting them in a plain `[dependencies]` drags the **host graph** into openkal
  too. The correct form is `[target.x86_64-linux-musl.dependencies]` (configure-time evidence: host graph openkal=0, musl graph openkal=4)
  [field-tested 2026-08-27].
- **`--no-default-config`**: the clang payload's `clang++.cfg` contains an **unconditional**
  `-Wl,--dynamic-linker=.../ld-linux-x86-64.so.2`; without dropping that flag you produce "link succeeded, build reported success,
  PT_INTERP is x86-64" in RISC-V firmware [src/build/flags.cppm]. mcpp adds it on every invocation itself. WARNING: but the flag
  **changes target features by itself**, so `std.pcm` and ordinary TUs end up with mismatched features - upstream has recorded this and
  **has not fixed it**.
- **When a layer comes from the dependency graph, the host's copy of it is closed off (2026.9.17.3, mcpp#662).** A graph-supplied
  `c-abi` adds `-nostdlibinc` (compiler resource headers stay, system/C-library directories go) and a graph-supplied `c++-abi` adds
  `-nostdinc++`, each judged on its own layer, to C, C++, assembly, the dependency scan and the `std` module precompile. Before, the
  clang driver still searched the host, so a package could compile on a machine that happened to have a matching SDK installed and
  link two C libraries' declarations. => After upgrading, a package that fails with `file not found` on an openkal-style target was
  leaning on the host; mcpp now appends advice naming the C library, and the fixes are `cfg(c-abi = "...")` adaptation or a platform
  dependency brought in through the graph with `visibility = "private"`. **GCC has no equivalent single flag**: its command line is
  unchanged and the build prints a `degraded` warning naming the C library and the compiler (an error under `--strict`).
- **The C library layer can declare the environment it presents (2026.9.18.1)** - `[c-abi] presents / data-model / wchar / builtins`,
  writable only by a package that provides `mcpp:c-abi=<impl>`. On Windows, `presents = "posix"` changes the **compile** `--target=` to
  `x86_64-pc-cygwin` while the resolved triple, output directory and **link** line stay `x86_64-windows-gnu` - a `compile_commands.json`
  showing a cygwin triple is this, not a bug. The declaration is verified by a `-E -dM` probe and mismatches fail the build; the
  realised environment enters both the fingerprint and the global cache key. Full rules in `references/mcpp-toml.md` §17 and
  `references/heterogeneous-and-baremetal.md` §6.10.
- **Macros the engine defines (`src/toolchain/predefines.cppm`, a contract tested in both directions)**: `__MCPP_TARGET_<OS>__` on every
  target-side unit, spelt from the triple's `os` field upper-cased (`__MCPP_TARGET_LINUX__`, `__MCPP_TARGET_WINDOWS__`,
  `__MCPP_TARGET_NONE__`) since 2026.9.21.1; `__OPENKAL__` when the resolved `kernel-abi` interface is `openkal`, since 2026.9.18.1;
  and `__unix__` where a `[c-abi]` realisation supplies it (macOS and freestanding). WARNING, spelling history: the first two shipped
  lower-case (`__mcpp_target_<os>__` in 2026.9.21.1 only, `__openkal__` in 2026.9.18.1 through 2026.9.21.1) and were upper-cased in
  **2026.9.21.2** with no transition; `__CYGWIN__` / `__CYGWIN32__` were defined under the Windows `presents = "posix"` substitution
  until 2026.9.21.1 and are explicitly undefined from 2026.9.21.2. Use `__OPENKAL__` only to decide whether to call `kal_*`, never to
  pick a header or infer the platform - that is what `cfg(c-abi = ...)` / `cfg(kernel-abi = ...)` in the manifest are for.
- **`[target.<sel>.build]` can condition on the resolved target side, not just the triple.** Five layer names are predicate keys:
  `compiler` / `compiler-runtime` / `kernel-abi` / `c-abi` / `c++-abi`, combinable with triple keys under `all`/`any`/`not`.
  WARNING: these sections used to be parsed and then **silently dropped**, so a package could build successfully against the wrong C
  library. They now take effect - re-read every `cfg(c-abi = …)` section you wrote against an older engine and confirm its contents are
  still what you want, because it was inert when you wrote it.
  WARNING: a layer predicate **cannot select dependencies** (the layers are resolved *from* the dependency graph); such a section is
  reported and ignored. Use a feature or a triple key.
  WARNING: the `c-abi` layer reports the **library name**, not the triple's env segment. They coincide on musl and diverge on gnu (Linux
  asks for `glibc`; on Windows the toolchain's MinGW form has a UCRT C runtime), and machine output's `layers[].interface` changed value
  accordingly. A script matching the literal `gnu` needs updating; `musl` is unaffected.
- **Three defences for per-triple clang cfg** (a field workaround; drop any one and you can repeat the false report) [field-tested
  2026-08-30]: (1) **delete every `compile_commands.json` before harvesting `-I`** - that file **accumulates across configurations** and
  is not a snapshot of this run; (2) after harvesting, **filter by the currently resolved versions and assert "exactly one version per
  package"** before writing the cfg (measured: after deleting the stale files the count dropped from 36 entries to 18, exactly half); (3)
  **prove the version before running tests**, and attach `mcpp.lock`. Also: **write only `-clang++.cfg`**; the bare-triple variant poisons
  C compilation.
  WARNING: **lesson**: "the signature is bit-for-bit identical" is not evidence that a fix was ineffective, it is evidence that **it is
  the same binary**.
  WARNING: mcpp itself writes `bin/<driver>.cfg`, not `<triple>-*.cfg`, and **only rewrites files that already exist; it never creates
  them** [src/toolchain/post_install.cppm:276,366-376] - so per-triple cfg files are hand-written and are lost whenever the mcpp home is
  reinstalled.
