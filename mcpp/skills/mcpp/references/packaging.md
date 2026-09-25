# Submitting a package to mcpp-index

## 0. Version stamps and evidence baseline

- Evidence baseline: `mcpplibs/mcpp-index` `origin/main @ 3a4ab31` (2026-08-30),
  cross-checked against the mcpp source repo at `2026.8.30.2`, **dated 2026-08-31**.
  WARNING: if your checkout sits on a feature branch, always read upstream state with
  `git -C <mcpp-index checkout> show origin/main:<path>`.
- WARNING: **this file's index-side facts were not re-verified at the 2026-09-16 mcpp baseline.** The mcpp-index
  repository is a different repository and was outside that review. Descriptor fields, lint rules, the validate /
  publish CI chain, the pinned `MCPP_VERSION` and every `N/175` count therefore carry the **2026-08-31** date and are
  `[unverified]` today. Check a number before relying on it; the *shapes and rules* are the durable part.
  What **was** re-pointed at the newer baseline: citations into the mcpp repository's own `docs/` tree, which was
  renumbered (see `version-notes.md` §1), and every `src/…` / `modules/…` / `CHANGELOG.md` line number, which now reads
  against mcpp `2026.9.15.2` / `main @ 2fc7b5b0`.
- => **This file carries two stamps on purpose.** mcpp-side citations: `2026.9.15.2` / `main @ 2fc7b5b0` / 2026-09-16, the same
  as the other seven files. Index-side facts (descriptor fields, lint rules, validate/publish CI, `N/175` counts): 2026-08-31,
  `[unverified]`. The top-level stamp in `../SKILL.md` §0 does **not** cover the second half.
- **Spot-checked 2026-09-23 at mcpp-index `origin/main @ 9c6ec87`** (only these three numbers, the rest stays as stamped
  above): `index.toml` has `min_mcpp = "2026.9.18.3"` and `latest_mcpp = "2026.9.21.2"`; `.github/workflows/validate.yml` pins
  `MCPP_VERSION: "2026.9.20.1"`. Note the file's own rule ("bump `min_mcpp` only together with the CI pin") and that the two
  numbers currently differ - a descriptor validated in CI was parsed by 2026.9.20.1, not by the floor version.
- **Two engine-side facts from mcpp 2026.9.16.1-2026.9.21.3 that change how you write a package** (details in `mcpp-toml.md` §17):
  1. **A new optional key goes in a new top-level table.** mcpp ignores an unknown top-level table but refuses an unknown member of
     a table it knows. openkal-musl first wrote its absence list as `[c-abi].absent`, and every engine below 2026.9.20.1 refused
     the whole manifest; as top-level `[c-abi-absent]` it needed no floor change at all. Diagnostic-only data never justifies
     raising `min_mcpp` for everyone.
  2. **Unknown `[package]` keys are now reported** (2026.9.16.1, warning; error under `--strict`). Put tool data in
     `[package.metadata.<tool>]`, which the engine keeps verbatim and older engines ignore. A platform SDK package should declare
     `provides = ["platform-sdk"]`, and consumers should take it with `visibility = "private"`.
- Evidence markers: `[index:<path>:line]` = mcpp-index; `[docs/xx-name.md]` = mcpp official English docs;
  `[src/xx:line]` / `[modules/xx:line]` = mcpp source; `[field-tested <date>]` = run and observed directly.
- Every "N/175" or "N/145" figure comes from a **full traversal** of that branch as of that date, not from sampling.

---

## 1. Read first: where the bundled upstream skill is out of date

The `add-mcpp-index-package` skill shipped inside the mcpp-index repository (143 lines)
has not been updated upstream. Checked row by row:

| Statement in the upstream skill | Reality (verified 2026-08-31) |
|---|---|
| Step 8 "update the README: add a row to the **matching category table**; update both `README.md` and `README.zh-CN.md`" | WRONG: **those category tables no longer exist**. The README keeps a single 7-row "Reference examples" table (one representative per shape); the full catalogue moved to the online site [index:README.md:22,40-51]. **A new package need not and should not touch the README**; register the case in `docs/descriptor-examples.md` (English) + `docs/zh/descriptor-examples.md` (Chinese), the complete case book grouped by shape [index:docs/descriptor-examples.md:5-11] |
| §feature "mcpp **0.0.68**'s `features` table **can only gate sources**; other subkeys are ignored by the parser" | WRONG: **badly outdated**. **Seven subkeys** are supported now (`sources` / `defines` / `deps` / `implies` / `requires` / `provides` / `flags`), and unknown subkeys are **no longer silently ignored** — they are recorded in `xpkgUnknownKeys` and `mcpp xpkg parse` errors on them [modules/manifest/src/xpkg.cppm:1628-1790, unknown-subkey recording at :1748-1757]. See §6 |
| The four shapes in the "twelve-step overall flow": C-source compat / header-only / C++23 module / external Form-A module repo | WARNING: **there are nine now (A-I)** [index:docs/package-types.md:14-22]. The four are still the most common entry points, but E/F/G/H/I are all shapes in real use |
| Step 4 "`xpm` must cover three platforms (linux/macosx/windows)" | WARNING: **only true for 115/175**. **56 packages are linux-only**, plus 3 linux+macosx and 1 windows-only. Single-platform is legal and common; consumers gate with `[target.'cfg(linux)'.dependencies]` (`compat.libaio` / `compat.wamr` are examples, `compat.wil` is the windows-only mirror image) |
| Step 4 "directory `<x>` takes the first letter of the full package name... misplacement makes a local path index report `not found in local index`" | WARNING: **two inaccuracies**. (1) The rule is actually "first letter of the **recommended filename**" — a non-default namespace uses `<ns>.<name>.lua` (`compat.wamr.lua` -> `c`), the default namespace `mcpplibs` uses `<name>.lua` (`imgui.lua` -> `i`) [modules/manifest/src/compat.cppm:168-174], which differs from "full package name" for `mcpplibs.*`. (2) Misplacement **no longer causes not found**: once every candidate filename misses, an **identity-first full index scan** takes over [src/pm/package_fetcher.cppm:697-740]. **4** of the 175 descriptors are in fact filed under the short name (`pkgs/e/compat.eui-neo.lua`, `pkgs/p/gnome.pango*.lua`) and all work. The only cost is giving up the fast path |
| Step 6 test project "contains `mcpp.toml` and `tests/*.cpp`" | Correct. But **upstream's "minimal project" template at `docs/package-types.md:299-314` is wrong** — it writes `[toolchain] default = "gcc@16.1.0"` + `[targets.<x>] kind="bin"` + `src/main.cpp`, while **0 of the 145 members** declare `[targets.*]`, 0 declare `[toolchain]`, and 0 have `src/main.cpp` |
| §local verification recipe | WARNING: it runs `cp -a "$root/registry/." ~/.mcpp/registry/` — **writing into the user's global home**. Use an isolated home instead, see §11. Its `MCPP_INDEX_MIRROR=GLOBAL` is also a **no-op** (see §11 note) |
| Step 12 "`lint` (including `mcpp xpkg parse`) and `mirror-cn-reachable` cover the new descriptor" | Structurally right, but lint has grown to **6 per-file + 3 whole-repo** checks, see §8 |

