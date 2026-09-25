# Reference: mcpp.toml full field reference

> Source of truth: `modules/manifest/src/toml.cppm` (key names and validation) + `modules/manifest/src/types.cppm` (types and defaults) +
> `src/project.cppm` (workspace inheritance) + `docs/04-mcpp-toml.md` / `docs/05-dependencies.md` /
> `docs/06-features-and-capabilities.md` / `docs/08-testing.md` (effective defaults and semantics), with the normative rules in
> **SPEC-004 `docs/specs/manifest-semantics.md`**. Baseline `main @ 2fc7b5b0` (version `2026.9.15.2`). Date 2026-09-16.
> The `macos_deployment_target` row of §3, the `sysroot` row of §6 and the `[toolchain]` entry of §14 were re-read at
> `main @ b4824697` (`2026.9.24.1`, 2026-09-24, source and docs only); their citations say `@ b4824697`.
>
> **Read SPEC-004 first when the question is structural** ("what shapes may a conditional section take", "which tables are the resolution
> axes", "how is a name allowed to be spelled"). It did not exist at this skill's previous baseline, and it is the authority its own
> authors cite; this file follows it rather than re-deriving the rules.

## 0. The three fates of an unknown key (read this first)

| Section | Unknown key | Evidence |
|---|---|---|
| `[build]` | schema **warning** (`--strict` promotes it to error) | toml.cppm:2173-2205 |
| `[targets.<n>]` | schema warning | :1304-1330 |
| `[target.<triple>]` / `[target.<pred>.build]` | schema warning; a **sub-table** mcpp does not read is reported separately | :2914-2950 / :3244-3258 |
| `[features.<f>]` | schema warning | :879-905 |
| `[runtime]` / `[target.<pred>.runtime]` | schema warning (`[runtime.<capability>]` sub-tables are a channel, not typos, and are skipped) | :2405-2418 / :3160-3170 |
| `[test]` | schema warning; a non-array or empty-string `discover` is an **error** | :2509-2530 |
| `[hooks]` | schema warning; but **a key given to the wrong event is an error** | |
| `[workspace.package]` | **parse-time ERROR, the whole manifest fails to load** | |
| `[workspace.build]` | **parse-time ERROR** | :3551-3556 |
| `[toolchain]` | **no unknown-key validation at all** (open platform -> spec map) | |

Rationale for the hard rejection in `[workspace.*]`: "A key in a table whose entire purpose is to propagate is either propagated or reported;
silently dropping it produces a workspace that looks configured and is not."

Two holes this table used to record are **closed**, so delete any note repeating them: `[features]` was the last structured section with no
unknown-key sweep, and `[build] std-module` / `std-compat-module` / `std-module-flags` were read-and-effective while being reported as
unsupported. Both fixed.
=> The practical consequence of closing them: **upgrading surfaces new schema warnings** in manifests that were quietly wrong, and a
`--strict` gate leg goes red until they are cleaned up. Those are defects being found, not regressions.

WARNING: **`[workspace.build] ios_deployment_target` is *read* [:3548-3549] but absent from the `kKnown` array the sweep checks against
[:3551-3556], so writing it in `[workspace.build]` is a hard error** - the loader consumes the value and the sweep then refuses the key.
A note on the mechanism: this one diagnostic is a **hand-written string literal** [:3573-3579] that currently lists exactly the same 14
keys as `kKnown` - `ios_deployment_target` is in neither. Every *other* unknown-key sweep at this baseline builds its message by looping
the array it checks ([:2196-2215] for `[build]`, whose comment records that a third hand-written copy had already drifted; [:3157-3161]
"ONE LIST, USED BY THE CHECK AND PRINTED BY THE MESSAGE"), so the old blanket advice "never trust the diagnostic" is a **retired** hazard,
not a live one.

## 1. `[package]`

| Field | Type | Default | Scope | Evidence |
|---|---|---|---|---|
| `name` | string | **required** | package | toml.cppm:556-559 |
| `namespace` | string | empty (inferred from name) | package | :564; types.cppm:39 |
| `version` | string | **required** | package | :566-569 |
| `standard` | string or int | `"c++23"` | **workspace-inheritable** | :580-601 (int form :586-601), `[language] standard` mirror at :607-613; types.cppm:41 |
| `description` / `license` / `repo` | string | empty | workspace-inheritable | :571-573 |
| `authors` | array\<string\> | empty | workspace-inheritable | types.cppm:70 |
| `platforms` | array\<string\> | empty | package (CI matrix hint) | types.cppm:72 |
| `provides` / `requires` | array\<string\> | empty | package (`mcpp:<layer>[=<impl>]`) | types.cppm |
| `exclusive` | array\<string\> | empty | declares this package the sole provider of a capability. Two packages providing one capability with at least one `exclusive` are refused **when the capability is bound**, before anything compiles (`exclusive-capability`). Naming a capability this package does not `provide` is a schema warning | toml.cppm:993-1005 |
| `accelerators` | array\<string\> | empty | mirrors `platforms`: an intent statement and CI-matrix hint shown by `mcpp why`, **never a gate** | toml.cppm:576 |
| `requires_abi` | inline table | empty | e.g. `{ threads = true }` - what this package needs of the artifact's ABI; unmet is refused before compilation | toml.cppm:972 |
| `std-module` / `std-compat-module` | string | empty | **the `[build]` spelling wins** | |
| `c-environment` | string, only `"platform"` | empty | 2026.9.18.1+: this package's own units compile in the **triple's** C environment rather than the one a `[c-abi]` block realises for the graph (§17). **Inferred** for any package whose `provides` names `mcpp:kernel-abi=<impl>`; an explicit value wins over the inference, and there is no way to write "not platform" | toml.cppm:1441-1446 (known-key list) |
| `metadata` | table of tables | empty | 2026.9.16.1+: `[package.metadata.<tool>]`, kept verbatim and **never interpreted**; reaches the root build program through `mcpp::graph_file()`. Paths in it are resolved by the reader against the package's `manifest_dir`. Older engines ignore it, so it needs no engine floor | docs/04; docs/30 |

*changed in 2026.9.16.1*: **`[package]` has a known-key sweep** - anything outside `accelerators authors c-environment description
exclusive license metadata name namespace platforms provides repo requires requires_abi standard std-compat-module std-module
std-module-flags version` [toml.cppm:1441-1446 at `b30e70c4`] is a schema warning, an error under `--strict`. Tool data that used
to be parked as an extra `[package]` key belongs in `[package.metadata.<tool>]`.

`standardDeclared` is an internal bool: it distinguishes "the author wrote `standard`" from "this is the default value". The two are
byte-identical but need opposite handling, and inheritance of `[workspace.package] standard` depends entirely on it.
Both spellings of `standard` (string and bare integer) are accepted.
WARNING: **`platforms` now has six legal values** - `linux | macos | windows | ios | android | emscripten`. A platform name is the triple's
`os` **unless an `env` names a platform itself**, so Android rows (`os = "linux"`, `env = "android"`) are **not** covered by `linux`, and
the Web row is `emscripten`, not `web`. This is not a tightening: values outside the old three-word list already only warned.
WARNING: a C++-layer provider (one supplying `hosted-standard-library` or `mcpp:c++-abi=`) that declares `[package] standard` compiles its
own non-module implementation units at **that** level while module units stay at the graph's level - which is how a `c++20` program can use
a `c++23` standard-library package. The level enters the dependency cache key, so such dependencies rebuild once after adopting it. A
provider that does not declare it is byte-for-byte unchanged.

## 2. `[language]` (legacy; after M5.0 `standard` moved to `[package]`)

`standard` (default `"c++23"`) / `modules` (`true`) / `import_std` (`true`) [toml.cppm:607-616]. `[language] standard` is only consulted when
`[package] standard` is absent [:610].

## 3. `[build]` - closed whitelist of 30 keys (unknown key is only a warning)

Whitelist verbatim [toml.cppm:2616-2632 at `b30e70c4`; it was 29 keys at 2026.9.15.2, `platform-dependencies` is the addition]:
```
accel, allow_host_libs, bmi_schedule, build_program_timeout, c_standard,
cache, cflags, cxxflags, cxx_runtime, default-profile, defines,
dependency_linkage, dialect_cxxflags, flags, include_dirs,
include_dirs_after, private_include_dirs, ios_deployment_target,
jobs, ldflags, macos_deployment_target, module_extensions,
platform-dependencies, profile,
sources, static_stdlib, target,
std-compat-module, std-module, std-module-flags
```
`platform-dependencies = "refuse"` (the only accepted value; absent = allow) fails the build when any package in the graph declares
`provides = ["platform-sdk"]`, reason `platform-dependency` (2026.9.18.1+, §17).
The **element syntax** of `cflags` / `cxxflags` / `asmflags` (and `flags[].cflags` etc.) is SPEC-004 §8 since 2026.9.17.1 - see
`../SKILL.md` §5 for the rules. A `defines` entry is one value and is **not** split.

| Field | Type | Effective default | Notes |
|---|---|---|---|
| `sources` | array\<glob **or table**\> | conventional glob (below) | WARNING: **`sources = []` is not the same as omitting the line** (the former means compile nothing); `sourcesDeclared` tells them apart. An entry may also be `{ glob = "…", accel = "…" }` - see `accel` below, and note that a schema assuming "array of strings" rejects valid manifests |
| `accel` | string | empty | which device backends and architectures this build targets, e.g. `"cuda12.9+{sm_89}, vulkan1.2"`. `--accel` overrides it and `--no-accel` asks for none. **Comma separates entries in the set; a space separates modifiers within one entry** - `"cuda12.9+{sm_89}, vulkan1.2"` selects both, the space-only spelling selects only cuda. A per-glob constraint matching no file is **refused by name**: an empty match is a typo or a moved directory, not a no-op |
| `ios_deployment_target` | string | the located SDK's version | iOS counterpart of `macos_deployment_target`. Also a `[workspace.build]` key *in the reader* - but see the §0 warning, it is missing from that table's known-key array |
| `cxx_runtime` | string or table | empty | `self-contained`\|`toolchain-coupled`\|`host-coupled`; the table form allows per-role values, and **`{ shared = "self-contained" }`** opts a dependency's C++ shared library into a private copy of a package-supplied C++ runtime. Without it, that situation is refused before compilation (`shared-library-cxx-runtime`). WARNING: the refusal spells out the price - with one copy per image, a `std::runtime_error` thrown by the shared library is **not** caught by that class in the program |
| `cflags` / `cxxflags` / `ldflags` | array | empty | WARNING: a `-std=` inside `cxxflags` is **a hard error**, you are told to use `[package].standard` [:2219-2224; the `[targets.<n>] cxxflags` sibling guard is at :1289-1296] |
| `defines` | array | empty | **package-level macros, reaching every TU including module interface units**, therefore they participate in P1689 scanning |
| `dialect_cxxflags` | array | empty | **graph-global**, see §11 |
| `flags` | array\<table\> | empty | per-glob flags, **ordered, later wins**. Subkeys are closed: `glob` (required) / `cflags` / `cxxflags` / `asmflags` / `defines`; an unknown key is a **hard error** |
| `include_dirs` | array | empty | relative to package root |
| `include_dirs_after` | array | empty | emitted as `-idirafter` |
| `private_include_dirs` | array | empty | **must be a subset of `include_dirs`** (not a second list; the reason is ordering); marks which ones are not passed to consumers. 2026.8.27.1+ |
| `c_standard` | string | **`c11`** (docs) | initial value in source is empty |
| `target` | string(triple) | empty | project default build target (equivalent to cargo `build.target`) |
| `bmi_schedule` | string | `"auto"`, **and auto currently means OFF** | `auto`\|`on`\|`off`, **exact match, no case folding, no synonyms** |
| `jobs` | string or int | **`"auto"`** (docs) | kept as text so that `"auto"` survives to the actual build |
| `default-profile` (alias `profile`) | string | empty means the global **`dev`** | `mcpp pack` is the exception: `--profile` > this key > `release` |
| `cache` | string | `"global"` | `global`\|`local`\|`off`; unknown value is a warning |
| `dependency_linkage` | string | empty = `"static"` | `static`\|`shared`; may also be given per profile. It sits **second** in the four-rung link-form ladder: the root's `linkage` on the dependency edge > this > the package's own `[targets.<n>] linkage` > `static`. WARNING: targets whose C library is statically linked (**musl by default**) reject `shared` - and drop the package default **with no warning**, because nobody asked for it |
| `static_stdlib` | bool | **`true`** | |
| `allow_host_libs` | bool | `false` | escape hatch for the hermetic-link check; `MCPP_ALLOW_HOST_LIBS=1` is the one-shot equivalent. WARNING: **it only relaxes the pre-link check, it does not suppress post-link physical impossibility** |
| `macos_deployment_target` | string | **`14.0`** built in | priority: `MACOSX_DEPLOYMENT_TARGET` env > this key > 14.0. Stated to the graph as the fact `macos.deployment-target`, which a dependency may require a floor on. Decided by the **target**, on any host: a target whose `os` is `macos` gets it in the effective triple, `-mmacosx-version-min`, the `std` precompile and the fingerprint; any other target never sees it [modules/platform/src/macos/macos.cppm:125-132; src/build/prepare.cppm:2111-2113 @ b4824697] |
| `module_extensions` | array | empty | extra module interface extensions; the only built-in is **`.cppm`**. `.ccm`/`.cxxm`/`.ixx` are **not** built in |
| `build_program_timeout` | int (seconds) | **600**, `0` = unlimited | the `optional<int>` is load-bearing (a plain int defaulting to 0 would drop the run limit for every project that omits the key) |
| `std-module` / `std-compat-module` / `std-module-flags` | | empty | now correctly on the known-key list; `std-module-flags` is also conditionable |

**Conventional default source glob** (injected when `sources` is absent) [modules/source-kind/src/source_kind.cppm]:
```
src/**/*<each module interface extension>   # at least .cppm, built in
src/**/*.cpp   src/**/*.cc   src/**/*.c
src/**/*.S     src/**/*.s    src/**/*.asm
```
WARNING: **`.cxx` has never been in the conventional defaults** - the source comment says adding it would be "a behavioral change wearing a
refactor's clothes" [:497-500, inside `default_source_globs`].

WARNING: **every file matched by `sources` must produce an object that gets linked** [docs/04-mcpp-toml.md]. A file whose extension is neither in
the built-in set nor in `module_extensions` is **rejected**, naming the file, the extension and the key - it is not ignored. The symptom
otherwise is `undefined reference` to a module's mangled symbols. Headers go to `include_dirs`; `.rc` goes to `[resources]`.
WARNING: **`.asm` is x86 only** (hard error elsewhere), **`.S` is unavailable on MSVC**, and `.asm` means **NASM syntax** (MASM sources must
be excluded with `!`). If nasm >= 2.16 is not found the build **fails hard** - assembly is never silently skipped [docs/04-mcpp-toml.md].
WARNING: **`module_extensions` needs a version floor** [docs/11-publishing-a-library.md]. Most `[build]` keys degrade cleanly; this one does not - an older
mcpp warns, ignores, and then **compiles those files as ordinary TUs, i.e. one wrong build**. Module interfaces produce no BMI, the failure
surfaces later, and it names neither that key nor that file.

## 4. `[profile.<name>]`

`opt` (default `"2"`) / `debug` (false) / `lto` (false) / `strip` (false) / `dependency_linkage` (inherits `[build]`) [toml.cppm:710-723]. The
internally parsed knobs have the same names [types.cppm:1683-1688].
WARNING: `[profile.*].strip` adds `-s` to the **link** (it cannot touch static archives and cannot split); `[pack] strip` governs what goes
**into the package** [docs/10-pack-and-release.md].

## 5. `[targets.<name>]` - build artifacts (closed whitelist)

Whitelist of 11 keys [toml.cppm:1304-1308]: `kind`, `linkage`, `main`, `soname`, `exports`, `cflags`, `cxxflags`, `defines`,
`required_features`, `windows_entry`, `windows_subsystem`.

| Field | Notes |
|---|---|
| `kind` | the user may write `bin` \| `lib` \| `shared` \| **`app`**; the source enum also has `TestBinary` (auto-discovered, not user-written). **`kind = "lib"` is not a linkage constraint, it is the default value** - "absence of a statement is not a statement" |
| `linkage` | `static` \| `shared`. **A default, not a constraint** - unlike `kind = "shared"`, a consumer that states a form explicitly is honoured, and overriding prints one `Linkage` information line rather than being a degradation (`--strict` accepts it). Refused alongside `kind = "shared"` in one table, and on a program target. Engines before 2026.9.15.2 report it as an unsupported key - **silently, for a dependency** - and link static, so a package using it must state an engine floor |
| `main` | entry source file of a binary/test |
| `soname` | shared library ABI name; rejected only on **non-library** targets. ELF shared libraries now default their SONAME to the file name (placed before `$ldflags`, so a project's own `-soname` still wins) |
| `exports` | the artifact's published symbol set: a symbol-pattern file, or an inline array. Rendered per platform as an ELF version script / `-Wl,-exported_symbols_list` / a PE `.def`. Omitting it means "export everything". It is a **link-time** property only and implies no compile-time hidden visibility; `-fvisibility=hidden` still goes through `[build] cxxflags`. Symbol versioning (`foo@@LIB_1.0`) is out of scope |
| `windows_subsystem` / `windows_entry` | `console` (default) \| `windows`; `main` (default) \| `wmain` \| `WinMain` \| `wWinMain`. **Fields, not link flags**, because the correct flag depends on the ABI (MSVC renders `/SUBSYSTEM:` + `/ENTRY:<entry>CRTStartup`, GNU renders `-mwindows` / `-municode`). They render nothing on ELF/Mach-O/wasm - byte-identical artifacts - reach only the target that declares them, and are refused on library targets |
| `cflags`/`cxxflags`/`defines` | WARNING: **they apply only to the entry source this target owns exclusively (its `main`)**, never to the shared module/implementation objects (compile-once model) |
| `required_features` | **a build gate**: the target is emitted only when every listed feature is active; **it does not activate features**. The gating criterion is the **root's** active feature set |

Warning text: "For config that must affect shared code, split into a workspace member or use `[features]`; for a whole-build mode use
`[profile.*]`".

`kind = "app"` means "the thing a user launches". On ELF/PE/Mach-O and `wasm32-emscripten` it is byte-identical to `bin`; on
`*-linux-android` it is a shared object (`libmyapp.so`, loaded by a Java process). `main` still names one translation unit on every row,
`windows_subsystem` / `windows_entry` apply exactly as they do to `bin`, and `mcpp pack` treats it as a program target.
*compatibility:* engines at or below 2026.9.12.2 reject the value by name - `targets.myapp.kind must be 'bin', 'lib' or 'shared'`.

**What `mcpp pack` packs is decided by `kind` and nothing else**: `bin`/`app` gives an application bundle; `lib` a static library package;
`shared` a dynamic library package. There is **no `--lib` flag and no `--artifact static|shared`** - "kind is already where mcpp records what
an artifact is; a flag would be a second place to say it" [docs/12-binary-distribution.md].

## 6. `[target.<triple>]` - per-target overrides

Three vocabularies, each with its own sweep [toml.cppm:2921-2930]:

**Scalars (5)**: `cxx_runtime`, `linkage`, `min_api_level`, `sysroot`, `toolchain`.
**Arrays (1)**: `runner`.
**Sub-tables (13)**: `abi`, `build`, `build-dependencies`, `dependencies`, `dev-dependencies`, `feature-deps`,
`feature-requires-abi`, `feature-xlings`, `requires_abi`, `runners`, `runtime`, `targets`, `xlings`.
A sub-table outside that set is reported as "not a section mcpp reads (ignored)" and the message lists the whole set.

| Field | Validation |
|---|---|
| `toolchain` | empty inherits `[toolchain]` |
| `linkage` | accepts only `static` \| `dynamic`, otherwise error. Answers a different question from `[targets.<n>] linkage` |
| `cxx_runtime` | accepts only `self-contained` \| `toolchain-coupled` \| `host-coupled` |
| `min_api_level` | Android's minimum API level, and **mandatory on Android rows** - bionic refuses an unversioned triple outright. A project decision, not a toolchain property: one NDK serves a range. It enters the **effective** triple handed to clang (`aarch64-unknown-linux-android24`) while the canonical triple stays `aarch64-linux-android`, and it **enters the build fingerprint** - two levels are two ABIs and never share a build directory |
| `sysroot` | **absent is not the empty string**: absent inherits the target row default, `sysroot = ""` **selects the zero-libc layer**. Otherwise the value must be an xpkg reference (`<ns>:<name>[@<ver>]`); a bare name is refused as `not an xpkg reference`. Implemented as two members `sysroot` + `sysrootDeclared` rather than `optional<string>` (an `optional<string>` data member poisons downstream TUs under clang + MSVC STL). **On an MSVC-ABI row (`*-windows-msvc`, recognised by spelling) the key names the MSVC toolset instead**, see below [modules/manifest/src/toml.cppm:676-701 @ b4824697] |
| `runner` | argv template; the artifact path is **appended**, or replaces `{}`. **mcpp ships no default runner.** It is honoured on hosted cross targets, not only freestanding ones, and the program is located in the declared payloads' `bin/` first and then `PATH` - a bare name on `PATH` resolves to an xvm shim, which answers per the *current* SubOS. "Nowhere to be found" is decided before any spawn and is an **error**, not a fall back to executing the artifact bare. `--no-runner` on `run`/`test` is the exit |
| `runners` (table) | named runners, `name = [argv]`, consumed by `mcpp run --runner` / `--list-runners` and `mcpp why runners` |
| `abi` (table) | the artifact's ABI switches, `threads` and `exceptions`. **Root-manifest only** - a dependency's own `[target.<sel>.abi]` is reported (`abi/dependency-table`) and ignored, because this is one property of the whole artifact. `threads` renders `-pthread` on targets that are neither PE nor freestanding and **enters the dependency cache key** through the dialect flags; `exceptions` renders `-fexceptions` only on `os = "emscripten"`. An unknown member is refused, listing both. WARNING: the `abi` table's members are the **one exception** to the compatibility rule that older engines ignore unknown keys - an older engine rejects a member it does not know, by name |
| `requires_abi` / `feature-requires-abi` (tables) | what a dependency needs of that ABI, per selector; the requirement set is the union of package-level, feature-level and every matching selector. WARNING: `[target.<sel>] requires_abi` is **silently ignored** by 2026.9.12.2 - it is a key whose value is an inline table, and that engine's schema sweep skips every table-valued key as a conditional channel. A package relying on it for protection must state its own engine floor |

WARNING: **the key `[build] linkage` does not exist** - it is absent from `kKnownBuildKeys` [toml.cppm:2173-2189], so the sweep
[:2190-2215] reports it as `[build] has unsupported key 'linkage' (ignored)`: a schema **warning**, promoted to a hard error by
`--strict`. It is ignored, but not silently. `x86_64-windows-gnu` links statically by default, and opting out **is only possible via the
target section**.
WARNING: **there is deliberately no `[workspace.target.<triple>]`**: an ordinary `[target.<triple>]` in the root manifest is **already**
inherited by every member per triple, member wins - adding a second spelling for an existing capability is "surface without function".

**`sysroot` on an MSVC-ABI row is the MSVC toolset** - its STL, CRT and the Windows SDK that follows it - because there the compiler
(cl.exe or clang) is the toolchain and the toolset is what it compiles against [docs/20-toolchains.md:522-551;
docs/22-target-side.md:1108-1113 @ b4824697]:

```toml
[toolchain]
windows = "llvm@22.1.8"

[target.x86_64-windows-msvc]
sysroot = "msvc@14.44.35207"     # or "msvc@system" (the default when absent), or "xim:msvc@14.44.35207"
```

| Value | Meaning |
|---|---|
| `msvc@system` | the machine's default toolset: `VCToolsInstallDir` -> default toolset of the `VSINSTALLDIR`/`VCINSTALLDIR` instance -> toolset of the first `cl.exe` on `PATH` -> default toolset of the newest instance with the C++ tools -> (no vswhere) the conventional paths. First complete candidate wins [docs/20-toolchains.md:381-397] |
| `msvc@<toolset>` | a complete installed toolset of that version, searched across every instance (partial versions match by component, highest wins), else the payload; the environment takes no part |
| `xim:msvc@<toolset>` | the payload only, with the `windows-sdk` payload installed beside it |

Anything else - a C library package, `""`, `xim:msvc@system`, a bare `msvc`, another family - is refused when the manifest is parsed.
The version is the toolset directory name (`14.44.35207`), not the cl banner. The SDK follows the toolset's origin: a payload toolset
binds its SDK payload and ignores `WindowsSdkDir` with a `note:`, an installed toolset takes `WindowsSdkDir`/`WindowsSdkVersion`, then
`Windows Kits\10` [docs/20-toolchains.md:474-477].
- With **clang**, prepare resolves the toolset once and passes `-Xmicrosoft-visualc-tools-root`, `-Xmicrosoft-windows-sdk-root` and
  `-Xmicrosoft-windows-sdk-version` on every compile, link and `std` precompile; `std.ixx` is that toolset's (a toolset without one
  leaves `import std` unavailable; `std.compat` is not provided on this row). The build prints `Resolved sysroot msvc@system → MSVC
  <version> (system: <product>) · Windows SDK <version>`, and `resolution.json` records `msvc_toolset` and `windows_sdk`
  [src/build/prepare.cppm:1393-1535,15209-15224 @ b4824697]. The toolset directory and SDK version are in the dependency cache key.
- With **cl.exe** the compiler is its own sysroot: a `sysroot` naming a different toolset than the compiler is refused, telling you
  to pin the toolset in `[toolchain]` (`msvc@<toolset>`) or build with clang [src/build/prepare.cppm:1542-1563 @ b4824697].
- The key never enters the project environment's install set as a C library package.
- WARNING: engines before 2026.9.24.1 refuse the whole manifest for `msvc@system` / `msvc@<toolset>` here, and accept
  `xim:msvc@<toolset>` without acting on it. A project that depends on the toolset it names pins the engine.

## 7. `[target.'cfg(...)']` - platform conditions (deferred evaluation)

### 7.1 The complete predicate set (exhaustive; an unknown key is now **reported**, not silently false)

Evaluator [src/build/prepare_inputs.cppm].
- **Combinators**: `all(...)` (empty list -> true) / `any(...)` (empty list -> false) / `not(expr)`, **arbitrarily nestable**.
- **Exactly 4 bare-word predicates** [:266-269]: `windows` / `linux` / `macos` / `unix` (the last tests `family=="unix"`).
- **5 key-value predicate keys** [:175,:197]: `os` / `arch` / `family` / `env` / **`accelerator`**.
- **5 resolved target-side layer keys** (2026.9.1.1+): `compiler` / `compiler-runtime` / `kernel-abi` / `c-abi` / `c++-abi`,
  combinable with the triple keys under `all`/`any`/`not`.
- **Two sugars**: bare OS aliases, `[target.linux]` is equivalent to `[target.'cfg(linux)']` (those four only); and bare
  triple exact match.
- Lexing: strings must use **double quotes**; whitespace is skipped, so `all( linux , not( windows ) )` is legal.

`accelerator` is **multi-valued** - one build may enable several backends, so comparison is membership throughout, and
`accelerator = "none"` is true exactly when the set is empty. It exists because the vocabulary is open: writing a CPU fallback
as `not(any(accelerator = "cuda", accelerator = "vulkan"))` silently changes meaning as the ecosystem grows.

**Not supported**:
- `musl` / `gnu` / `msvc` **as bare words** - you must write `env = "musl"`
- `target_os` / `target_arch` (Rust spelling)
- **`feature = "x"`** - cfg **cannot** reference features
WARNING: an unknown `cfg` key is now **reported** rather than evaluating to false, which used to read identically to "this
section correctly did not match". => Misspellings that were silently inert before will surface on upgrade, and a `--strict`
leg can go red on them.

WARNING (stale-claim retired): older write-ups say `cfg(c-abi = "musl")` is constant false (the identifier lexer stopping at
`-`) and that `std-module-flags` is not conditionable, so the documented example fails twice over. **Both halves were fixed in
2026.9.1.1.** The layer predicates evaluate, and `std-module-flags` and `private_include_dirs` are on the conditional
allowlist. => If you have `cfg(<layer> = …)` sections written against an older engine, **re-read their contents**: they were
inert when you wrote them and are live now.
WARNING: a **layer** predicate cannot select dependencies - the layers are resolved *from* the dependency graph, so such a
section would drop a package while keeping the sources that include it. It is reported and ignored. Use a feature or a triple
key.
WARNING: the `c-abi` layer reports the **library name** (`glibc` / `musl` / `picolibc` / `libSystem`), not the triple's env
segment. They coincide on musl and diverge on gnu.

### 7.2 Where cfg may appear

Per SPEC-004, the **one shape** of a conditional section is `[target.<selector>.<section>]`, and the sections mcpp reads are
the 13 sub-tables listed in §6: `abi`, `build`, `build-dependencies`, `dependencies`, `dev-dependencies`, `feature-deps.<f>`,
`feature-requires-abi`, `feature-xlings.<f>`, `requires_abi`, `runners`, `runtime`, `targets.<name>`, `xlings`.

| Subsection | Accepted keys | Evidence |
|---|---|---|
| `[target.<p>.build]` | `cflags`,`cxxflags`,`defines`,`flags`,`include_dirs`,`include_dirs_after`,`ldflags`,`private_include_dirs`,`sources`,`std-module-flags` (10) | toml.cppm:3248-3252 |
| `[target.<p>.dependencies]` / `.dev-dependencies]` / `.build-dependencies]` / `.feature-deps.<f>]` | full dep grammar | |
| `[target.<p>.runtime]` | `frameworks`, `libraries`, `link_library_dirs` (3) | toml.cppm:3162-3164 |
| `[target.<p>.abi]` | `threads`, `exceptions` | |
| `[target.<p>.targets.<name>]` | states a library target's form on that row | |
| `[target.<p>.xlings.workspace]` / `.feature-xlings.<f>]` | tools resolved against the **target** rather than the host | |

**cfg cannot appear in**: inside `[features]`, inside `[dependencies]` (write `[target.<p>.dependencies]` instead),
`[profile.*]`, `[package]`, `[targets.<name>]` at top level.
WARNING: `[target.<selector>.xlings]` does **not** accept `subos` (a project has exactly one environment) and does not accept a
package name written directly under it - the refusal names `[target.<selector>.xlings.workspace]` as the right place. A
selector on that axis also may not name a target-side layer (`accelerator`, `c-abi`, `compiler`, …): the reason is ordering,
those layers are resolved after tools are provisioned.

**Merge semantics, and the one reversal worth knowing**: build inputs **append, in declaration order**, after the base entries,
so GNU last-wins makes the conditional rule prevail (that is exactly why "remove on this platform" is expressible - the `-U`
comes after the base `-D`). `sources` is additionally mirrored into `modules.sources` (the scanner reads the latter).
**Dependencies no longer merge that way.** On a row the selector matches, a declaration of some identity in
`[target.<sel>.dependencies]` **replaces** the declaration of the same identity in `[dependencies]`, compared by normalised
identity rather than by the key's spelling; with several matching sections the later one in manifest order wins. The same holds
for `dev-dependencies`, `build-dependencies` and `feature-deps`.
*changed in 2026.9.14.2:* the unconditional declaration used to survive, so an option written only in the conditional table - a
`linkage = "shared"`, say - was silently dropped on exactly the rows it was written for.
```toml
[dependencies]
"compat.zlib" = "1.3.2"

[target.'cfg(env = "android")'.dependencies]
"compat.zlib" = { version = "1.3.2", linkage = "shared" }   # this row wins on android
```
WARNING: a conditional table that writes only options and no source (`version` / `path` / `git` / `workspace`) declares a
**different package** by the grammar. That is reported, with the completed form shown.
WARNING: **never ship a package using a bare `[target.'<triple>']`** - before mcpp 2026.8.18.1 the bare form was **inert**
without an explicit `--target`, so such a package worked in CI and silently dropped its flags on a developer machine.

## 8. `[dependencies]` / `[dev-dependencies]` / `[build-dependencies]` / `[feature-deps.*]`

All four tables **share one selector grammar** (SPEC-001).

### 8.1 Identity model and the four legal spellings [docs/specs/package-identity.md]

A package's identity is the pair `(namespace, name)`. `namespace` is a dot-separated hierarchical path and may be empty; `name` is **a single
atomic segment and must not contain `.`**. "Hierarchy always belongs to the namespace."

| # | Spelling | Normalized identity |
|---|---|---|
| 1 | `[dependencies]` + `cmdline = "0.0.2"` | `(mcpplibs, cmdline)` |
| 2 | `[dependencies]` + `acme.widget = "1.0"` | `(acme, widget)` - **the last segment is the name** |
| 3 | `[dependencies.acme]` + `widget = "1.0"` | `(acme, widget)` - exactly equivalent to #2 |
| 4 | `[dependencies]` + `"acme.widget" = "1.0"` | `(acme, widget)` |

**A bare name can only mean `mcpplibs`**: "`compat`, third-party namespaces and namespace-less packages never become implicit candidates", so
**gtest must be written `compat.gtest`**. A bare `gtest` requests a different identity, `(mcpplibs, gtest)`.
WARNING: **transitional fallback (from `2026.8.10.1`)**: on a miss for `(mcpplibs, name)` it retries `(compat, name)`; on a hit it emits a
deprecation warning and writes the **canonical identity** into lock/install/cache. **The ramp does not cover** selectors that spelled a
namespace - a miss is a miss. Rationale: a global short-name search would make resolution depend on which indices happen to be installed on a
machine, and adding an index could silently change how an existing dependency resolves (supply-chain risk).
**Reproducibility beats convenience.**
WARNING: the spec says "removal in `2026.9`" and **that has not happened** - §4.2.1 of `docs/specs/package-identity.md` still describes the
ramp, and `allowLegacyBareDefault=true` is still passed on 2026.9.15.2 [src/pm/package_fetcher.cppm:724,762]. Deprecated, not gone; do not
tell anyone their build "now fails".

**A `path` or `git` dependency takes the identity its own manifest declares** (2026.9.14.2+), whatever key reaches it. A key that normalises
to a different identity takes the declared one and **warns once per declaring edge**, naming the requester, the key, the identity the key
names and the identity the manifest declares. Consequences worth planning for in a multi-member workspace:
- Two edges written `fw` and `huxdemo.fw` over one directory are **one package**, compiled once, and `mcpp why deps` lists both keys under it.
- A manifest declaring **no** namespace takes the key's, so two differently-namespaced keys over one directory are two identities over one
  source - **refused before scanning**, naming both. The fix is a `namespace` in that manifest, or one key in both places.
- A `version` dependency is unaffected; its identity is the key.
=> Audit member manifests so each `path` key spells the identity the member declares. That also silences the per-edge warning permanently.

**When two declarations of one identity disagree** [docs/05-dependencies.md]: identical kind and reference is silent; two version constraints
are AND-combined by SemVer and an unsatisfiable pair is refused naming both constraints and both requesters; two `git` declarations differing
in rev/tag/branch, or two `path` declarations differing by canonical directory, resolve to the **root's** when the root is one of the two
requesters (otherwise to whichever resolved first), always with a `dependency/source-override` warning naming both sides, which is used, why,
and how to take the other. A root `path`/`git` declaration also beats a dependency's `git`/`version` declaration, and when the loser is a
version requirement it is checked against the `[package] version` of the root's resolved checkout. Two **non-root** declarations of different
kinds are still refused - with one added sentence: declare the identity in the root to settle it.
*changed in 2026.9.13.x:* no field was compared at all; whichever declaration was dequeued first survived, which is why "the root wins" was
folklore rather than behaviour.

### 8.2 `DependencySpec` fields [modules/manifest/src/dep_spec.cppm]

| Field | Default | Notes |
|---|---|---|
| `version` | - | SemVer: `^` (default) / `~` / `=` / range `">=1.0, <2.0"` |
| `path` | empty | a sibling mcpp package on disk |
| `git` / `rev` / `tag` / `branch` | empty | WARNING: **a `branch` git dependency is pinned by `mcpp.lock`** - the lock is authoritative, not a cache hint; deleting `$MCPP_HOME/git` or moving to another machine will not silently drift to a newer tip, you must run `mcpp update <pkg>` [docs/05-dependencies.md] |
| `visibility` | **`"public"`** | `public` \| `private` \| `interface` |
| `linkage` | empty | `static`\|`shared`. WARNING: **only effective on edges of the root manifest** (a dependency four levels deep should not get to decide the final program's layout) |
| `features` | empty | requested feature set |
| `default-features` | true | the **official way** to turn features off (there is no `!feature` negation syntax) |
| `backend = "<impl>"` | - | **sugar**, desugars 1:1 into `features = ["backend-<impl>"]` |
| `tools = [...]` | **off by default** | **host tools** you want from the dependency (the names of its `kind="bin"` targets); built for the **build machine** (never for `--target`), and the paths are handed to build.mcpp as `MCPP_DEP_<PKG>_BIN_<TOOL>`. 2026.8.5.1+ |
| `host-module = true` | **off by default** | build-time only; **neither compiled into nor linked into the target, and neither is anything it depends on**. 2026.8.5.1+, semantics corrected in 2026.8.29.1 |
| `reexport = true` | **off by default** | deliberately does not piggyback on `visibility` (which defaults to public). 2026.8.6.2+ |

**Merge rules** [docs/05-dependencies.md]: `tools` and `features` take the **union**; `host-module` and `reexport` take the **or**;
`version`/`path`/`git` **do not merge**.

WARNING: **write `"^0.3.0"`, not `"0.3"` / `"0.3.x"`** [docs/05-dependencies.md]. Measured: `"0.0"` resolves and then fails with `install path
missing after fetch`; `"0.0.x"` gives `E_NOT_FOUND` while naming a package that does exist. **This bites harder in `[feature-deps]` than in
`[dependencies]`** - a project developed against `path` dependencies never queries the index.

- `mcpp build` **ignores `[dev-dependencies]`**; only `mcpp test` resolves them.
- `[build-dependencies]` **could be parsed, merged and conditionalized before 2026.8.29.1, while no decision-making code
  read it**.
- **Not cached across projects**: `path` and `git` dependencies at any depth, **and workspace members** [docs/05-dependencies.md]. Host
  **tools** built from them are cached, but their store key carries the source: a `git` tool by resolved commit, a `path` tool by a stat
  imprint of its tree (relative path, size, **mtime**). Editing such a tool without bumping a version now reaches consumers - and the
  tar/`cp -p` rollback trap applies to that imprint.

## 9. `[features]` / `[feature-deps.*]` / `[capabilities]` / `[tools.overrides]`

### 9.1 The `[features]` table form accepts 10 keys [toml.cppm:879-905]

`defines` / `flags` (per-glob) / `forward` (Cargo `dep/feat` forwarding) / `implies` / `provides` / `requires` / `requires_abi` /
`sources` / `device_extensions` / `rule_module`. Array shorthand `name = ["implied", ...]`.
- **`include_dirs` is not supported**; `cxxflags` cannot be written directly (use the per-glob `flags` form).
- `deps` is **not** inside the feature table; it lives in the separate top-level section `[feature-deps.<feature>]`. The gate spelling is
  fixed as top-level `<qualifier>-<section>`: `feature-deps`, `feature-xlings`, `feature-requires-abi`. SPEC-004 gives the reason it is not
  `[features.<f>.deps]`: TOML forbids extending an inline table with a sub-table.
- `requires_abi` states what this feature needs of the artifact's ABI, e.g. `mt = { requires_abi = { threads = true } }`.
- `device_extensions` + `rule_module` make a feature a **build rule**: which device source extensions it compiles, and the module a
  consumer's build program imports. **They must appear together** - a feature declaring extensions without naming who compiles them is
  refused - and `rule_module` implies `host-module = true`. This is the mechanism by which a new device language costs no engine release.
  ```toml
  [features.rules-slang]
  sources           = ["rules/slang.cppm"]
  device_extensions = [".slang"]
  rule_module       = "mcpp.rules.slang"
  ```
- WARNING (stale-claim retired): this section **does** have an unknown-key sweep now. A feature name no `[features]` table declares is also
  reported when used as a gate (`[feature-xlings.<f>]`, …). Older notes calling `[features]` "the only section with no check" are wrong.

### 9.2 Semantics [docs/06-features-and-capabilities.md]

- Activation sources: the package's own `default` set, union explicit requests (root package `--features a,b`;
  dependencies use the long form's `features`/`backend`).
- Each active feature yields `-DMCPP_FEATURE_<NAME>` on **that package's own** compilation (uppercased, non-alphanumerics
  become `_`).
- **Strict validation**: a package that declares `[features]` and receives an undeclared request warns, and errors under
  `--strict`; **a package with no `[features]` accepts any request**.
- CRITICAL: **features are additive - a consumer cannot turn a default off** [docs/06-features-and-capabilities.md]. And "the library's
  default plus what the program supplies itself" is a **duplicate definition, not a replacement** (archive semantics do
  not apply to package dependencies).
