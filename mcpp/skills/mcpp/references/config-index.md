# Configuration reference index

Moved out of `SKILL.md` to keep it short; section numbers there still point here.

**Field-by-field tables live in `references/mcpp-toml.md`**; only the easiest traps are here.

- **Three fates for unknown keys** (the difference matters): `[build]` / `[targets.*]` / `[target.*]` / `[features]` / `[runtime]` /
  `[hooks]` -> **schema warning** (promoted to an error by `--strict`); `[workspace.package]` / `[workspace.build]` -> **hard parse error,
  the whole manifest fails to load**; `[toolchain]` -> **no validation at all** (it is an open platform -> spec map).
  Two long-standing holes are now closed, so **delete any note that repeats them**: `[features]` has an unknown-key sweep
  [modules/manifest/src/toml.cppm:879-905], and `[build] std-module` / `std-compat-module` / `std-module-flags` are in `kKnownBuildKeys`
  [:2188] instead of being reported as unsupported while working. `[runtime]` and `[target.<pred>.runtime]` gained the same sweep.
  => Upgrading from a pre-2026.9 engine will surface **new** schema warnings in manifests that were silently wrong. Those are real
  defects being found, not regressions - but a `--strict` gate leg will go red on the first run.
  *changed in 2026.9.16.1*: **`[package]` joined the swept tables** - its known keys are `accelerators authors c-environment
  description exclusive license metadata name namespace platforms provides repo requires requires_abi standard std-compat-module
  std-module std-module-flags version` [modules/manifest/src/toml.cppm:1441-1446]. Tool-specific data belongs in
  `[package.metadata.<tool>]`, which the engine keeps verbatim and never interprets (it reaches the root build program through
  `mcpp::graph_file()`, §6).
- **One word syntax for compile-flag elements (2026.9.17.1, SPEC-004 §8)**: an element of `cflags` / `cxxflags` / `asmflags` - wherever
  it is written, including xpkg descriptors and `mcpp:cflag=` / `mcpp:cxxflag=` - is split like POSIX `sh` **without any expansion**:
  unquoted blanks separate words, `'...'` is literal, inside `"..."` only `\"` and `\\` escape, outside quotes a backslash escapes only
  blank / quote / backslash (so `-IC:\sdk\include` survives), and `$ * ; |` mean nothing. The one legacy exception: an element starting
  with `-D` or `/D` that contains a space is one word verbatim. A **`defines` entry is one value, never split**: `defines =
  ["N=\"x\""]` now reaches the compiler as `-DN="x"` (older releases dropped the quotes). `ldflags`, `dialect_cxxflags` and
  `std-module-flags` are outside this rule. On the first plan after upgrading, an element whose words differ from what the older
  engine passed on this host warns once under `build/flag-words`, naming both readings. `compile_commands.json` and
  `emit build-database` now list exactly those words in `arguments`, executable without a shell.