WARNING: **the index repo's own docs have two gaps** (verified the same day):
(1) the mcpp-section field cheat sheet at `docs/repository-and-schema.md:88-103` **covers only 13 of the 26 keys**,
missing real keys such as `target_cfg` / `defines` / `flags` / `runtime` / `provides` / `requires` /
`include_dirs_after` / `private_include_dirs`;
(2) the "minimal project" template at `docs/package-types.md:299-314` **matches 0 of the 145 members** (see §10).

WARNING: **one error is in the merged descriptor itself**: the header comment of `compat.wamr` claims
"A descriptor cannot [select per architecture]" — **not true**; `target_cfg` has been able to do this
for a long time (see §4.3.1 and §12 pitfall 1). It was not caught before publication, only by a later
adversarial review.

---

## 2. Two routes: decide the origin first, then the shape

| | (a) Third-party upstream library | (b) Library developed on mcpp |
|---|---|---|
| Does upstream have `mcpp.toml` | no | yes |
| Descriptor shape | **Form B**: `mcpp = { ... }` inline build info | **Form A**: `mcpp = "<glob>/mcpp.toml"`, or **omit the field entirely** and use default lookup |
| Namespace | almost always `compat` | upstream's own (`mcpplibs` / author name / org name) |
| Full flow | all of this document | mostly the chain in `docs/11-publishing-a-library.md`; the index side only registers |
| Measured share (175 descriptors) | **Form B 111** | **Form A 64** (`mcpp = "..."` 47 + no `mcpp` field 17) |

**The full publishing chain for (b) is in the mcpp official docs [docs/11-publishing-a-library.md]**, five steps:
tag (the `mcpp.toml` version must match the tag; GitHub's auto-generated
`archive/refs/tags/<tag>.tar.gz` **is** the artifact, nothing extra to upload)
-> mirror to gitcode (**must be byte-identical**) -> add an entry to mcpp-index ->
**wait for `publish-artifact.yml` to finish** (the index is an artifact, not a git clone; editing
`pkgs/**` in a cache does nothing) -> **cold resolve verification** (delete the local checkout and any
installed copy, then build).
WARNING: that document warns specifically: **delete the seed copy before believing the real chain works**
— the seed's 0.0.48 and the published 0.0.48 are indistinguishable to a build, and a silently failed
publish leaves exactly the seed copy behind.

---

## 3. Package shapes today: nine, not four

[index:docs/package-types.md:14-22]; the letters are upstream's own numbering:

| | Shape | Criterion | Key fields |
|---|---|---|---|
| **A** | C-source compat | a little C/C++ source, users write `#include <foo.h>` | `sources` + `c_standard` |
| **B** | header-only | headers only, nothing to compile | `include_dirs` + one anchor TU |
| **C** | C++23 module | public `import x.y;` | `modules` + `generated_files`, or `.cppm` sources |
| **D** | external Form-A module repo | upstream ships its own descriptor, or the build needs something inline descriptors cannot express (`build.mcpp`, workspace, a code generator that must be compiled first) | `mcpp = "<repo path>"` |
| **E** | whole-source build + generated config | upstream generates config headers via configure/CMake; the snapshot is embedded in the descriptor | `generated_files` + `include_dirs` |
| **F** | shared-library compat | must be the **only** copy of that `.so` in the process (third parties `dlopen` it, or ecosystem payloads link the same soname) | `targets = { kind = "shared", soname = ... }` |
| **G** | host runtime adapter | drivers and similar things that cannot be vendored; only a symlink farm plus metadata | `runtime.library_dirs` / `capabilities` |
| **H** | host tool provider | the tarball also carries a **code generator** consumers must run at build time | one `kind = "bin"` + `main` entry in `targets`, plus `required_features` |
| **I** | ecosystem stack binding | the library is an internal build target of a project the ecosystem **already owns**, and upstream ships no separable unit | `xpm.<plat>.deps.runtime = { "xim:<pkg>" }` + `runtime.library_dirs` **and** `link_library_dirs` |

### 3.1 Build from source or bind: the only criterion is separability [index:docs/package-types.md:24-54]

The index **defaults to building from source**. The only question is whether upstream publishes the
library as a **separable unit** (its own release, buildable without forking the parent project).

WARNING: **"a copy already exists in the payload" is not a reason to bind** — measurement refuted that
belief: a soname already present in `DT_NEEDED` is **reused**, ld.so never searches again, so the copy
the consumer links directly gets mapped first and everything else follows it
[index:docs/package-types.md:46-48].
This holds only for `kind = "shared"` with a canonical soname; under the index default `kind = "lib"`
(objects merged into the consumer) there is no `.so` to reuse, and the library's static state exists twice.

### 3.2 Full case book

`docs/descriptor-examples.md` (45 lines, one line per shape, each giving a representative descriptor plus
**what it deliberately does not do**) [index:docs/descriptor-examples.md]. The Chinese version is
`docs/zh/descriptor-examples.md`; the two are equivalent.
**A new package should register one line here when merged** (this replaced the now-deleted README category tables).

---

## 4. Full descriptor field reference

### 4.1 Top-level `package` section

Required [index:docs/repository-and-schema.md:51-52]:
`spec` / `namespace` / `name` / `description` / `licenses` / `repo` / `type="package"` / `xpm`
(Form B additionally `mcpp`).

Lint only hard-requires that the file contain the three needles `spec =`, `name =`, `xpm =`
[index:.github/workflows/validate.yml:189-194].

**Identity is the pair `(namespace, name)`**: `namespace` is a **dotted hierarchical path**,
`name` is a **single atomic segment**; all hierarchy belongs to the namespace
[index:docs/repository-and-schema.md:56-68]:

```lua
namespace = "compat",        name = "zlib"      -- ok
namespace = "mcpplibs.capi", name = "lua"       -- ok, multi-level namespace
namespace = "mcpplibs",      name = "capi.lua"  -- rejected, not reinterpreted
```

- **The compatibility form is still accepted**: descriptors published before SPEC-001 repeat the
  namespace inside `name` (`namespace="compat", name="compat.zlib"`); the prefix is stripped before the
  check [index:tests/check_package_name.lua:9,17-19]. The index has since migrated wholesale to the short form.
- The same short name **may coexist across namespaces** (three pairs exist today); this requires
  xlings >= 0.4.69 [index:docs/repository-and-schema.md:74-77].
- **The filename does not participate in resolution** [index:docs/repository-and-schema.md:79-81],
  see the last row of the §1 table.
- There is an optional **explicit opt-out** `platform_versions_diverge = true`: "this package's per-platform
  version sets really are different" [index:tests/check_platform_version_parity.lua:26-32].
  **Exactly 1** descriptor in the whole index uses it.

### 4.2 The `xpm` section

`xpm.<linux|macosx|windows>.<bare version>` [index:docs/repository-and-schema.md:83-86]:

- `url`: a string, or a `{ GLOBAL = ..., CN = ... }` table.
- `sha256`: **required**, equal to the digest of the bytes actually downloaded.
- Versions are written **bare** (`"1.2.3"`), no leading `v`; the download URL may keep upstream's
  `.../v1.2.3.tar.gz`.
- Also `deps.runtime = { "xim:<pkg>" }` (used by shape I).
- No entry for a platform means "this platform is not supported"; **do not declare platforms you have
  not verified just for symmetry** (`compat.wamr`'s header comment is the model: it says WAMR itself is
  portable, but macOS/Windows were never built or run, so `xpm` carries only `linux`
  [index:pkgs/c/compat.wamr.lua:51-60]).