- WARNING: **capability binding selects a provider, it does not prune link lines** [docs/06-features-and-capabilities.md]: a dependency
  contributes its objects whether or not its capability is bound. For providers defining **the same symbol**, having two
  in the graph is **a defect to fix, not an ambiguity to pin**.

### 9.3 Feature gating is implemented as a synthesized `!` exclusion

`!` is a **source glob exclusion**, scoped to the entire source list of **a single package** (never across packages), and
**order-independent** (all positive globs are expanded first, then the exclusions are subtracted wholesale)
[src/modgraph/scanner.cppm:858-885]. Feature gating works via `bc.sources.push_back("!" + g)` [src/build/prepare.cppm:6243-6245] - merely
removing the glob string is not enough, because the file may still be covered by a broader base glob (the default `src/**`). The activation
side **does not filter `!`**, so **an active feature may contribute a `!` exclusion** (used to turn off files that would compile by default).
WARNING - packaging pitfall: **the `!` exclusion is global and will override an entry naming the same file inside a feature**, so "exclude in
base, add back in the feature" **compiles and then blows up at link time**; make the base include it unconditionally instead [field-tested
2026-08-30, WAMR packaging].

### 9.4 Other

- `[feature-deps.<feature>]`: dependencies added only when the feature is active. Inside `[target.<p>.feature-deps]` the
  **feature itself is registered unconditionally**; only what it pulls in is conditional.