- **Dependency `visibility` is documented (docs/05)**: `public` (default) / `private` (only this package's own units see the
  dependency's include dirs, defines and flags) / `interface` (only consumers do). A platform SDK a package needs internally belongs
  under `[feature-deps.<f>]` with `visibility = "private"`; leaving it at the default hands its headers to every consumer.
- **`[workspace.build]` is a closed allowlist** of `cflags cxxflags ldflags defines dialect_cxxflags include_dirs include_dirs_after
  private_include_dirs c_standard linkage target cxx_runtime dependency_linkage macos_deployment_target`
  [modules/manifest/src/toml.cppm:3551-3556]. WARNING: `ios_deployment_target` is **read** [:3549] but is missing from that list, so
  writing it in `[workspace.build]` is a hard error. NOTE: this one diagnostic is a hand-written literal [:3573-3579] that happens to list
  the same 14 keys; every other unknown-key sweep now prints the array it checks, so read the array when in doubt but do not treat "the
  message lies" as a general rule any more.
  Inheritance semantics [src/project.cppm]: **vectors prepend** (workspace first, so on the command line the member wins last-wins),
  **scalars fill in only when the member is empty**, **relative include dirs anchor to the workspace root** (otherwise each member
  resolves them against its own directory). `allow_host_libs` is **explicitly refused**, with a reason: keys that say "how to build" may be
  inherited, keys that say "which check to skip" stay in the package that produces the artifact. Inheritance also runs for **members
  compiled as sibling `path` dependencies**. WARNING: the membership test asks the workspace's **own `members` list**, so in-tree path
  dependencies such as vendored copies or examples **do not receive** these flags.
  WARNING: the root's plain `[build]` is **never** propagated to members - a workspace-wide default target belongs in
  `[workspace.build] target`, and `MCPP_TARGET` is not a thing.
- **`[toolchain]` pinning and the two separate refusals of `system`** (do not conflate them): (a) bare
  `[toolchain] <platform> = "system"`, refused with a pasteable alternative; (b) `<family>@system` (e.g. `gcc@system`), a **separate,
  long-standing** refusal [src/toolchain/registry.cppm]. **`msvc@system` is the only exception.** The asymmetry is by design: **libraries
  are the program's own business** (not refused), **the compiler is mcpp's own contract** (refused).
- **`xim:` is the only namespace a toolchain spelling accepts**, wherever one is parsed (`[toolchain]`, `[target.<t>] toolchain`,
  `--toolchain`, `MCPP_TOOLCHAIN`, `mcpp toolchain install/default`). Any other prefix is refused with `'<ns>:' is not a toolchain
  namespace` [src/toolchain/registry.cppm:539-550 @ b4824697], and so is `xim:<family>@system` [:574-581 @ b4824697]. For gcc and
  llvm, which only ever come from payloads, `xim:gcc@16.1.0` and `gcc@16.1.0` are the same toolchain and the canonical spelling drops
  the prefix. For msvc the prefix changes the meaning: `msvc@<toolset>` takes a complete installed toolset of that version first and
  the payload only when none is installed, `xim:msvc@<toolset>` takes the payload (and its SDK) only [docs/20-toolchains.md:426-449
  @ b4824697]. The identity, origin and selection rules behind this are drafted as SPEC-006, `docs/specs/toolchain-management.md`;
  see `references/mcpp-toml.md` §14.
- **`[toolchain]` is an open platform->spec map with no unknown-key validation** (contrast `[target.<triple>]`, which has an allowlist);
  the keys that actually do anything are `linux`/`macos`/`windows` plus `default`. **A dependency's own `[toolchain]` is ignored
  entirely** - the only legitimate channel by which a dependency influences the compiler is `requires = ["mcpp:compiler=<family>"]`, and
  two dependencies demanding different families is an **error**, not a choice.
- **In `[dependencies]`, write `"^0.3.0"`, not `"0.3"` / `"0.3.x"`**: measured, the former resolves and then fails with "install path
  missing after fetch", the latter gives `E_NOT_FOUND` naming a package that definitely exists [docs/05-dependencies.md]. **This bites
  harder in `[feature-deps]` than in `[dependencies]`** - a project developed against `path` dependencies never queries the index, so the
  failure appears only after publication, on someone else's machine.
- **A conditional dependency declaration REPLACES the unconditional one of the same identity** on the rows its selector matches (same for
  `dev-dependencies` / `build-dependencies` / `feature-deps`; with several matching sections the later one in manifest order wins). This is
  a reversal of the older behaviour, where the unconditional entry survived and options written in the conditional table were silently
  dropped on exactly the rows they were written for. A conditional table that writes only options and no source (`version`/`path`/`git`)
  declares a *different package* by the grammar and is reported.
  => Grep any multi-member workspace for a dependency named both unconditionally and under `[target.<sel>.dependencies]`: the resolved
  variant flips, and nothing errors.
- **Dependency-graph rules tightened in 2026.9.16.1** (docs/05): a `[feature-deps.<f>]` entry that restates an unconditional dependency
  must restate **the same source** (a restatement without `path`/`git`/`version`/`workspace` is read as a namespace table and refused; a
  different source is refused naming both - it used to be ignored); what the restatement adds (`tools`, `features`, `host-module`,
  `reexport`) merges into the edge in effect, and the same merge now applies when one package is named in both `[dependencies]` and
  `[build-dependencies]` (the second declaration's requests used to be dropped). A dependency whose declared `[targets]` are **all
  programs** (`bin`/`app`/`test`; a package with no `[targets]` table is unaffected even when a `src/main.cpp` infers a program)
  contributes only its tools: it is not scanned, compiled or linked into the consumer, so a tool may
  depend on the package that requests it. A package cycle is refused where the graph resolves (`package-cycle`). A `git` dependency key
  whose identity is not the repository's root package selects the matching member of that repository's `[workspace] members` at the
  same commit (there is deliberately no `subdir` key: an older engine would ignore it and build the root package silently).
- **Every file matched by `sources` must produce a linked object**; a file whose extension is neither in the builtin set nor in
  `module_extensions` is **refused by name** [docs/04-mcpp-toml.md]. The builtin **device**-source extension table (CUDA/HIP, SYCL,
  Ascend C, the 14 GLSL stages, `.glsl`, HLSL, OpenCL C, Metal) is enumerated in one place only - **[docs/42-heterogeneous-builds.md:101-112]**,
  which is also where the refusal rule is stated. Check it before adding a `.comp`/`.rgen`/`.hlsl`/`.metal` source; anything outside it
  comes from a rule package's `device_extensions` (see `references/mcpp-toml.md` §9.1) or is refused.
  => The whole device-source surface - the axis, the constrained-glob refusals, and how a rule package adds an extension - is
  `references/heterogeneous-and-baremetal.md` §1 and §3. WARNING: **`.cxx` has never been in the convention default glob**
  [modules/source-kind/src/source_kind.cppm]. WARNING: `sources = []` is **not** the same as deleting the line (the former means
  "compile nothing"). A `sources` entry may now also be a table `{ glob = "...", accel = "..." }`, so a schema that assumes "array of
  strings" will reject valid manifests; a constraint matching no file is refused by name rather than treated as a no-op.