### 4.3 The `mcpp` section (Form B inline) - a **closed vocabulary**

The source of truth is the allowlist `kKnownXpkgKeys` in the mcpp parser [modules/manifest/src/xpkg.cppm:252-260], **26 keys**:

```
cflags  c_standard  cxxflags  defines  deps  features  flags
generated_files  import_std  include_dirs  include_dirs_after  private_include_dirs
language  ldflags  linux  macosx  modules  provides  requires  runtime
scan_overrides  schema  sources  target_cfg  targets  windows
```

Semantics of the common keys [index:docs/repository-and-schema.md:88-103]:

| Key | Meaning |
|---|---|
| `language` | usually `"c++23"` |
| `import_std` | mostly `false` |
| `c_standard` | for C sources: `"c99"` / `"c11"` |
| `modules` | module libraries: `{ "x.y" }` |
| `include_dirs` | glob list; header directories exposed to consumers |
| `generated_files` | `{ ["relative/path"] = "content string" }`; mcpp >= 0.0.85 supports Lua long brackets `[==[...]==]` for multi-line strings (**recommended**, readable and reviewable) |
| `scan_overrides` | `{ ["glob"] = { provides={...}, imports={...} } }`; declarative scan results, matching files skip the M1 text scan. Reconciled against the compiler's P1689 output at build time, so **a wrong entry fails loudly** (mcpp >= 0.0.85) |
| `sources` | glob list; sources compiled into the lib |
| `cflags` / `cxxflags` / `ldflags` | appended to the corresponding rule |
| `targets` | `{ ["name"] = { kind="lib"/"bin"/"shared", main=..., soname=... } }` |
| `features` | see §6 |
| `deps` | `{ ["ns.name"] = "ver" }`, flat or dotted |
| `linux` / `macosx` / `windows` | **per-OS subtables**, which may themselves contain `cflags` / `ldflags` / `sources` etc. |
| `target_cfg` | **per-target conditional config**, `{ ["cfg(...)"] = { ... } }`, see below |

WARNING: **the table above comes from the index repo's field cheat sheet
[index:docs/repository-and-schema.md:88-103], which covers only 13 of the 26 keys.**
The authoritative list is the parser's `kKnownXpkgKeys` [modules/manifest/src/xpkg.cppm:252-260]. Of the 13 keys the cheat sheet **omits**,
at least `target_cfg` / `defines` / `flags` / `runtime` / `provides` / `requires` /
`include_dirs_after` / `private_include_dirs` are real.

### 4.3.1 `target_cfg` - descriptors **do** have a per-architecture hook

[modules/manifest/src/xpkg.cppm:1443-1520]

```lua
target_cfg = {
    ["cfg(arch = \"x86_64\")"]  = { sources = { "*/arch/invokeNative_em64.s" },
                                     defines = { "BUILD_TARGET_X86_64" } },
    ["cfg(arch = \"aarch64\")"] = { sources = { "*/arch/invokeNative_aarch64.s" },
                                     defines = { "BUILD_TARGET_AARCH64" } },
},
```