- `[feature-xlings.<feature>]`: **tools** pulled only when the feature is active - a consumer who never asks for the feature never downloads
  it. Accepts `when` exactly as unconditional entries do. Composes with the target axis as `[target.<sel>.feature-xlings.<f>]`.
- `[capabilities]`: capability pinning (the manifest counterpart of `--cap`). See `[package] exclusive` for the case where two providers of
  one capability must be a refusal rather than a choice.
- `[tools.overrides]`: `"<pkg>:<tool>" = "<path>"`. Resolution order (first hit wins): 1. the
  `MCPP_TOOL_<SANITIZED_PKG>_<SANITIZED_TOOL>` environment variable; 2. the manifest. An override **deliberately does not
  enter the store key**: "it is an escape hatch, not a reproducible input, and pretending otherwise would let a local
  path silently decide a cached artifact's identity."

## 9b. `[test]`

One key: **`discover`**, an array of globs selecting where tests come from, default `["tests/**/*.cpp"]`
[src/build/test_targets.cppm:22,46-50]. Same vocabulary as `[build] sources`: each positive glob's matches is one test program, and a glob
beginning with `!` removes what it matches, whichever positive glob found it. A test's **name** is its path relative to the fixed prefix
directory of the first glob that matched it, extension stripped. `discover = []` finds nothing (the right answer for a pure library member).
Duplicate names are refused, naming both files. A value that is not a non-empty string array is an error, and any other key under `[test]` is
a schema warning.
```toml
[test]
discover = ["checks/**/*.cpp", "!checks/fixtures/**"]
```
=> Fixtures that live under `tests/` no longer have to be moved out of the way to stop being compiled as standalone test programs.
WARNING: `mcpp test --list` falls back to `tests/**/*.cpp` when the manifest cannot be loaded, and some downstream consumers still read that
default rather than the `discover` set.

## 10. `[hooks]`

Whitelist: `build_start`, `build_failed`, `build_finished`, `during_build`, `timeout_seconds`, `enabled`, `side_effect`.

| Field | Default | Notes |
|---|---|---|
| `build_start` / `build_failed` / `build_finished` | - | **self-closing** intervals; accept only `cmd` + `timeout_seconds` |
| `during_build` | - | **spanning** interval (opened before the build, closed after); accepts only `cmd` + `loop` |
| `timeout_seconds` | **10** | table-level default; upper bound `24*60*60` |
| `enabled` | **true** | switch for the whole table |
| `side_effect` | **false**, and `true` is **hard-rejected** | |

WARNING: **a key given to the wrong event is an error, not an ignore**, and the message names the right one:
```
[hooks].build_start.loop does not apply: this command's interval ends when it exits,
so there is nothing to restart. `during_build` is the event that spans the build
```
`Hooks::active()` = `enabled && at least one command declared` - a table setting only policy keys is not active and **will not** move the
build off the fast path. The failure criterion for `loop` is **five consecutive unsuccessful exits within one second**; both upper bounds are
**fixed and not configurable**, on the grounds that "a knob whose wrong value is a spin is not a knob" (a typo in the command would otherwise
restart thousands of times per second for the entire build). `during_build` output is discarded (visible with `--verbose`), and it is stopped
**by process tree** (POSIX `POSIX_SPAWN_SETPGROUP` + `killpg`, Windows job object), covering Ctrl-C. For the remaining scope and failure
semantics see `../SKILL.md` §6.