- Subkeys: `sources` / `cflags` / `cxxflags` / `ldflags` / `defines` / `flags` / `include_dirs` / `private_include_dirs` / `include_dirs_after` [xpkg.cppm:1499-1508 - the subkey dispatch, whose error text names `flags/include_dirs/private_include_dirs/include_dirs_after`]. **Unknown subkeys are a hard error here**; the predicate and entry refusals are at [xpkg.cppm:1452,1460,1474].
- Same data model as `mcpp.toml`'s `[target.'cfg(...)'.build]`, and **evaluated against the resolved target** (not the build host) => **gating sources by architecture works under cross-compilation**.
- The predicate is the full `cfg()` grammar: `all(...)` / `any(...)` / `not(...)` / `key="value"` / bare words. The key-value vocabulary is **five** keys, not four - `os` / `arch` / `family` / `env` [src/build/prepare_inputs.cppm:174-176] plus **`accelerator`** [:196-198], which is an *input* (`--accel`, `[build] accel`) known before resolution rather than one of the five late `kCfgLayerKeys` at [:199-203]. This matches `mcpp-toml.md` §7.1; an older "4 keys" reading of this page predates `accelerator`. Bare words are `windows` / `linux` / `macos` / `unix` [:203-205, evaluated in `match_alias` at :264-270]. => **`arch` is a first-class predicate** [:174-176]. The vocabulary is the canonical triple vocabulary; alias spellings (`x86_64-w64-mingw32`) evaluate the same as canonical ones.
- **Availability**: landed together with #258 and the per-glob `flags`/`include_dirs` of `[target.'cfg(...)'.build]` in **0.0.102/0.0.103 (2026-07-22)** [CHANGELOG.md:6302-6345; the per-glob item itself is at :6335, the #258 batch header at :6323],
**well before** the `2026.8.27.2` the index currently pins. e2e coverage on the mcpp side: `tests/e2e/85_target_cfg_build_flags.sh`, `86_target_cfg_dependencies.sh`, `119_dep_cfg_sources.sh`, `195_target_cfg_feature_deps.sh`.
- WARNING: **0 of the 175 descriptors in the index use it** (full traversal, 2026-08-31). => Syntax and engine exist, but **there is no precedent in this index**. Whoever uses it first must do their own end-to-end verification, and should note that the index field cheat sheet does not document it yet. (Shape D / Form A packages take an equivalent route: `mcpp.toml`'s own `[target.'cfg(arch = ...)']` sections, as `mcpplibs.openarch` does [index:pkgs/o/openarch.lua:6-8].)

WARNING: **unknown key = hard error**: `mcpp xpkg parse` reports unknown mcpp-section keys as errors and
exits 1 by default (`--allow-unknown` downgrades them to warnings)
[src/cli/cmd_xpkg.cppm:238-244,264-273]. The parser also has a "common misspelling" redirect table
(`dependencies`->`deps`, `define`->`defines`, `include_dir`->`include_dirs`, ...) plus small-edit-distance
guessing [modules/manifest/src/xpkg.cppm:264-283 - the table is `kXpkgKeyAliases`, immediately after `kKnownXpkgKeys`; the suggester
itself is `closest_known_xpkg_key` at :284-309].

WARNING: **`archs` is package-level metadata, not a selector.** Fork by architecture with `target_cfg`
(§4.3.1) or with the generated-file route in §12 pitfall 1 (`compat.wamr` uses the latter).

### 4.4 The `install()` hook (used by shapes E/F/G/I)

A top-level Lua function `function install()` that runs upstream's own build system (Make, Perl Configure, ...)
and places the artifacts into the install directory. **15** descriptors in the whole index use it
(`compat.openssl`, `compat.openblas`, the `compat.x11` family, `compat.libdrm`, `compat.libgbm`, ...).
Sibling packages are referenced from the hook with `pkginfo.install_dir("compat:xcb-proto", "1.17.0")`
— **a typo returns nil instead of raising**, which is why one whole-repo lint check exists just for it
[index:tests/check_cross_package_refs.lua:1-6].

### 4.5 Difference from `mcpp.toml`

| | `pkgs/*/*.lua` descriptor | a project's `mcpp.toml` |
|---|---|---|
| Syntax | Lua table | TOML |
| Author | index maintainer / packager | library or application author |
| Describes | **how to turn an upstream tarball into a package** (download URL + checksum + build info) | how this project builds itself |
| Conditional axes | only the three per-OS subtables `linux`/`macosx`/`windows` | `[target.'cfg(...)']` predicates, far finer-grained |
| Unknown keys | **hard error** (`xpkg parse` is strict) | three fates: `[build]`/`[targets.*]` warn, `[workspace.*]` hard error, **`[features]` unchecked** (see `../SKILL.md` §5) |
| Generator | `mcpp emit xpkg [-V VER] [-o FILE] [--namespace NS]` [src/cli.cppm:636-645] | - |
| Validator | `mcpp xpkg parse <f.lua> [--json] [--allow-unknown] [--all-os]` [src/cli/cmd_xpkg.cppm:111] | `mcpp build --strict` |

IMPORTANT: **`--all-os` must be run before submitting a package**: without it only the **current host's**
section is validated, and errors in the other two sections of a three-platform descriptor stay invisible
[src/cli/cmd_xpkg.cppm:216-249]. (`--all-os` and `--json` are mutually exclusive [:133-134].)

---

## 5. `generated_files`

A **literal write-to-disk** of "path -> file content string"; it **cannot execute any command**
[modules/manifest/src/xpkg.cppm:1327-1347; the same mechanism on the `mcpp.toml` side is at
modules/manifest/src/toml.cppm:1048-1076, whose comment at :1048-1053 says "Same mechanism as the index
descriptor's generated_files key"]. 62/175 descriptors use it. Three typical uses:

1. **Config header snapshot** (shape E): embed the `config.h` that configure/CMake would generate.
2. **Architecture dispatch** (§12 pitfall 1): generate a header mapping compiler-predefined macros onto
   the macros upstream expects, then deliver it to every TU via `cflags = { "-include", "<that header>" }`.
3. **Module wrapping** (shape C): generate a `.cppm` for a header-only library so it becomes importable.

Write it with Lua long brackets, readable and reviewable:

```lua
generated_files = {
    ["mcpp_generated/include/mcpp_foo_config.h"] =
[==[
#ifndef MCPP_FOO_CONFIG_H
#define MCPP_FOO_CONFIG_H
...
#endif
]==],
},
```

Generated paths can go straight into `sources` (`"mcpp_generated/mcpp_wamr_invoke_native.S"`) and
`include_dirs` (`"mcpp_generated/include"`) — they carry no `*/` prefix because they are not inside the
upstream tarball's wrap directory [index:pkgs/c/compat.wamr.lua:143,210].

---

## 6. The usable surface of `features` (**where the upstream skill is most wrong**)

The source of truth is the parser: the `features` branch opens at [modules/manifest/src/xpkg.cppm:1628] and runs to ~:1790.
(The preceding block, :1539-1627, is the `targets` parse - an older revision of this page cited that range by mistake, so every
per-row marker pointed into target parsing.) **Seven subkeys**:

| Subkey | Meaning | Lands in |
|---|---|---|
| `sources` | glob-gated sources: excluded by default, compiled into the same lib when the feature is requested | `buildConfig.featureSources` [:1708] |
| `defines` | macros that apply **only to this package's own TUs**, not propagated to consumers | `buildConfig.featureDefines` [:1709] |
| `deps` | optional dependencies activated by the feature, `{ ["ns.name"] = "ver" }`, same shape as top-level `deps` | `featureDeps` [:1683] |
| `implies` | implies other features; `dep/feat` tokens are split into `featureForwards` (Cargo parity, #243) | `featuresMap` / `featureForwards` [:1766-1774] |
| `requires` | declares a required capability | `featureRequires` [:1710] |
| `provides` | declares a provided capability | `featureProvides` [:1711] |
| `flags` | per-feature, per-glob compile flags (#253). When active they are **appended after the base entries** and win by "last flag wins"; private, per-TU, not propagated | `buildConfig.featureFlags` [:1698] |

**Not supported (named explicitly)**: `include_dirs`. The parser comment uses it as the example
[modules/manifest/src/xpkg.cppm:1753]. => Header directories can only be hoisted into base
(§12 pitfall 4).

WARNING: **unknown subkeys are no longer swallowed silently**: they are recorded in `xpkgUnknownKeys`,
`mcpp xpkg parse` errors, and the build warns via `warn_unknown_xpkg_keys`
[xpkg.cppm:1624-1632; src/build/prepare.cppm:106].
The upstream skill's "other subfields are ignored by the parser" describes the behaviour before that.

### 6.1 Deciding whether an optional component can be a feature

- **Can**: it is **extra compilable source**.
- **Cannot (headers only)**: it shares the include root with the core and cannot be hidden.
- **Cannot (an ABI-changing define)**: `defines` reach only the package's own TUs, so a macro that
  changes the layout of a type crossing the library boundary desynchronizes consumers from the library.
  `compat.recastnavigation`'s `DT_POLYREF64` was excluded from the feature table for exactly this reason
  [index:README.md:46].
  => Conversely, **the criterion is "does the consumer's TU need to see this macro?"** — if yes, it cannot
  be a feature. `compat.wamr`'s two features are safe because it verified case by case that the public
  header `wasm_export.h` **never** branches on `WASM_ENABLE_LIBC_BUILTIN` / `WASM_ENABLE_LIBC_WASI`
  [index:pkgs/c/compat.wamr.lua:77-82].
- **Mutually exclusive backends**: a `default` feature **cannot express** exclusivity (its own
  `defines`/`sources`/`deps` have no effect at all). The correct shape is "default backend = no feature
  named"; `compat.eui-neo` is the model [index:docs/descriptor-examples.md:34].
- **Consumer-side declaration**: `dep = { version = "...", features = ["extra"] }`.
- **Negative verification is mandatory**: with the feature off, the corresponding symbols/sources must
  **actually be missing**. See §13 — the first version of one such negative assertion was evergreen.

---

## 7. The GLOBAL + CN mirror table

[index:docs/cn-mirror.md]

- Mechanism: rewrite `xpm.<plat>.<ver>.url` from a plain string into `{ GLOBAL = "<upstream>", CN = "<gitcode mirror>" }`.
  **Resolution prefers GLOBAL; CN is only the fallback when GLOBAL is unavailable**; resolution happens in
  **xlings** (the xim engine), not in mcpp's C++ parser [index:docs/cn-mirror.md:6-9].
- CN layout: gitcode organization **`mcpp-res`**, one repo per library, assets attached to a release
  tagged with the version number.
- Repository slug = package name with the `compat.` / `mcpplibs.` prefix removed (`compat.eigen` -> `eigen`;
  the `nlohmann` family uses `nlohmann-json` to avoid the ambiguity of a bare `json`).
- URL convention: `https://gitcode.com/mcpp-res/<slug>/releases/download/<ver>/<slug>-<ver>.<ext>`

### 7.1 What to do without write access to `mcpp-res`

**Do not fabricate a mirror table.** Lint requires that once `url` is a table, `CN` **must** live under
`https://gitcode.com/mcpp-res/` [index:tests/check_mirror_urls.lua:44-45], so
`{ GLOBAL=upstream, CN=upstream }` fails lint outright.
**The correct fallback is a plain string url** (lint imposes no mirror constraint on plain strings):

```lua
["2.4.5"] = { url = "https://github.com/<owner>/<repo>/archive/refs/tags/<TAG>.tar.gz",
              sha256 = "..." },
```

CN users fall back to the upstream source: slower, same functionality. A maintainer can upgrade it to a
table later (the sha256 does not change). Precedents: `pkgs/t/tensorvia-cpu.lua`, and `compat.wamr`
[index:pkgs/c/compat.wamr.lua:84-89].

### 7.2 The standard procedure when you do have access (`gtc`)

`tools/gtc` is a Python wrapper over gitcode API v5; the token lives in
`~/.config/gitcode-tool/config.json` or `GITCODE_TOKEN` [index:docs/cn-mirror.md:42-44].

```bash
# 0. Download the GLOBAL tarball, compute sha256, compute it twice to confirm stability
curl -L -fsS -o <slug>-<ver>.tar.gz "<GLOBAL url>" && sha256sum <slug>-<ver>.tar.gz
# 1. Create the repo (idempotent)
gtc repo create mcpp-res/<slug> --description "<Lib> - CN mirror for mcpp-index"
# 2. A new repo has no branch; push an init commit first or the release cannot use --target main
mkdir init && echo "# <Lib> - CN mirror" > init/README.md
gtc repo push mcpp-res/<slug> init --branch main
# 3. Publish the release and upload the asset (exactly the same file as GLOBAL)
gtc release publish mcpp-res/<slug> --tag <ver> --name "<Lib> <ver>" --target main --asset <slug>-<ver>.tar.gz
# 4. Close the loop: CN returns 200 and is byte-identical to GLOBAL
curl -fsSL -o cn.tar.gz "<CN url>" && cmp cn.tar.gz <slug>-<ver>.tar.gz && echo BYTE-IDENTICAL
```

**Four cautions** [index:docs/cn-mirror.md:82-90]:
(1) the gitcode API is rate-limited to 25 requests/minute/user, roughly 3.2 s apart; back off and retry on 429;
(2) **a release asset of the same name cannot be overwritten** — a bad upload can only be deleted through
the web UI, so the name is fixed once and for all (`<slug>-<ver>.<ext>`);
(3) a new repo has no branch; without an init commit first, `--target main` is impossible;
(4) gitcode applies text filtering, and some library descriptions or repo names get rejected — reword neutrally.

WARNING: **reachable does not mean correct**: when a fork tag of the same version is recut, gitcode cannot
overwrite the same-named asset (DELETE even returns 405), so the old tarball keeps serving 200 while GLOBAL
has moved on, and CN users silently get an old build. Observed twice on `mcpplibs/libglvnd v1.7.0`
[index:.github/workflows/validate.yml:319-324]. That is why the CI mirror job now **downloads and compares sha256**.

---

## 8. Full lint rule table

### 8.1 Per file (run on every `pkgs/*/*.lua`) [index:.github/workflows/validate.yml:175-230]

| # | Check | Fails when |
|---|---|---|
| 1 | Lua syntax | `lua5.4 -e "assert(loadfile('$f','t'))"` fails. `'t'` accepts text only, rejects bytecode |
| 2 | xpkg V1 baseline | the file lacks one of the three needles `spec *=` / `name *=` / `xpm *=` |
| 3 | no leading v | matches `\["v[0-9]+` or `\["[^"]+"\]\s*=\s*"v[0-9]+`. `refs/tags/v*` inside download URLs is unaffected |
| 4 | mirror table completeness | `check_mirror_urls.lua`: the table form must have **both** a non-empty `GLOBAL` and `CN`; `CN` must be under `gitcode.com/mcpp-res/`; **`GLOBAL` must not point at a CN mirror** [index:tests/check_mirror_urls.lua:37-48] |
| 5 | identity shape | `check_package_name.lua`: `name` must be a single atomic segment (a legacy `<ns>.<name>` prefix is stripped first) |
| 6 | `c++fly` admission | **WARN only, never FAIL**. Both spellings are checked: `language = "c++fly"` and `standard = "c++fly"` embedded in a heredoc/`generated_files`. Rationale: c++fly = "newest toolchain tier + all experimental switches", which is not reproducible for consumers |

### 8.2 Whole repo (needs to see all descriptors at once)

| Check | Why it needs the whole repo |
|---|---|
| `check_cross_package_refs.lua` | `install()` hooks address sibling packages as `<namespace>:<literal package.name>`, and **a miss returns nil instead of raising**, so a typo only surfaces far downstream (a broken libxcb shows up as a libX11 link error) [validate.yml:232-238] |
| `check_platform_version_parity.lua` | **Within one descriptor, every platform section carrying versioned entries must carry the same version set.** A partial bump is a "looks like one line" edit that must land in N platform sections; after editing `xpm.linux` and reading the file back, the file really does **contain** the new version, so the author and any whole-file grep see success, while the failure appears on a different platform against a file that literally contains that version string. Measured on 2026-08-06: xpkg 0.0.52/0.0.53 were added only to `xpm.linux`, linux CI went green twice, and eight external diagnoses were all "correct" yet all answered the wrong question [validate.yml:239-254]. The explicit opt-out is `platform_versions_diverge = true` |
| `check_duplicate_versions.lua` | **A published version number names one set of bytes, forever.** Lua accepts duplicate keys and silently folds them, so "an old tag was re-released" leaves no other trace [validate.yml:256-261] |

### 8.3 The single-source-of-truth syntax gate: `mcpp xpkg parse`

[index:.github/workflows/validate.yml:262-285] runs once per descriptor, using the CI-pinned
`env.MCPP_VERSION` (currently **`2026.8.27.2`** [validate.yml:166]).
**Strict by default: an unknown mcpp-section key fails outright** (otherwise it would be silently ignored at build time).

This also **mechanically enforces the release-ordering rule "raise the floor first, then use the new syntax"**:
a descriptor that needs newer syntax **physically cannot** pass a lint pinned to an older mcpp
[index:docs/repository-and-schema.md:152-155].
=> **Changing `index.toml`'s `min_mcpp` must be synchronized with `validate.yml`'s `MCPP_VERSION`**
[index:index.toml:5-7,41-44].

### 8.4 Reproducing lint locally [index:docs/repository-and-schema.md:222-232]

```bash
fail=0
for f in pkgs/*/*.lua; do
  lua5.4 -e "assert(loadfile('$f','t'))" >/dev/null 2>&1 || { echo "SYNTAX $f"; fail=1; }
  for n in 'spec *=' 'name *=' 'xpm *='; do grep -q "$n" "$f" || { echo "MISS $n $f"; fail=1; }; done
  grep -nqE '\["v[0-9]+|\["[^"]+"\][[:space:]]*=[[:space:]]*"v[0-9]+' "$f" && { echo "LEADING-V $f"; fail=1; }
  lua5.4 tests/check_mirror_urls.lua "$f" >/dev/null 2>&1 || { echo "MIRROR $f"; fail=1; }
  lua5.4 tests/check_package_name.lua "$f" || fail=1
done
lua5.4 tests/check_cross_package_refs.lua pkgs/*/*.lua
lua5.4 tests/check_platform_version_parity.lua pkgs/*/*.lua
lua5.4 tests/check_duplicate_versions.lua pkgs/*/*.lua
[ $fail -eq 0 ] && echo "ALL LINT PASS"
```

(WARNING: under zsh an unmatched `pkgs/*/*.lua` **aborts the whole command**; the snippet above is written
for bash, run it with bash.)

---

## 9. The CI chain

### 9.1 `validate.yml` - six jobs [index:.github/workflows/validate.yml]

Triggers [:3-30]: PRs (**path-filtered**: `pkgs/**/*.lua`, `tests/**`, both READMEs,
`mcpp.toml`, `index.toml`, the workflow itself), pushes to main, a **weekly cron at 06:00 UTC Sunday**
(full regression — selective testing is structurally blind to "two changes each green, broken together"),
and `workflow_dispatch` (with a `cache: global|local` input).

| Job | Line | What it does |
|---|---|---|
| `lint` | `:169` | §8.1 + §8.2 + §8.3. **Always runs** |
| `mirror-cn-reachable` | `:287` | `curl`s every CN url of the **changed** descriptors chosen by `select`, **downloading the full body and comparing sha256** (reachable != correct, see §7.2). The full sweep is left to the weekly cron. The whole job is skipped when the diff touches no descriptor [:313] |
| `select` | `:395` | **Computes the entire plan once** and hands it to the runners as data: which members run, how many shards per platform, which member lands in which shard. On PRs it maps from `git diff` (`pkgs/<x>/<lib>.lua` -> members referencing `<lib>` in mcpp.toml; `tests/examples/<m>/**` -> member `<m>`). **Pure documentation changes and `tools/` changes select zero members** |
| `graphics-side-effects` | `:748` | installing graphics packages must not affect unrelated members |
| `workspace (<platform> [toolchain] [shard])` | `:781` | **the only build/run channel**, no shell-driven exceptions. Matrix: linux default / linux llvm / macos default / windows default. Runs `tests/run_members.sh` (**the same script used locally**). Refreshes the published index with `mcpp index update` first [:983-988] |
| `timings` | `:1075` | merges per-shard timings into a `member-timings` artifact. **Does not auto-commit** `tests/member-timings.tsv` |
| `sweep-alert` | `:1187` | opens/updates an issue when the full sweep fails |

WARNING: **the `build` check in `gh pr checks` belongs to `site-check`, not `validate`.**
Reading it as `validate` once produced a false "build passed" claim on PR #299 by conflating the two
workflows. [field-tested 2026-08-30]

**Non-linux platforms pass because members gate themselves**: `compat.wamr`'s two members write
`[target.'cfg(linux)'.dependencies.compat]`, so on non-linux the test sources compile into a no-op `main`.
**56** of the 145 members use this technique.

### 9.2 `site-check.yml` / `deploy-site.yml`

`site-check` builds the online index site on PRs and checks that there are no warnings and that the landing
page exists; `deploy-site` publishes after a push to main. Both are path-filtered.

### 9.3 `publish-artifact.yml` - after the merge [index:.github/workflows/publish-artifact.yml]

- Triggers: pushes to `main` that **touch `pkgs/**`**, dispatch, or a daily cron at 18:00 UTC [:9-16].
- What it does: `tools/publish_mcpp_index.sh` builds a **content-hash-named artifact plus a rolling pointer**
  and pushes it to `xlings-res/mcpp-index` (both GitHub and GitCode); **clients on the artifact source pick
  it up on their next refresh** — no new mcpp release needed [:3-6].
- WARNING: **runs from forks or without secrets are skipped** (an empty `XLINGS_RES_TOKEN` takes the skip
  branch [:46-48]).
- => **Merged does not mean available.** After the merge, confirm this workflow went green before doing the
  cold resolve verification.

---

## 10. Test member conventions (full sample: 145 members, 2026-08-31)

| Fact | Count |
|---|---|
| entries in the root `mcpp.toml` `[workspace] members` | **145**, equal to the number of `tests/examples/*/mcpp.toml` on disk |
| declaring `[targets.*]` | **0** |
| declaring `[toolchain]` | **0** |
| having `src/main.cpp` | **0** |
| total `tests/**/*.c*` test files | **165** |
| declaring `[indices]` | **43** |
| gated with `[target.'cfg(...)']` | **56** |

=> **The real member shape** (`compat.wamr`'s two members are the standard model):

```toml
# tests/examples/<short>/mcpp.toml
[package]
name = "<short>-tests"
version = "0.1.0"

[target.'cfg(linux)'.dependencies.compat]
wamr = "2.4.5"                                        # or the long form with features
```

plus `tests/*.cpp` (auto-discovered by `mcpp test`), and **no `[targets]`, no `[toolchain]`,
no `src/main.cpp`**. Tests must carry **assertions that can actually fail**; a non-zero process exit is a failure.

### 10.1 `[indices]` redirection [index:docs/repository-and-schema.md:105-142]

- **Root-level inheritance**: the workspace root's `mcpp.toml` declares `[indices] compat = { path = "." }`; relative paths resolve against the **workspace root** (mcpp >= 0.0.97) and members inherit it directly, so **each member need not repeat it**.
- **Members consuming `compat` write nothing**; a member consuming another namespace writes **exactly one** `[indices]` of its own, and that declaration **replaces** (does not merge with) the inherited root table.
- **Why only one**: the index table is keyed by namespace. Declaring it under a name no dependency requests means it is not registered at all, and resolution silently falls back to the published remote index — at which point what is under test is not this checkout. Registering the same path under multiple namespaces **does** register all of them, but every subsequent lookup is then N-way ambiguous (mcpp#238 / xlings#374; before xlings 0.4.69 this was a **silent exit 1**, afterwards a loud error).
- **The cross-namespace trade-off**: one member cannot resolve two namespaces from this checkout. `tests/examples/asio-ssl` exploits this deliberately: it writes no member-level declaration and inherits the root `compat`, so asio itself comes from the published remote index while its `ssl` feature dependency `compat.openssl` resolves from this checkout — **an unmerged compat descriptor can be validated through a published consumer**.
- **Bare-name dependencies are out of scope**: redirection is keyed by the **requester's** namespace, and a bare `eigen = "5.0.1"` is a request from the default namespace, so it goes to the remote index even if it ultimately lands on a compat descriptor. **Members should always use the qualified spelling.**

---

## 11. Local verification recipe (isolated-home mode)

**Do not copy the upstream skill's version** — it does `cp -a ... ~/.mcpp/registry/`, writing into the
user's global home. Keep everything inside the working directory instead. What follows is the setup that
was actually used to take a package PR green [field-tested 2026-08-30]:

```bash
# -- One-time: build an isolated environment matching the CI version (about 2.4G) --
W="$PWD/.mcpp-verify"                         # scratch dir inside your project
MV=$(git -C <mcpp-index checkout> show origin/main:.github/workflows/validate.yml \
     | grep -oP 'MCPP_VERSION:\s*"\K[0-9.]+')  # currently 2026.8.27.2
mkdir -p "$W" && cd "$W"
curl -L -fsS -o mcpp.tgz \
  "https://github.com/mcpp-community/mcpp/releases/download/v$MV/mcpp-$MV-linux-x86_64.tar.gz"
tar -xzf mcpp.tgz
cp -a "$MCPP_HOME" "$W/mcpp-home"             # copy an existing home; never touch the original

# -- Per verification run --
cd <mcpp-index checkout>
R=$W/mcpp-$MV-linux-x86_64
env -u XLINGS_HOME -u XLINGS_BIN \
    MCPP_HOME=$W/mcpp-home \
    MCPP_VENDORED_XLINGS=$R/registry/bin/xlings \
    $R/bin/mcpp test -p wamr            # the other member is -p wamr-features
```

**Six things you must know:**

1. **The version must match CI** — read it from `validate.yml`'s `env.MCPP_VERSION`, not from whatever happens to be installed locally.
2. **`-p` takes the member directory name** (`wamr`), **not the package name** (`wamr-tests`) [src/project.cppm:333-335].
3. **A copied home reports "SubOS not self-described" / glibc version mismatch on first use**; one run of `xlings self doctor --fix` fixes it.
4. **`MCPP_INDEX_MIRROR` is a no-op.** A grep across the whole mcpp repo hits **0 files** (verified 2026-08-31 across `src/ modules/ docs/ README.md` and the whole repo, twice); mcpp definitively does not read it. `validate.yml` still sets it [:986,993], which is for xlings (or pure historical residue); **dropping it from a local rerun does not change the result**. For the real analogue see `../SKILL.md` §1.2.
5. **Cold verification must also clear the global build cache**: `rm -rf $MCPP_HOME/build-cache`, so the output shows `Compiling compat.wamr` rather than `Cached` — otherwise it is an mtime-staleness false green (`../SKILL.md` §1.7). You can also clear `rm -rf "tests/examples/<member>/target"`.
6. **The criterion is `test result ok` at the end of the output**, and a non-zero exit from the test binary is a failure. To inspect the unpacked headers/sources: `tests/examples/<member>/.mcpp/.xlings/data/xpkgs/<idx>-x-<name>/<ver>/<wrap>/`.

### 11.1 The same harness CI uses

```bash
bash tests/run_members.sh --all                     # all members
bash tests/run_members.sh wamr wamr-features        # named members
bash tests/run_members.sh --all --shard 1/3         # the batch linux shard 1 runs in CI
bash tests/run_members.sh --all --cache local       # bypass the package build cache (much slower, isolates per-member cost)
```

`MCPP` selects the binary (default: `mcpp` on PATH), `MCPP_TIMINGS` names a file to append
`<seconds>\t<member>\t<ok|FAIL>` to. Shard indices are **0-based**
[index:docs/repository-and-schema.md:236-252].

---

## 12. Four pitfalls you will hit while packaging

All four come from actually packaging a C library with per-arch assembly (`compat.wamr`)
[field-tested 2026-08-30]. A different library will most likely hit them too.

### Pitfall 1 - selecting sources by architecture: WARNING, the premise used at the time was wrong

**The problem is real**: WAMR must define either `BUILD_TARGET_X86_64` or `BUILD_TARGET_AARCH64`,
otherwise the whole invoke-native section of `wasm_runtime_common.c` compiles to nothing — **the build
succeeds and the link explodes**; and the per-OS subtables of `sources` / `cflags` only split by OS.

**But the sentence written into the descriptor at the time, "A descriptor cannot [select per architecture]",
is wrong** (found by adversarial review on 2026-08-31). `target_cfg` has offered `cfg(arch = "...")`-gated
`sources` / `defines` / `cflags` since **0.0.102 (2026-07-22)**, well before the `2026.8.27.2` the index
pins, and it is **evaluated against the resolved target**, so it works under cross-compilation (§4.3.1).
So what follows **is one viable route, not the only route, and not the only route available then**.
=> **Consider `target_cfg` first for a new package**; it just has no precedent in the index
(0 of 175 descriptors), so using it means doing your own end-to-end verification.

**The route actually taken** (still valid; `compat.wamr` is merged and verified end to end) —
let the preprocessor read the compiler's own architecture macros:

1. `generated_files` emits a config header mapping `__x86_64__`/`__aarch64__` onto the macros upstream
   expects, delivered to every TU via `cflags = { "-include", "<that header>" }` (`compat.zlib` uses the
   same technique for `Z_HAVE_UNISTD_H`).
2. Then emit a **`.S`** (uppercase) that `#include`s the selected assembly file.

**The `.S` vs `.s` distinction stands on its own and is independent of that correction**:
upstream's `arch/invokeNative_*.s` use the **lowercase** suffix, and clang assembles them **without the
preprocessor**, so the `#ifdef`s inside them have no effect. Your own dispatch file must be named `.S` to be
preprocessed, so that `#include` can paste the chosen implementation in as text and the `#ifndef
BH_PLATFORM_DARWIN` guards already inside those files work as upstream intended.
(libffi's `.S` files can self-guard precisely because of the uppercase suffix.)
=> Even if you switch to `target_cfg` and name the `.s` files directly, **this still has to be known**:
conditional compilation inside a `.s` file does not take effect.
[index:pkgs/c/compat.wamr.lua:20-37,187-204]

### Pitfall 2 - `c_standard = "c11"` defines `__STRICT_ANSI__`

Under it, bare `asm` is not a keyword (only `__asm__` is), so upstream's GNU-dialect inline assembly does
not compile. **Append `-std=gnu11` via `cflags` to override it** (later wins).
Do not work around it by flipping an upstream "turn that feature off" switch — that disables a fast path
just to accommodate a language mode.
[index:pkgs/c/compat.wamr.lua:39-48,148-149]

### Pitfall 3 - `!` exclusion is **global** and overrides same-named entries inside a feature

The pattern "exclude with `!` in base, add back inside the feature" **compiles and then fails to link**.
`compat.wamr` hit exactly this: three POSIX files that upstream does not compile when WASI is off, whose
natural translation is base-exclude plus add-back in the `libc-wasi` feature, which left the WASI build
missing `os_file_get_access_mode` / `os_closedir` / `os_is_dir_stream_valid`.
=> **Include them unconditionally in base instead** (each file was verified to compile cleanly with the
feature off); the cost is a few KB of unreferenced objects dropped by the linker.
[index:pkgs/c/compat.wamr.lua:220-231]

### Pitfall 4 - a feature cannot carry `include_dirs`

`features.<name>.include_dirs` is a key the parser **explicitly does not support** (§6).
With WASI on, even base's own `wasm_runtime_common.h` does `#include "posix.h"`, so `wasm_loader.c` /
`wasm_runtime.c` fail to compile without the sandboxed-system-primitives root.
=> **Header directories can only be listed unconditionally in base.** With the feature off they cost
nothing — they are just `-I` flags pointing at directories no base source includes from.
[index:pkgs/c/compat.wamr.lua:128-142]

---

## 13. Three tests that were nearly evergreen

All three come from the same packaging round [field-tested 2026-08-30].

1. **WAMR only warns about unresolved imports; it does not refuse instantiation.**
   The first version of the negative assertion said "instantiation should fail" — **it does not fail, so
   that case was evergreen**. The loader logs `failed to link import function` and continues; the refusal
   only appears at **call** time, as an exception whose text contains `unlinked`.
   => **Proving "this capability was not compiled in" requires actually calling it**, not asking whether the
   module loads.
   [index:tests/examples/wamr/tests/run_module.cpp:56-59]
2. `putchar_wrapper` returns **1** (the number of bytes written), not "the character written" as C's
   `putchar` contract says. Writing the expected value from the C standard fails.
   [index:tests/examples/wamr-features/tests/libc_features.cpp:94-96,102]
3. **A WASI module must export memory**, or WAMR refuses to load it
   (`a module with WASI apis must export memory by default`) — WASI wrappers need to address the guest's
   linear memory to return results. Easy to forget when hand-writing wasm bytes.
   [index:tests/examples/wamr-features/tests/libc_features.cpp:33,36-39]

**The general shape**: feature gating needs **both a positive and a negative member** — the base member
asserts "with the feature off, that import does not resolve", the features member asserts "with it on, the
call goes through". That is why `compat.wamr` is split into `tests/examples/wamr` +
`tests/examples/wamr-features` [index:tests/examples/wamr-features/mcpp.toml:3-5].

---

## 14. Worked example: `mcpplibs/mcpp-index#299`

**https://github.com/mcpplibs/mcpp-index/pull/299** — `feat(pkg): compat.wamr 2.4.5
(WebAssembly Micro Runtime)`. **Merged** (2026-08-30T11:34:13Z, by Sunrisepeak),
**9 files +894/-0, zero comments, zero reviews, merged directly** (re-checked with `gh pr view` on 2026-08-31).

It is a complete sample of Form B / shape A (C-source compat) + architecture dispatch + two features +
no CN mirror:

| File | What to look at |
|---|---|
| `pkgs/c/compat.wamr.lua` | 89 lines of header comment stating **the reason for every decision** (why a config header and a `.S` are generated, why `-std=gnu11` instead of `c_standard`, why only linux is declared, what is in base, why the two features are safe, why there is no CN mirror), then 175 lines of descriptor body |
| `tests/examples/wamr/` | base member: actually runs a hand-written wasm module, guest calls back into the host (`compute(6,7) = 42`), **plus the negative assertion for feature gating** |
| `tests/examples/wamr-features/` | features member: both guest-libc layers on, positive assertions |
| `mcpp.toml` | the two members added to `[workspace] members` |
| `docs/descriptor-examples.md` + `docs/zh/descriptor-examples.md` | registered on the "C-source compat selecting sources per architecture" line (**this replaced the deleted README category tables**) [index:docs/descriptor-examples.md:18] |

**Its CI was fully green**, including all four `workspace` groups: linux default / linux llvm /
macos default / windows default — the last two pass because the members gate on `cfg(linux)` and compile to
a no-op main elsewhere.

**End-to-end evidence** (after the merge and after `publish-artifact.yml` finished): a fresh empty project
containing only `compat.wamr = "2.4.5"` resolved from the **published index**
(log line `Updated package index 8e62120 -> 7efcc8d`) -> downloaded -> compiled -> ran `compute(6,7) = 42`.
[field-tested 2026-08-30]

WARNING: **one correction was added after publication**: the PR text could read as if aarch64 had been
verified, whereas only **assembly dispatch compiling + the config header selecting the right macros** was
proven; the C side had no sysroot to run on. Clarified with `gh pr edit`.
Under-claiming is inaccurate too, so re-reading after publishing is still worth it (see `contributing.md` §9.3).

**A second error was found after the merge** (adversarial review, 2026-08-31): the descriptor's header
comment asserts "A descriptor cannot [select per architecture]", while `target_cfg` + `cfg(arch = ...)`
has been able to since 0.0.102 (2026-07-22), more than a month before the mcpp version the index pins.
**The descriptor is still correct, CI is still green, and the behaviour is not wrong in any detail — what is
wrong is the reason it gives.**
=> When citing this worked example, **do not take that header comment as fact**; copying its reasoning
propagates a limitation that does not exist. The real picture is §4.3.1.

---

## 15. Namespace conventions (induced from all 175 descriptors)

| Namespace | Count | What goes in |
|---|---|---|
| `compat` | **104** | third-party C/C++ libraries that **ship no mcpp support**, adapted by this index in Form B |
| `mcpplibs` | **29** | the mcpp ecosystem's own module libraries (`tinyhttps` / `imgui` / `ffmpeg` / `xpkg` / ...). **This is mcpp's default namespace** — bare-name dependencies resolve into it |
| `freedesktop` | **18** | the freedesktop stack (the wayland quartet, cairo, fontconfig, egl, opengl, xkbcommon, ...), mostly Form A forks |
| `gnome` | 7 | the GNOME stack (the pango family, ...) |
| `grpc` | 2 | the gRPC family |
| one-package families | 1 each | `aimol` `boost-ext` `chriskohlhoff` `ffmpeg` `fmtlib` `ggml-org` `godotengine` `gzj-creator` `marzer` `mcpplibs.capi` `neargye` `nlohmann` `ocornut` `opencv` `wlroots` |

**The rules this induces:**

1. **`compat.* = "this library does not know mcpp exists; a packager adapted it in".** The criterion is whether
   upstream has an `mcpp.toml`, not the library's language or size. 104/175 take this route.
2. **`mcpplibs` is the default namespace**, reserved for module libraries maintained by the mcpp ecosystem.
   WARNING: **a bare `mcpp add gtest` can only mean `mcpplibs`**; third-party packages must be written
   `compat.gtest`. WARNING: the transitional fallback is documented as "removal in `2026.9`" and is **still present**
   on mcpp `2026.9.15.2` — deprecated and warned about, not gone [docs/specs/package-identity.md §4.2.1].
3. **When upstream is an organization or project with an identity, use its name** (`freedesktop` / `gnome` /
   `godotengine` / `nlohmann` / `chriskohlhoff` / `marzer` / `neargye` / `ocornut` / `boost-ext`).
   These are typically Form A: "upstream ships an mcpp project, or someone forked one for it".
4. **When one upstream has both a compat layer and a module layer, the two use different namespaces**:
   `compat.godot-cpp` (a 1022-TU source build) + `godotengine.godot-cpp-m` (module layer);
   `compat.ffmpeg` (2281 TU) + `mcpplibs.ffmpeg` (module layer).
5. **Multi-level namespaces are legal**: `mcpplibs.capi` + `name = "lua"` — hierarchy goes in the
   namespace, `name` is always a single segment.
6. **The same short name may coexist across namespaces** (three pairs today: `compat:imgui`/`mcpplibs:imgui`,
   `compat:ffmpeg`/`mcpplibs:ffmpeg`, `compat:lua`/`mcpplibs.capi:lua`); requires xlings >= 0.4.69
   [index:docs/repository-and-schema.md:74-77].

---

## 16. Committing and the PR

1. Branch from `main`; **do not push to `main` directly**.
2. Before committing, run the local lint from §8.4 and the member tests from §11, and **include the actual
   command output as evidence**.
3. The PR body must state: **shape determination / mirror status / feature assessment / verification conclusion**.
   If there is no CN mirror, say why (no `mcpp-res` access) so the maintainer knows it can be added later.
4. Confirm CI: the `workspace (...)` logs should show that only the members for this library were selected;
   `lint` (including `mcpp xpkg parse`) and `mirror-cn-reachable` should cover the new descriptor and its CN url.
   WARNING: do not mistake `site-check`'s `build` for `validate` (§9.1).
5. The maintainer performs the merge. **After the merge, confirm `publish-artifact.yml` went green**, then
   do one more cold resolve verification (§2 / §11 item 5) — merged does not mean available.
6. **Always read `git diff --stat` before publishing** (`git add -A` will drag in `target/`,
   `compile_commands.json`, `mcpp.lock`); **always re-read the published body online afterwards**.
   For the writing style of outbound text, see `contributing.md` §9.