## 11. `dialect_cxxflags` vs `cxxflags` - two channels with opposite behavior

| Where written | Effect |
|---|---|
| `[build] cxxflags` | **applies only to this package's TUs**; external dependency packages **do not get it**, and it **does not flow to consumers** either |
| `[build] dialect_cxxflags` | **applies to every TU in the whole graph, dependencies included** (the same global string as `-std=`). This is the explicit escape hatch for "a flag the known list does not yet recognize" |
| `[workspace.build] cxxflags` | channel one, plus prepended to every **member** (including members compiled as sibling dependencies), so all member TUs; **does not apply to** index/git dependencies |
| `[workspace.build] dialect_cxxflags` | prepended into the root member's `dialectCxxflags`, so if that member is the build root it takes channel two, i.e. the whole graph |

**The auto-promotion whitelist is exactly 7 entries** [types.cppm:2132-2139, in `is_dialect_flag`]: `-freflection` / `-fno-reflection` / `-fcontracts` /
`-fno-contracts` / `-fchar8_t` / `-fno-char8_t` / the prefix `-D_GLIBCXX_USE_CXX11_ABI=`. Criterion: these flags change **what the standard
library headers declare**, so a graph mixing them is already ill-formed.

**Recognized but refused promotion** [types.cppm:2153-2180, in `is_unpromoted_dialect_flag`]: `-fno-exceptions` / `-fexceptions` / `-fno-rtti` / `-frtti` / `/EHsc` / `/EHs-c-`
/ `/EHa` / `/EHac` / `/GR` / `/GR-`. Reason: **dependencies may legitimately disagree** - promoting them would compile every dependency as
no-exceptions, and the failure lands in source the user does not own. The purpose of recognizing them is to **refuse before compiling** and
point at `dialect_cxxflags` (from 2026.8.30.2 it also checks whether they made it into the `import std` precompilation).

Therefore `-fno-modules-reduced-bmi` is on **neither list** - zero references in the code. Written in `[build] cxxflags` it **applies only to
this package's TUs**, which is the right scope for working around the clang 22.1.8 reduced-BMI defect (llvm#184957). To affect the whole
graph, use `dialect_cxxflags`.

WARNING: **there is no environment-variable form of flag injection whatsoever**: `MCPP_CXXFLAGS` / `CXXFLAGS` / `CFLAGS` / `LDFLAGS` **are
read by nobody** (zero grep hits across the repository). Every build-variant knob must go through the manifest - that is the precondition for
fingerprint completeness.

## 12. `[workspace]` / `[workspace.package]` / `[workspace.build]`

### 12.1 `[workspace]`
`members` (member directories, relative paths), `exclude` [toml.cppm:3470-3473].

CRITICAL: **for a member to be importable you must write both `[workspace] members` and `[dependencies.<ns>] x = { path = ... }`** - mcpp's
own manifest calls this pitfall out: "`members` is what makes `-p` and `mcpp test` address them; it is **NOT** what makes them importable. ...
needing both is easy to get wrong because either one alone looks sufficient." [mcpp.toml:80-82]

### 12.2 `[workspace.package]` - closed set of 6 keys
`standard` / `version` / `license` / `description` / `repo` / `authors`. An unknown key is an **ERROR**:
```
[workspace.package] has no key '<x>'. Supported: standard, version, license,
description, repo, authors. `name` is per-member by definition.
```
`standard` is normalized here (accepting both string and integer), so members inheriting it get the same canonical spelling, and an invalid
value is reported on the line that wrote it rather than on the first member that inherits it.

### 12.3 `[workspace.build]` - closed set of 14 keys
```
cflags, cxxflags, ldflags, defines, dialect_cxxflags,
include_dirs, include_dirs_after, private_include_dirs,
c_standard, linkage, target, cxx_runtime,
dependency_linkage, macos_deployment_target
```
[toml.cppm:3551-3556]. **`allow_host_libs` is named and rejected separately**, with its own reason: "It disables the hermetic-link check for
a specific artifact, so it belongs in that package's own [build] table where the person turning it off owns the result." Criterion: **keys
that say "how to build" are inheritable; keys that say "which check not to run" stay in the package that produces the artifact**.

WARNING: `ios_deployment_target` **is read** by the loader [:3549] but is **not in that array**, so writing it here is a hard parse error.
The array is the authority, not the unsupported-key message.

**Difference set (present in `[build]`, absent from `[workspace.build]`, i.e. not inheritable)**: `allow_host_libs` (explicitly rejected),
`accel`, `sources`, `flags`, `module_extensions`, `static_stdlib`, `bmi_schedule`, `jobs`, `cache`, `default-profile`/`profile`,
`build_program_timeout`, `std-module*`, `ios_deployment_target` (see the warning above).
`jobs` is refused here **on purpose**: concurrency is a machine fact, and its one home is `[build] default_jobs` in
`$MCPP_HOME/config.toml`.

WARNING: the root's plain `[build]` is **never** propagated to members - in a virtual workspace it is silently ignored. A workspace-wide
default build target belongs in `[workspace.build] target`, and there is no `MCPP_TARGET` environment variable.

### 12.4 Inheritance implementation [src/project.cppm:234-285]

```
vectors (prepend, workspace first):
  cflags, cxxflags, ldflags, defines, dialect_cxxflags,
  include_dirs, include_dirs_after, private_include_dirs
scalars (filled only when the member's value is empty):
  c_standard, linkage, target, cxx_runtime,
  dependency_linkage, macos_deployment_target
```
**Who wins: the member** - workspace flags are inserted at the head, member flags come after, and GNU last-wins applies on the command line.
**Relative include directories are anchored to the workspace root** [:265-274]: otherwise every member would resolve them relative to its own
directory. The failure mode would be "a header that cannot be found three member levels deep, naming neither the manifest that declared it nor
the root it was written relative to". Absolute paths pass through unchanged.
WARNING: the scalars use **`.empty()`** rather than a "was declared" flag (contrast `[workspace.package] standard`, which uses
`standardDeclared`). These fields all default to the empty string so it is equivalent in practice, but it would become a defect if any of them
ever gets a non-empty default.

**`inherit_workspace_build` has a second call site** [:222-232]: it must also run once for **every other member pulled in as a `path`
dependency** - which is exactly the relationship between workspace members, i.e. the normal case. Without that second call, `mcpp build -p
appb` would give `appb` the workspace flags and give the sibling `liba` compiled by the same command none at all. (This is the increment
#539 has over #538.)

WARNING: **the membership criterion asks the workspace's own `members` list** (compared via weakly_canonical), **not** "is this path under the
workspace directory" [src/project.cppm:137-149], so **vendored copies and examples that live inside the tree as `path` dependencies do not get
these flags**. (The regression test `tests/e2e/321_workspace_inheritance.sh` asserts both directions in the same case - testing only the
positive direction would let the wrong fix "inherit to every path dependency" pass too.)

### 12.5 Other workspace-level inheritance

| Item | Rule |
|---|---|
| `[toolchain]` | inherited only when the member's `byPlatform` is **entirely empty** (**not** a per-key merge) |
| `[target.<triple>]` | inherited **per triple**; not overridden where the member already has that triple |
| `[indices]` | `inherit_workspace_indices` |
| `[workspace.dependencies]` | the member writes `x.workspace = true`, **explicit opt-in** (the only category that keeps opt-in) |

Keeping opt-in for dependencies is **a deliberate exception**: a dependency is an **edge** in the resolution graph, and implicitly inheriting
an edge would change what a member resolves to without its manifest mentioning it. Everything else chose implicit-if-absent over cargo's
per-key opt-in, on the grounds that the drift this mechanism exists to eliminate is precisely **a member forgetting to opt in**.

### 12.6 Command semantics and fan-out boundaries [docs/07-workspace.md]
- **Virtual root** (only `[workspace]`, no `[package]`): a bare `mcpp build`/`test` acts on **all** members.
- **With a root package**: bare commands act on the **root package**; `--workspace` is required to include all members.
- The value of `-p` is the **last segment** of the member directory name **or** the full relative path.
- **Building from a member subdirectory**: mcpp searches **upward**; it enters workspace mode when it finds an
  `mcpp.toml` containing `[workspace]` **and** the current directory is listed in `members`.
- `mcpp test --workspace` reports per member, **continues past failing members**, and exits nonzero overall if any failed.
- **One standard governs the whole module graph** [docs/07-workspace.md]: BMIs are incompatible across standard levels, so
  **the root package's `standard` applies to every package in the graph, dependencies included; a dependency's own
  `standard` has no effect**. Warning by default (since 2026.8.30.2), promoted to error under `--strict`, and **reported
  only for manifests the project author controls** (root package, members, `path` dependencies).
- **Per-member and exclusive**: each member's own `target/` subdirectory; **test discovery is scoped per member** (two
  members each having a `tests/main.cpp` do not collide); `[hooks]`.

## 13. `[xlings]` - build environment (L-1); subsections mirror `.xlings.json` 1:1

| Field | Type | Notes |
|---|---|---|
| **`workspace`** | table | **the one table.** Each entry yields two projections: an install address `[<ns>:]<target>[@<version>]` and a resolution pin `[<ns>:]<version>` written into `.xlings.json` |
| `subos` | string | **absent selects `McppDefault`, an explicit `subos = "default"` selects `NamedSubos("default")`** - a string alone cannot distinguish absent from an invalid empty value |
| `deps` | array\<string\> | **superseded.** Still honoured, but warns and names the line to write instead; an **error under `--strict`**. Naming one package in both `deps` and `workspace` at different versions is a hard error. Not refused outright because the offending declaration may sit in a dependency's manifest the consumer cannot edit |
| ~~`envs`~~ | - | **REMOVED, and writing it is now a hard parse error** [toml.cppm:2153-2156]. It was materialised into `.xlings.json` and read by nothing. => Grep for it before upgrading: this is the one manifest change here that stops a build outright |

Entry spellings for `[xlings.workspace]`:
```toml
[xlings.workspace]
"xim:picolibc-riscv" = "1.8.12"                             # recommended: namespace on the key (quotes required)
picolibc-riscv       = "xim:1.8.12"                         # also accepted; the materialised file's vocabulary
code                 = ""                                   # present, version unconstrained
llvm                 = { linux = "22", macosx = "20", default = "22" }   # per host platform
"xim:probe-rs"       = { version = "0.24.0", when = "run" } # scoped; `version` is required even when empty
```
Platform keys are xlings' own `linux` / `macosx` / `windows` / `default`, with `macos` accepted as an alias; an unknown platform key is a hard
error. Writing the namespace on both the key and the version and disagreeing is an error.

**`when = "build" | "run" | "dev"`** is the axis package dependencies always had. Omitting it is exactly the pre-2026.9.4.2 behaviour, so
nothing has to migrate. Omitted and `build`: installed by every verb that builds, propagates to consumers. `run`: installed only by
`mcpp run` / `mcpp test`, propagates. `dev`: installed only when the declaring package is itself the root, **does not propagate**.
=> Moving run-only tools to `when = "run"` is the cheapest way to shrink a build-only gate leg on a throttled machine.
A consequent hazard is closed rather than left open: `mcpp build` installs less than `mcpp run` needs, so the build cache records "this build
left run-tier tools uninstalled" and `mcpp run`'s fast path rejects that entry - a `build` followed by a `run` is no longer a no-op.

**Two resolution axes, and the decision test.** `[xlings.workspace]`'s platform keys resolve against the **host** (the machine running the
build); `[target.<sel>.xlings.workspace]` resolves against the resolved **target**. Neither supersedes the other. *Does the produced code
compile or link against it?* Target axis. *Does it merely execute on the build machine?* Host axis. On a native build the two name the same
platform, so a project stating target facts on the host axis is **right by accident** and stops being right the first time it is
cross-compiled.

**Provisioning is gated but on by default.** `--offline` / `MCPP_OFFLINE=1` / `MCPP_NO_AUTO_INSTALL=1` each refuse the install and name what
would have been installed [src/build/prepare.cppm:1541-1571]; provisioning spans the **whole dependency graph**, not just the root project,
which matches the lookup side that was already graph-wide. => Point `MCPP_HOME` at a project-local directory. The reason is disk ownership,
not the absence of a switch.

**In a workspace `subos` is taken from the root manifest**, not the member's. **A target's sysroot rides the same channel**: "one
materialization, one place that can be wrong. What it must NOT do is depend on the project having an `[xlings]` section: a bare-metal project
written to the template has none." Appended rather than replacing, and deduplicated.

**One package, one version** (2026.9.6.6+): a tool's identity is `(namespace, name)` and the version is always a constraint. Installation is
decided in two steps. **Adjudication**: the declaration closer to the artifact wins (project over dependency), a declaration with no version
abstains, and the outcome is reported. **Validation**: the winner must satisfy every losing *requirement* (`>=`, `^`, `~`, comma
combinations) or the build is refused, naming both sides and the way out (`tool-version-conflict`). A bare version is a **selection**, not a
requirement, so two different exact pins go to adjudication rather than refusal. It is one comparison, not a search - there is no constraint
solver, and some combinations a solver could satisfy are refused, with the refusal saying how to proceed.
*changed in 2026.9.6.6:* two declarations of one tool at different versions installed **both** (multiple GB each) while `xpkg_dir` answered
only one, silently. => This is the pattern to look for on a long-lived registry: two versions of one `xim:` package on disk.

**SubOS routing table - what belongs elsewhere** [docs/23-the-project-environment.md]:

| Need | Goes to |
|---|---|
| a library the program links | `[dependencies]` |
| a compiler | `[toolchain]` |
| a host tool produced by a dependency | `tools = [...]` on the edge |
| a tool that already exists in the environment | `[xlings] deps` |
| which environment | `[xlings] subos` |

**PATH prepending** (2026.8.25.1+): the declared environment's `bin` is placed at the **front** of the runtime `PATH` for `build.mcpp`, as
`PATH=<declared env's bin>:<the PATH mcpp itself was started with>`.
WARNING: **it only applies to projects that declared `[xlings].subos`**; otherwise you get the PATH mcpp was started with, **byte for byte**.
WARNING: **it prepends, it does not replace**: `git`, `python3` and the shell are all outside the SubOS.
WARNING: **`command -v` answers a question about this machine, not about this build** - measured with `qemu-system-riscv64`, PATH yields a
shim reporting "is not installed in this subos" while a usable copy sits in the project's own environment [docs/30-build-mcpp.md].
**Degradation rule**: a SubOS that exists but has no `subos_info` block is **a degradation, not a failure** (runtime binding reports
`inconclusive`, no payload-first binding, a note is printed, the build continues) [docs/23-the-project-environment.md].

## 14. Quick reference for the remaining sections

**`[generated_files]`** [toml.cppm:1048-1076]: `"<relative path>" = "<file content>"`. The value must be a string; the path must be relative and
stay inside the project root (checked with `has_root_path()` rather than `is_absolute()` - on Windows `/x` is root-relative but not absolute
and would still escape), and each segment is checked for `..`. **It cannot execute any command** (that is `build.mcpp`'s job). It is written
to disk **before** build.mcpp and module graph scanning, and also **before dependency resolution** (because it may produce `build.mcpp`
itself). **Writing is skipped when the content is identical** (because ninja is mtime-driven). Three write points: root project / dependency
(including members acting as path dependencies) / xpkg index descriptor (Form B).
WARNING: upstream has recorded an ordering defect of its own: **the root and dependency writes happen on opposite sides of the merge**;
tracked separately, unfixed [types.cppm:317, in the comment block at :313-322].

**`[scan_overrides."<glob>"]`** [toml.cppm:1077-1100]: subkeys `provides` / `imports` (arrays of string). **Both empty is an error.** These are
author-asserted scan results that bypass textual scanning and are validated at build time by the compiler's own P1689 (`.ddi`).

**`[resources]`** (**consumed only by PE targets**; on ELF/Mach-O the whole section is inapplicable - not a degradation, not a
skip-with-warning: with no consumer the build is byte-identical and nothing is said): `icon` / `files` (author-written `.rc`) / `extra-inputs`
(escape hatch for the `.rc` input scanner) / `version-info` (bool or table). `version-info` subfield defaults: `company` from `authors[0]`;
`product` from `name`; `description` from `description`; `copyright` synthesized from authors/license; `originalFilename` from the produced
file name; `internalName` from `name`.
WARNING: **a declared file that does not exist is an error**, deliberately: "missing -> silently skip would institutionalize the very thing
this feature exists for: a release binary with no icon and no version metadata, and not a word about it in the build output. Not wanting an
icon is already expressible - delete the line."
WARNING - **unverified**: whether an unset `version-info` implies `true` (the source is an unset `optional<bool>`; the docs do not say; the
source notes marked this unverified and the marker is kept here).

**`[lib]`**: only `path`; empty means the convention (`src/<package-tail>.cppm`).

**`[pack]`** [types.cppm:1491-1530 (`PackConfig`); parse at toml.cppm:2706-2730]: `default_mode` (empty means `"bundle-project"`; **accepts only** `static`\|`bundle-project`\|`bundle-all`)
/ `strip` (tri-state; unset means strip) / `debug_symbols` / `include` / `exclude` / `also_skip` / `force_bundle` (additions to and
subtractions from the PEP 600 skip table).
WARNING: **there is deliberately no `[pack] profile`**: which profile `mcpp pack` uses is `--profile` > `[build] default-profile` >
`"release"`.

**`[runtime]`** [docs/04-mcpp-toml.md], a closed set of 13 keys [toml.cppm:2410-2414] (`[runtime.<capability>]` sub-tables are a provider
channel, not keys, and are skipped by the sweep): `requirements[]` (`{kind,value,phase:link|run,required,discovery}`, `required` defaults to **true**, an
undeclared `discovery` is reported as **`unknown` rather than inferred**) / `provides` / `artifacts[]` (required `role`/`path`/`provenance`) /
`libraries` / `link_library_dirs` (-> `-L`) / `transitive_needed_dirs` (-> `-Wl,-rpath-link`, ELF only) / `runtime_search_dirs` (->
RUNPATH/rpath, **never** `-L`) / `frameworks` (-> `-framework`, Mach-O only) / `deploy_files` (-> copy edges; on PE copied next to the output,
**never** a linker flag) / **`deploy`** / `[runtime."<cap>"] provider`. The legacy keys `library_dirs` / `dlopen_libs` / `capabilities`
**create no provider**. Each artifact's `identity` verdict is computed by the engine: `ok`/`mismatch`/`missing`/**`unverified`**
(`unverified` is **deliberately not equal to `ok`**).

**`deploy = [{ from, to }]`** places a runtime file in a **subdirectory** relative to the executable, which `deploy_files` cannot express (it
only ever places files beside the executable - not enough for a loader that reads a fixed subdirectory, such as `<exe dir>/vulkan/icd.d`).
`from` is relative to the declaring package, `to` to the executable's directory, and `"."` is that directory itself. Paths are `/`-separated,
must not be absolute, must not name a drive, and must contain no empty, `.` or `..` segment; offending entries are refused **by index**, and
two sources landing on one destination are refused. Test binaries see the same layout.
```toml
[runtime]
deploy = [ { from = "share/vulkan/icd.d/widget_icd.json", to = "vulkan/icd.d" } ]
```
It is a separate key rather than a table form of `deploy_files` because an older descriptor reader chokes on a `{` inside `deploy_files`
while safely skipping a `runtime` key it does not know.
*changed in 2026.9.12.2:* `mcpp pack` stages `deploy_files` **and** `deploy` beside the packed executable. Packing read **neither** list
before, so a packed smoke test may legitimately contain more files than it used to.

**`[indices]`** [modules/manifest/src/index_spec.cppm:14-32]: `name`/`url`/`rev`/`tag`/`branch`/`path` (a local path takes precedence over
url)/`artifact`/`source` (`auto`\|`artifact`\|`git`). Any rev/tag/branch pin or a local path **forces the git route**, and the artifact
declaration is ignored (with a seed-period warning). `default = {...}` / `"" = {...}` are aliases for `mcpplibs`, but the combination
`default` + `url` (rather than `path`) is **hard-rejected at parse time**.

**`[toolchain]`** [types.cppm:255-270 (`byPlatform` at :259, lookup helper at :263-266); toml.cppm:1846-1852]: a `byPlatform` map whose keys are platform names
(`linux`/`macos`/`windows`/`default`) and whose values are `"pkg@ver"`; lookup goes by platform first, then falls back to `default`. **No
unknown-key validation.** family is one of {gcc, llvm, msvc}, with the aliases `clang`->llvm, `musl-gcc`, `mingw*`, `openkal-llvm`->llvm,
`<triple>-gcc` (**the legacy spelling is a permanent alias, not a deprecation**). `@system` **is legal only for msvc**. **A `[toolchain]`
shipped by a dependency package is ignored entirely** - the only legal channel by which a dependency influences the compiler is `requires =
["mcpp:compiler=<family>"]`, and **two dependencies demanding different families is an error, not a choice between them**.
The one namespace a value may carry is `xim:`; any other `<ns>:` is refused (`'<ns>:' is not a toolchain namespace`), as is
`xim:<family>@system` [src/toolchain/registry.cppm:539-550,574-581 @ b4824697]. Since the table only stores strings, the refusal
comes when prepare parses the value, prefixed with where it came from. For gcc and llvm `xim:` is a synonym and the canonical
spelling drops it; for msvc it selects the payload only, while a bare `msvc@<toolset>` takes an installed toolset of that version
first ([docs/20-toolchains.md:426-449 @ b4824697]; the same spellings on a `*-windows-msvc` `sysroot` are in §6).

SPEC-006, `docs/specs/toolchain-management.md` (draft v0.2, 2026-09-24, written in Chinese), is the normative text behind these
rules. Each clause carries its own status - implemented, partly implemented or not implemented - and only the implemented ones are
facts about 2026.9.24.1. The vocabulary it fixes [docs/specs/toolchain-management.md:21-29 @ b4824697]: a toolchain is the
compiler driver with what ships alongside it (compiler runtime, the C++ standard library that comes with the compiler, assembler,
linker, archiver); a payload is a prebuilt tree xlings installs from the index, identified by namespace, name and version; the
origin is `managed` (ecosystem package) or `system` (located on this machine), and only msvc has a system origin; the
sysroot is the target environment a compile is for - the C library payload on Linux rows, the MSVC toolset and its SDK on MSVC-ABI
rows. Implemented clauses worth knowing: one resolution per build, read by compile, scan, `std` module, link and cache key alike
(§3.1); every probed choice is printed, written to `resolution.json` and keyed (§3.3); properties that describe the artifact are
decided by target, never by host - only the host-run `build.mcpp` compile follows the host (§3.6). §3.2 (partly implemented; its
three listed items are implemented) says a declared version outranks environment variables and machine probing and an ignored
variable is reported in one line; the three items are the managed toolset ignoring `WindowsSdkDir` and reporting it,
`VSINSTALLDIR` ahead of vswhere, and a pinned version ignoring `VCToolsInstallDir` / `VSINSTALLDIR` and reporting it
[:71-79 @ b4824697]. The payload
contract (§4: relocatable, no frozen build-machine C library headers in `include-fixed/`, rewrites limited to ELF
`PT_INTERP`/`RUNPATH` and clang `.cfg` and recorded in `.mcpp-fixup.json`, completeness, `.mcpp-toolchain.json`, a new asset name
for changed content), the build rules (§5), the acceptance programs (§6: payload lint, a compiler x C library matrix enumerated from
the index, the admission gate in CI) and the release order (§7) are mostly partial: §4.1-4.5, §5.1, §5.3 and §6.2-6.4 are partly
implemented, §4.6 (a changed payload takes a new asset name) is implemented, and the payload lint (§6.1), the fixed build container
(§5.2) and the release order (§7) are not implemented [docs/specs/toolchain-management.md:126-221 @ b4824697]. Upstream plans the
rest with the next LLVM toolchain batch [CHANGELOG.md:84-88 @ b4824697]. Implemented acceptance pieces: the doctor
`include-fixed` check (§6.4, see `commands.md` `mcpp self`); the admission script `verify-toolchain.sh` exists in the index
repository but is not run in CI (§6.3); on a descriptor change, CI installs only the `latest` payload and compiles one
`import std` program with it (§6.2).

WARNING: SPEC-006 and the code disagree on what a complete MSVC toolset is. §3.4 requires `modules/std.ixx` when the build needs
`import std` and says an incomplete candidate is skipped and reported [docs/specs/toolchain-management.md:101-102 @ b4824697]; the
code, like docs/20, checks only `include\`, `lib\<arch>\` and, on the cl.exe row, `cl.exe` [src/toolchain/msvc.cppm:842-852;
docs/20-toolchains.md:395 @ b4824697]. A toolset without `std.ixx` is still selected, and `import std` is then unavailable with it on
both rows [src/toolchain/msvc.cppm:1516-1526; src/build/prepare.cppm:1506-1525 @ b4824697]. Go by the code.

## 15. Three hard conclusions that are easy to forget

1. WARNING: **`defines` cannot make a macro-guarded `import` legal** [docs/04-mcpp-toml.md]. mcpp's lexical prescan rejects
   **any** `import` inside `#if`/`#ifdef` and does not evaluate the condition, so `#ifdef FOO` / `import bar;` fails even
   when `FOO` is in `defines`. Put the condition around an `#include` in the global module fragment instead (mcpp#421).
2. WARNING: **the zero-match glob warning has a blind spot** [docs/04-mcpp-toml.md]. A glob in `[build].flags` that
   matches no source file warns; but a **conditional** `flags` entry that does not match the current target **does not
   exist at all** and cannot be warned about - the same goes for entries of an inactive feature.
3. WARNING: **package-defined TOML keys are not supported** [docs/04-mcpp-toml.md]. The legality of a key must not depend on
   first resolving the target package. A package's extension point is an open value domain inside a fixed mechanism.
   Also: a directory whose `provenance` starts with `mcpp-pack` is marked as a generated package, and **mcpp refuses to
   `build` inside it**.

## 16. Reference implementations

`<mcpp source checkout>/mcpp.toml` (117 lines) is a real example of a manifest that is **both a package and a workspace root**: `[build]
default-profile = "release"` with a comment explaining why it opts back to release (`:10-14`); `[build] bmi_schedule = "on"` with why it is on
here and auto elsewhere (`:15-36`); `[toolchain]` pinning three platforms; `[target.x86_64-linux-musl]` with an explicit toolchain plus
`linkage = "static"`, while `[target.aarch64-linux-musl]` writes only linkage and lets the host-aware convention pick the toolchain; a
`[dependencies.mcpp]` subtable with 9 `{ path = ... }` entries matching 9 `[workspace] members`; `[dev-dependencies.compat] gtest = "1.15.2"`.

`examples/` has 13: `01-hello` / `02-with-deps` / `03-pack-static` / `04-workspace` / `05-lib-distribution` / `06-openkal-cross` /
`07-project-subos` / `08-build-rules` / `09-heterogeneous` / `10-graphics` / `11-features` / `12-a-new-device-language` /
`13-platform-targets`.
WARNING: `docs/03-examples.md` does not list them all - **the numbering is sparse, read the directory**.

## 17. Target-side declarations added in 2026.9.16.1 - 2026.9.21.3

Source: `modules/manifest/src/{toml,targetside_model,types}.cppm`, `src/toolchain/{cenv,cenv_probe,predefines}.cppm`,
`docs/22-target-side.md` and `docs/24-openkal-cross.md` at `b30e70c4`. Most projects never write these; they matter to anyone who
**publishes** a C library, a kernel-ABI implementation or a platform SDK package, and to anyone reading why a graph was refused.

### 17.1 `[c-abi]` - the C environment a C library presents (2026.9.18.1+)

```toml
[package]
provides = ["mcpp:c-abi=musl"]     # required: only the provider of the layer may write [c-abi]

[c-abi]
presents   = "posix"        # posix | windows | none            (no default)
data-model = "arch-default" # arch-default | lp64 | llp64 | ilp32 (no default)
wchar      = 32             # 16 | 32                            (no default)
builtins   = "iso"          # iso | platform                     (default platform)
```

- Written without the `mcpp:c-abi=<impl>` provide -> refused at parse time. A missing one of the three default-less keys, an unknown
  key or an unknown value -> parse error naming it. A package without the block changes nothing: command lines and cache keys are
  byte-identical to before.
- **Realisation** (one table in `cenv.cppm`, names no library): Linux `posix` = nothing to add (so GCC is accepted, 2026.9.18.2);
  macOS and freestanding `posix` = `-D__unix__`; Windows `posix` + `arch-default` = compile-only `--target=x86_64-pc-cygwin` (link
  line keeps the resolved triple) and, from 2026.9.21.2, `-U__CYGWIN__ -U__CYGWIN32__`. (`-D__MCPP_TARGET_WINDOWS__=1` is there too,
  but not because of `[c-abi]`: since 2026.9.21.1 every target-side unit of every build gets `-D__MCPP_TARGET_<OS>__=1`
  [src/build/prepare.cppm:11155-11170]; docs/22's sentence "emitted only under this substitution" predates that and is stale.) `wchar`
  adds `-fno-short-wchar` / `-fshort-wchar` when it differs from the hosted triple's native width (16 on Windows, 32 elsewhere) and
  **always** on a freestanding target (2026.9.18.3, because a Windows-hosted clang defaults to 16 even for `riscv64-none-elf`)
  [src/toolchain/cenv.cppm:504-518]; `builtins = "iso"` adds `-fno-builtin` on Apple targets (2026.9.21.3). Anything else is refused
  (`c-env-unrealisable`). A non-Clang compiler is refused only when the realisation is non-empty.
- **Verification**: a `-E -dM` probe with the final flags compares `__SIZEOF_LONG__`, `__SIZEOF_WCHAR_T__` and the identity macros
  with the declaration; a mismatch fails the build printing both columns (`c-env-verification-mismatch`). Cached per compiler
  identity plus flags. It selects the target on freestanding builds only since 2026.9.20.1.
- The realisation reaches `.S`/`.s` units through an engine-only `asmflags` broadcast (there is no manifest `[build] asmflags`).
- `presents` is **frozen** at three values and says which identity macros source sees - **not** whether `fork`, `/proc`, `epoll`
  or any header exists. Capability questions go to §17.3.
- Known costs recorded upstream: under the Windows substitution LLVM rejects `__builtin_thread_pointer()` (mimalloc fails in the
  backend); portable code written `#ifdef __unix__ ... #elif defined(__APPLE__)` takes the Unix branch on macOS.

### 17.2 `[c-abi-absent]` - what the C library does not supply (2026.9.20.1+)

```toml
[c-abi-absent]
fork      = { form = "link" }
mprotect  = { form = "enosys", note = "no operation upon a mapping's protection" }
tcsetattr = { form = "accepted-no-effect", note = "fields the kernel ABI does not name are not applied" }
```

`form` is required and closed: `link` (the definition is not in the archive - the shape the openkal capability model asks for),
`enosys` (present, reports it cannot act), `accepted-no-effect` (succeeds, part of the request is not done). Purely diagnostic: when a
link fails on a `link`-shaped name, mcpp attaches the `note`. **It is a top-level table on purpose**: older engines ignore unknown
top-level tables but refuse an unknown member of a known one, so `[c-abi].absent` made every engine below 2026.9.20.1 refuse the
whole manifest on every target (measured upstream against the published 2026.9.18.3). `absent` inside `[c-abi]` is refused with a
message naming the top-level spelling.
=> General lesson for package authors: **a new, optional, diagnostic-only key belongs in a new top-level table**, so older clients
keep building; a new member of an existing strict table raises the index `min_mcpp` floor for everyone.

### 17.3 `[kernel-abi]` - interfaces provided and required (2026.9.20.1+)

```toml
# the implementation (must provide mcpp:kernel-abi=<impl>)
[kernel-abi]
provides-interfaces = ["openkal.abort", "openkal.stream", "openkal.memory", "openkal.fs"]

# any consumer
[kernel-abi]
requires-interfaces = ["openkal.fs", "openkal.net"]
```

The engine knows no interface name; it computes a set difference at **resolution**, before compiling, and refuses naming the
missing interface, the package that wants it and the implementation that lacks it: reason `interface-not-provided`, also printed in
brackets in the message. A provider that states nothing is not a provider that provides nothing: the graph builds, and since
2026.9.21.2 a note says `note kernel-abi interfaces: <impl> states none, N requirements unchecked`.

### 17.4 Platform dependencies and closure visibility (2026.9.18.1+)

- A package that is a platform SDK says so: `provides = ["platform-sdk"]` (an ordinary unprefixed capability). Nothing is inferred from
  paths or flags.
- The `Target` report prints `platform-deps` with every such package (under the same visibility rule as the layer lines).
- `[build] platform-dependencies = "refuse"` turns their presence into a refusal (`platform-dependency`).
- Pair it with `visibility = "private"` on the edge (usually under `[feature-deps.<f>]`): private keeps the SDK's headers off
  consumers' search paths; `platform-sdk` keeps the fact visible to reports.

### 17.5 `[index]` in the home's `config.toml` (not `mcpp.toml`)

| Key | Default | Since | Meaning |
|---|---|---|---|
| `auto_refresh` | `true` | old; *widened 2026.9.16.1* | `false` blocks **every** implicit refresh (miss, pre-install, first sync of a custom index) |
| `refresh_timeout` | `120` (s) | 2026.9.16.1 | bound on one refresh; exceeding it warns and continues with the local index |
| `[index.repos."mcpplibs"] artifact` | `{ GLOBAL = "https://github.com/xlings-res/mcpp-index", CN = "https://gitcode.com/xlings-res/mcpp-index" }` | 2026.9.16.1 | region object, an ordered chain in the bundled xlings; existing homes are upgraded in place [src/config.cppm:355-375 at `b30e70c4`] |
