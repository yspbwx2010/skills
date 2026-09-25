# Heterogeneous builds, custom device languages, platform rows, and the bare-metal ecosystem

Evidence baseline: mcpp source `main @ 2fc7b5b0` (version `2026.9.15.2`), read-only clone; every command shape
cross-checked against the `2026.9.15.2` release binary; GitHub reads dated 2026-09-16. §6.10 (the openkal chain) was added on
2026-09-23 against mcpp `main @ b30e70c4` (`2026.9.21.3`), mcpp-index `9c6ec87` and the openkal repositories' tags. For a
target this host cannot execute, `mcpp test --target <t> --no-run` (2026.9.21.3) is the build-only answer; see `../SKILL.md` §4.
The Apple deployment-target paragraph of §5 and the `sysroot` note of §6.5 were re-read at `main @ b4824697` (`2026.9.24.1`,
2026-09-24, source and docs only).
Evidence markers as in `../SKILL.md` §0. Items marked `[unverified]` are collected in §9 and are not facts.

This page is written for someone who has **never built device code, never targeted a browser or a phone, and never
flashed a board**. Every section carries the same thing: the complete manifest, the exact commands, where the
artifacts land, what has to be on the machine first, and the refusals you will actually hit.

## 0. When you need this page

| the question | section |
|---|---|
| compile part of a program for a GPU / NPU; `--accel`; `cfg(accelerator = …)`; a `.cu` / `.comp` / `.sycl` / `.asc` source | §1, §2 |
| *"mcpp has no role for the extension '.x'"*, or teaching mcpp a language it does not know | §3, §4 |
| writing a **build plugin / rule package**, or reading what `mcpp:plugins` does | §3 |
| `--target wasm32-emscripten`; an Android or iOS row; `min_api_level`; `pack --format apk` | §5 |
| a freestanding target (`*-none-elf`, `thumb*-none-eabi*`); board-support packages; runners; openkal | §6 |
| is `openhal` / `openarch` usable today | §7 |

Upstream's two long chapters are
[`docs/42-heterogeneous-builds.md`](https://github.com/mcpp-community/mcpp/blob/main/docs/42-heterogeneous-builds.md)
(883 lines) and [`docs/40-baremetal.md`](https://github.com/mcpp-community/mcpp/blob/main/docs/40-baremetal.md)
(814 lines). This page is the operational layer over them, not a summary of them.

### 0.1 The one prerequisite everything here shares

Nothing on this page needs a pre-installed SDK, cross-compiler, or vendor toolkit. **mcpp installs what a build
declares, on first use**, into `$MCPP_HOME/registry/data/xpkgs/` — the same channel a gcc or llvm payload arrives
through [docs/20-toolchains.md:513-525]. What you supply is a network connection and disk.

Two knobs refuse that instead of doing it, naming the packages so they can be installed out of band:
`--offline` / `MCPP_OFFLINE`, and `MCPP_NO_AUTO_INSTALL` [docs/40-baremetal.md:663-666].

What is **not** installable, and must already be on the machine, is a **driver** — a kernel-coupled, usually
non-redistributable library. That is the whole of what separates "this builds anywhere" from "this runs here", and
each section below says which side of the line it is on.

### 0.2 The paths a maintainer will hand you that do not exist

WARNING: `docs/zh/13-baremetal.md` and `docs/zh/20-heterogeneous-builds.md` are **pre-renumbering** spellings and
return 404 on `main` (GitHub contents API, 2026-09-16). `docs/zh/` mirrors the English tree **file for file**, with
the same band numbering — there is no separate Chinese numbering axis. The live pages are `docs/zh/40-baremetal.md`
and `docs/zh/42-heterogeneous-builds.md`. See `version-notes.md` §1 and §7.

## 1. The accelerator axis

### 1.1 What the axis is

mcpp does not compile device code itself. It owns the **graph**, the artifact's **identity**, and one target-side
layer called `accelerator`; a **rule package** owns the command line of each vendor compiler
[docs/42-heterogeneous-builds.md:362-372]. The axis is how a build says which devices it is for, and everything
downstream — which sources compile, which `cfg` sections apply, which payloads download, which build directory is
used — follows from it.

```toml
[build]
accel = "cuda12.9+{sm_89} ptx>=89, vulkan1.2"
```

A build names the backends it targets and **may name several** [docs/42-heterogeneous-builds.md:19-32]. The
punctuation carries meaning and is the first thing people get backwards:

- a **comma** separates entries in the set;
- a **space** separates modifiers *within one entry*. `cuda12.9+{sm_89} ptx>=89` is ONE backend with an architecture
  set and a portable-form floor, not two [docs/42-heterogeneous-builds.md:29-32].

The grammar is a backend name, a version, an optional `+{arch,arch}` list, and an optional floor — and it is **open**:
mcpp compares those four parts with no table of who exists, so a sixth backend is a package rather than an engine
release [docs/42-heterogeneous-builds.md:522-545].

```
cuda12.8+{sm_80,sm_90f} ptx>=90
vulkan1.3+{spirv1.6} floor>=1.4
sycl2020+{spir64,nvptx64-sm_89}
hip6.4+{gfx942}
ascend8.5+{dav-c220}
```

`floor>=` is the backend-neutral spelling of the portable-form floor; `ptx>=` is CUDA's word for the same field and
remains accepted [docs/42-heterogeneous-builds.md:539-542]. An architecture whose spelling carries no leading number
— `gfx942` — is compared by **equality**, because there is no ordering to read out of it
[docs/42-heterogeneous-builds.md:534-538].

### 1.2 `accelerator` is a set, and `none` is the empty one

`cfg(accelerator = "cuda")` is a **membership test**, so a build naming both CUDA and Vulkan answers true to each, and
each backend's rule compiles its own units into one artifact [docs/42-heterogeneous-builds.md:26-28, 574-584]. `any`,
`all` and `not` compose over it as ordinary boolean combinators.

`accelerator = "none"` (mcpp 2026.9.6.5) is the empty set — true exactly when this build named no accelerator at all,
and the one value that is not a backend name [docs/42-heterogeneous-builds.md:34-37, 630-656].

> **The single most common manifest bug on this axis.** Writing a CPU fallback as
> `cfg(not(accelerator = "cuda"))` is correct for a project with ONE backend and silently wrong the moment it gains a
> second: a CUDA build also satisfies `not(accelerator = "vulkan")`, so the CPU implementation joins the link beside
> the CUDA one, and — because both define the same `extern "C"` symbols — the link fails:
>
> ```
> ld: obj/src/cpu/impl.o: multiple definition of `impl';
>     obj/src/cuda/impl.o: first defined here
> ```
>
> Loud, and at the link rather than at run time, but avoidable in the manifest. Say "this build named no backend"
> directly [docs/42-heterogeneous-builds.md:614-656]:
>
> ```toml
> [target.'cfg(accelerator = "none")'.build]
> sources = ["src/cpu/*.cpp"]
> ```
>
> and `cfg(not(accelerator = "none"))` — "this build named at least one backend" — for a dispatcher shared by several.
> The four single-backend examples in `examples/09-heterogeneous` still use the `not(accelerator = "<its own>")`
> spelling and are correct *for one backend*; `cann/` is the one that switched, and its README explains why
> [examples/09-heterogeneous/cann/app/README.md:84-89].

### 1.3 The four spellings, and which command takes which

| spelling | lives in | meaning |
|---|---|---|
| `[build] accel = "<set>"` | manifest | what this build compiles device code FOR |
| `--accel <SPEC>` | `build`, `run`, `test` | overrides `[build] accel` for one invocation — the relation `--target` has to `[toolchain]` |
| `--no-accel` | `build`, `run`, `test` | **an explicit request for no accelerator**, not the absence of `--accel`; selects the CPU-only variant |
| `[package] accelerators = ["cuda", "vulkan"]` | manifest | which backends this package's **sources are written for** |

Verified on the binary (`2026.9.15.2`): `--accel <SPEC>` and `--no-accel` appear in `mcpp build --help`,
`mcpp run --help` and `mcpp test --help`, and in **none** of `mcpp pack --help`. `pack` reads `[build] accel` from the
manifest like any other build input [docs/42-heterogeneous-builds.md:704-710].

`run` and `test` gained the flags in **2026.9.5.2**. The measured consequence beforehand was a project whose CPU-only
variant could be built and not run: `mcpp build --no-accel` produced it and `mcpp run` handed back the device build
[docs/42-heterogeneous-builds.md:704-710; src/cli/cmd_build.cppm:200-208].

WARNING: `--no-accel` travels internally as the sentinel string `"(none)"`, which is a **display** form; the resolved
empty set is the empty string [src/cli/cmd_build.cppm:106-107, 518-519; src/build/prepare.cppm:3074-3096]. Do not
match on `(none)` in a script. The bug that named it: a guard written `if (!accel.empty())` was true for every project
on earth and appended `#accel=(none)` to builds that had asked for nothing [src/build/prepare.cppm:3081-3092].

WARNING: **`[package] accelerators` is two different things depending on who reads it.** Upstream describes it as "a
statement of intent and a CI-matrix hint, not a gate", which is true of *consumers selecting a package*
[docs/42-heterogeneous-builds.md:478-488]. But it **is** checked for the declaring package's own constrained globs: a
`{ glob = …, accel = "…" }` entry naming a backend absent from `[package] accelerators` is refused before anything
compiles [src/build/prepare.cppm:8730-8742]:

```
`myapp`: [build] sources entry 'src/kernels/**/*.cu' names accelerator backend "cuda",
         which this package does not declare.
         [package] accelerators = [vulkan]
       A constrained glob is left out of builds that do not name its backend, so a
       backend spelled wrong here is a file that is never compiled and never mentioned.
       fix: correct the spelling, or add the backend to `[package] accelerators`.
```

That refusal exists because the failure it replaces is silent — a misspelled backend makes a file that is never
compiled and never mentioned.

### 1.4 The constrained glob

A `[build] sources` entry may be a **table** rather than a string:

```toml
[build]
accel   = "cuda12.9+{sm_89} ptx>=89"
sources = [
  "src/*.cppm",
  "src/*.cpp",
  { glob = "src/kernels/**/*.cu", accel = "cuda12.9+{sm_89}" },
]
```

The glob **gates itself**. It reaches the build program only when this build's `accel` accepts it, so device sources
need no `cfg` block at all, and three outcomes follow from one declaration
[examples/09-heterogeneous/cuda/README.md:67-93; examples/09-heterogeneous/multi-backend/README.md:14-21]:

| the build | what happens to the glob |
|---|---|
| `mcpp build` with a covering `accel` | compiled |
| `mcpp build --no-accel` | **excluded**, silently and correctly — this is how the CPU-only variant arises |
| `--accel` naming a subset that omits this backend | **excluded** (naming a subset is not a mismatch, mcpp 2026.9.6.5) |
| `--accel` naming this backend but **not covering its architecture** | **refused before anything compiles** |

The refusal, verbatim [src/build/prepare.cppm:8776-8785]:

```
`cuda-saxpy`: [build] sources entry 'src/kernels/**/*.cu' is constrained to accel "cuda12.9+{sm_89}",
       which this build does not cover.
         this build targets: cuda12.9+{sm_86}
       fix: build with `--accel` covering it, or `--no-accel` to leave every constrained
       glob out (the CPU-only variant).
```

Machine-readable channel: `reason: accel-mismatch` [docs/50-machine-output.md:392;
src/build/refusal.cppm:131]. A glob matching **no file at all** is also refused by name rather than treated as a
no-op [src/build/prepare.cppm:8699-8712].

WARNING: **device extensions are not in the default source glob**, ever. A package that vendors a `.cu` it builds
elsewhere must not begin compiling it on an mcpp upgrade — a break its author cannot fix once that version shipped —
so device sources are opted into by naming them [docs/42-heterogeneous-builds.md:134-137].

### 1.5 Which extensions are device sources without being told

The criterion is **the compiler, not the language**. A device translation unit is never scanned for imports and never
produces a BMI, because no device compiler accepts C++20 modules
[docs/42-heterogeneous-builds.md:87-99]. `.sycl` is where that becomes visible: its content is ordinary C++ and
nothing in the file would tell a reader otherwise.

| language | extensions | since |
|---|---|---|
| CUDA, HIP | `.cu`, `.hip` | always |
| SYCL | `.sycl` | 2026.9.6.1 |
| Ascend C | `.asc`, `.cce` | 2026.9.6.5 |
| GLSL by stage | `.comp` `.vert` `.frag` `.geom` `.tesc` `.tese` `.mesh` `.task` `.rgen` `.rint` `.rahit` `.rchit` `.rmiss` `.rcall` | — |
| GLSL stage-less | `.glsl` | — |
| HLSL | `.hlsl` | — |
| OpenCL C | `.cl` | — |
| Metal | `.metal` | — |

[docs/42-heterogeneous-builds.md:101-112]

`.cuh` and `.hiph` are classified as **headers**: not compiled, but editing one invalidates the fast path exactly as
any other header does [docs/42-heterogeneous-builds.md:130-132]. A stage-less `.glsl` is refused **by the rule
package**, not the engine, because glslang derives the stage from the extension
[docs/42-heterogeneous-builds.md:126-128].

Anything outside that table comes from a rule package's `device_extensions` (§3) or is refused by name. `.slang` is
the first language supported without the engine naming it [docs/42-heterogeneous-builds.md:117-123].

### 1.6 Where the axis shows up in output

- **The build directory.** The resolved set is appended to the fingerprint as ` #accel=<set>`, and **only when
  non-empty**, so a project that asks for no accelerator keeps the directory it has
  [src/build/prepare.cppm:11557-11565]. Consequence worth knowing: the device and CPU variants live in *different*
  `target/<triple>/<16-hex>/` directories, so alternating between `mcpp build` and `mcpp build --no-accel` does not
  rebuild from scratch [examples/09-heterogeneous/cuda/README.md:85-90].
- **The build program's environment.** `MCPP_ACCEL` carries the already-resolved set (a rule package derives its own
  vendor spelling from it), and `MCPP_DEVICE_SOURCES` the package's **whole** device set, one package-root-relative
  path per line [src/build/build_program.cppm:134-138, 611-619].
- **A published artifact's descriptor.** `[[runtime.artifacts]] accel = "…"` sits **beside** the ABI tag rather than
  inside it, because an architecture list is a set while the tag is a dash-joined string whose triple already contains
  a variable number of dashes [docs/42-heterogeneous-builds.md:490-508]:

  ```toml
  [[runtime.artifacts]]
  role       = "static-library"
  path       = "lib/libgpukit.a"
  provenance = "mcpp-pack/1"
  abi        = "x86_64-linux-gnu-gcc16-libstdcxx16-c++23"
  accel      = "cuda12.8+{sm_80,sm_90f} ptx>=90"
  ```

  An **absent** `accel` means the artifact carries no device code and constrains nothing, which is why a CPU-only
  library is usable by every build.
- **Machine output** carries two reason tokens, `accel-mismatch` and `accel-backend-undeclared`
  [docs/50-machine-output.md:392-393], plus `device-source-unconsumed` [src/build/refusal.cppm:134-135].
- **NOT `resolution.json`.** Schema 2 writes `schema_version`, `toolchain`, `graph` and `runtime` and nothing else;
  there is no `accel` key anywhere in it, and its `runtime.artifacts[]` entries carry
  `role / provider / path / provenance / abi / digest / host_fingerprint / identity` — **not** `accel`
  [src/build/prepare.cppm:13354-13358, 13379-13400, 13508-13540]. A script that wants a finished build's device axis
  must read the fingerprint directory name or re-ask mcpp. The `accel` field above belongs to a **published
  descriptor**, which is a different document.

### 1.7 `[[runtime.requirements]]` — stating what the machine must already have

The failure this exists to move: a program built against a device runtime newer than the driver it will meet
compiles cleanly, links cleanly, and fails at first use with a message naming neither side
[docs/30-build-mcpp.md:205-212].

Two halves, and the engine only compares them. A rule package **measures** at build time:

```cpp
mcpp::fact("cuda.driver", driver_version);     // what this machine has
mcpp::floor("cuda.driver", runtime_needs);     // what the resolved runtime needs
```

and a package may state a fact **statically**, from install time, where probing belongs
[docs/06-features-and-capabilities.md:304-316]:

```toml
[runtime]
provides = ["cuda.driver=12.4"]
```

against which any package writes a floor:

```toml
[[runtime.requirements]]
kind  = "version-floor"
value = "cuda.driver >= 12.0"
```

mcpp compares them when capabilities are bound and refuses **before anything is compiled**, with
`reason: version-floor-unmet` [docs/30-build-mcpp.md:195-200]:

```
error: `toolkitnew` requires cuda.driver >= 13.0, and cuda.driver is stated as 12.4.
         stated by: driverfact
```

Four properties worth carrying:

- **No vendor vocabulary reaches the engine.** It reads a name, a relation and a version; `cuda.driver` is data
  flowing through, and a backend mcpp has never heard of compares the same way. A unit test
  (`tests/unit/test_core_vendor_probes.cpp`) asserts that no vendor tool name appears in `src/` once comments are
  stripped, with the file count as its own denominator [docs/42-heterogeneous-builds.md:424-430, 720-726].
- **A floor nobody answered is silent.** A machine that never declared what it has is not one that fails the floor —
  it is one nobody asked. Turning "we do not know" into "no" is the failure mode this avoids, asserted directly by
  `tests/e2e/603_version_floor.sh` [docs/06-features-and-capabilities.md:327-333].
- **A fact is cached with the build program's other output and replayed on a cache hit.** Declare what would change
  it — `rerun_if_changed` on the library the version was read from — or the fact outlives the machine it described
  [docs/30-build-mcpp.md:216-219].
- **The mechanism is not accelerator-specific.** From 2026.9.14.2 the engine states the target's own platform floor
  the same way: `android.api-level`, `ios.deployment-target`, `macos.deployment-target`
  [docs/06-features-and-capabilities.md:336-355]. §5 uses the identical channel.

### 1.8 What a rule package reports before the first compile

Three things go wrong late with a device toolkit, and none is a fact about the build graph. All three are read and
reported by the **rule package**, and the engine owns none of them
[docs/42-heterogeneous-builds.md:424-464]:

1. **Which host compiler a device compiler will accept.** nvcc refuses host compilers newer than a bound it states in
   its own `crt/host_config.h`, and mcpp's toolchain payload is frequently newer. The rule reads the bound from the
   toolkit it resolved — a payload before the host — and says which compiler it chose and why, through
   `mcpp::warning`. The clang route has no such bound: `clang -x cuda` is its own host compiler.
2. **Whether the device compiler can reach its own back end.** A toolkit can be installed, complete and on `PATH` and
   still fail at its first stage: nvcc runs `cicc`, `cudafe++`, `ptxas` and `fatbinary` as bare names on a `PATH` it
   prepends from an `nvcc.profile` beside its own binary. The rule asks `nvcc --dryrun` for its plan rather than
   assuming one, and names the first stage that does not resolve together with the payload that provides it.
3. **Whether the driver is new enough for the runtime** — the `fact`/`floor` pair of §1.7.

Reported rather than enforced where a wrong answer would cost more than none: a machine with no rule package in its
project has nothing vendor-specific to say and says nothing.

### 1.9 Consuming a dependency that ships prebuilt device code

A build's request is satisfied by an artifact when, **for each backend the build asks for**, the artifact declares
that backend, agrees on the toolkit's **major** version, and covers every requested architecture. An architecture is
covered when it is named, when a family target of the same major and an equal-or-lower minor is named, or when the
embedded portable form's floor is at or below it [docs/42-heterogeneous-builds.md:510-520]. Family targets and
portable forms are what keep the variant matrix finite: publishing one artifact per chip does not scale, one per
generation does.

When nothing matches, the refusal names the dimension and both sides
[docs/42-heterogeneous-builds.md:547-563]:

```
error: mcpplibs.gpuonly@0.1.0: no prebuilt artifact matches this toolchain.
  your toolchain : x86_64-linux-gnu-gcc16-libstdcxx16-c++23  accel=cuda12.8+{sm_86}
  published tags :
                   x86_64-linux-gnu  accel=cuda12.8+{sm_90f}
  closest is x86_64-linux-gnu, and it differs on:
    accel     needs cuda12.8+{sm_90f}, this build has cuda12.8+{sm_86}
  fix: build for an architecture the package carries (--accel), or take
       a variant that carries no device code (--no-accel), or ask the
       publisher for one covering yours.
```

WARNING (publishers): **list the CPU-only artifact FIRST.** A consumer takes the first artifact whose tag accepts it,
and an mcpp predating the `accel` field ignores that field entirely — ordering is what still gives such a client
something that runs anywhere [docs/42-heterogeneous-builds.md:566-571].

WARNING (publishers): **`mcpp pack` does not emit the `accel` field, deliberately.** The field states what an artifact
*carries*; mcpp does not yet compile device code itself, so it has nothing to measure, and recording a declaration in
a field whose meaning is "measured" would make the identity lie in exactly the way the dimension exists to prevent. A
publisher writes it into the descriptor by hand today; `mcpp pack` will emit it once `kind = "device"` puts device
compilation inside mcpp [docs/42-heterogeneous-builds.md:711-718].

### 1.10 Two shapes, and choosing between them

Accelerator toolchains come in two shapes, and **mcpp implements one mechanism**
[docs/42-heterogeneous-builds.md:44-85]:

- An **island** keeps device code in separate translation units compiled by a separate compiler. CUDA, HIP, Ascend C
  and Metal work this way. The device compiler produces an object (or, for shading languages, a runtime resource)
  that joins the ordinary link.
- A **whole-target** model puts device code in ordinary `.cpp` files and compiles the entire target with an
  offloading compiler. SYCL, OpenMP offload and stdpar are used this way.

mcpp implements the island only — a statement about the **design**, not about coverage. A whole-target toolchain is
reached *through* the island rather than beside it, which costs a rule package and no second mechanism; SYCL is in the
shipped set for exactly that reason, because a SYCL kernel is a lambda inside a `submit` and a project can confine
every one to its own translation unit, with `.sycl` making that convention checkable.

**OpenMP `target` and stdpar cannot be reached this way.** `#pragma omp target` and `std::execution::par_unseq` appear
at arbitrary call sites in ordinary code; there is no unit to move, so there is no island to impose. That boundary is
a property of the model, not a gap in the tool.

Two consequences stated plainly: an existing SYCL project whose kernels sit in `.cpp` files **does not build
unchanged** — its device units move into `.sycl` first, which is a rename and a seam, not a rewrite; and one
extension means one thing, because letting a constrained glob carry `.cpp` would make the same name select two
different compilers depending on which glob matched first.

### 1.11 Link-time selection versus run-time selection

A **seam** replaces one implementation with another, so exactly one may be linked — that is what the `cfg` exclusions
in §1.2 are for, and it is the right shape for a **program**. A **library** compiled once and consumed by people
whose machines differ cannot make that choice, so its backends are **additive**
[docs/42-heterogeneous-builds.md:658-677; examples/09-heterogeneous/multi-backend/README.md:1-10]:

- compile **every** backend the build was given — each `cfg(accelerator = …)` section adds its own sources, and the
  CPU implementation is unconditional;
- give each a distinct name, and have the seam ask at run time which devices are present.

There is then no exclusion to maintain at all. This is the shape ggml uses — each backend registers itself and
`ggml_backend_reg_by_name` picks one when the program runs — and `ggml-org:llamacpp` is built that way, its
`backend-vulkan` feature **additive over** `backend-cpu` rather than exclusive with it.

Which shape to choose is a property of the program, not of mcpp.

### 1.12 The layers underneath, and why confusing two of them breaks a build elsewhere

[examples/09-heterogeneous/README.md:115-138]

| layer | owns | example |
|---|---|---|
| engine | the graph, the artifact's identity, the axis | mcpp itself |
| rule package | the spelling of one programming model | `mcpp.rules.cuda` in `mcpp:plugins` |
| payload | the binaries, versioned by the rule and overridable by the project | `xim:cuda-nvcc`, `xim:dpcpp`, `xim:glslang` |
| adapter | a built artifact's reach to something the **host** owns | `compat:cuda-driver`, `compat:vulkan-runtime`, `compat:sycl-runtime` |

**The adapter layer exists for one reason.** An mcpp-built program runs under mcpp's own private loader, which does
not consult `/usr/lib`, so a bare-soname `dlopen` from inside the program finds nothing. Anything the host must
supply — the NVIDIA driver, a Vulkan ICD — is reached by an index package that puts a directory on the artifact's
runtime search path. A project declares it as an ordinary dependency and does not otherwise think about it.

WARNING: **the runtime adapters are a Linux construction.** macOS (dyld) and Windows (the PE loader) have no such
layer by construction, and a project targeting them declares no adapter
[docs/42-heterogeneous-builds.md:818-824].

Everything else is a payload. Which package and how old it may be belongs to the **rule**; *exactly which version* is
the project's to override and nobody's to discover from the machine.

## 2. `examples/09-heterogeneous`, walked

Seven sub-examples, each computing `2.0 * [1,2,3,4] + [10,20,30,40]` = `12 24 36 48`
[examples/09-heterogeneous/README.md:1-7]. The numbers are deliberately identical everywhere, which is why every
example also prints the device it used: without a name in the output, a run that silently fell back to the CPU is
indistinguishable from a device run, and each backend fills that in **only after a successful call**
[examples/09-heterogeneous/README.md:46-54].

| directory | model | `[build] accel` | rule feature | boundary | what the machine needs |
|---|---|---|---|---|---|
| `boundary/` | none — a C island | *(absent)* | `tools-island` | generated, L0 | **nothing** |
| `cuda/` | CUDA | `cuda12.9+{sm_89} ptx>=89` | `rules-cuda`, `tools-island` | generated, L1 | NVIDIA driver for the device leg |
| `vulkan/` | Vulkan compute | `vulkan1.2` | `rules-spirv` | hand-written, L3 | **nothing** — `xim:mesa-lavapipe` is a CPU device |
| `sycl/` | SYCL | `sycl, cuda12.9+{sm_89}` | `rules-sycl`, `tools-island` | generated, L1 | an NVIDIA device for the device leg |
| `hip/` | HIP (NVIDIA platform) | `hip, cuda12.9+{sm_89}` | `rules-hip` | hand-written, L3 | NVIDIA driver for the device leg |
| `cann/` | Ascend C | `ascend8.5+{dav-c220}` | `rules-ascendc` | hand-written, L3 | Ascend NPU **to run**; compiles anywhere |
| `multi-backend/` | CUDA **and** Vulkan | *(absent — opt in)* | `rules-cuda`, `rules-spirv` | hand-written | nothing by default |

Read `boundary/` first: it needs no device and isolates the interface between an island and the C++ side. Then
`cuda/`, which adds the device compiler and a seam over that boundary. The four beside `cuda/` assume it, and
`multi-backend/` assumes two of them [examples/09-heterogeneous/README.md:19-28].

### 2.1 `boundary/` — the whole mechanism, with no device at all

```
examples/09-heterogeneous/boundary/
├── mcpp.toml                 one dependency edge
├── build.mcpp                scan the root, emit the boundary
└── src/
    ├── main.cpp              import boundary.kernels;
    └── kernels/
        ├── saxpy.c           the island
        └── vec/scale.c       a second island, one directory deeper
```
[examples/09-heterogeneous/boundary/README.md:15-23]

**The complete manifest** [examples/09-heterogeneous/boundary/mcpp.toml:1-14]:

```toml
[package]
name    = "boundary"
version = "0.1.0"

[language]
standard = "c++23"

# `tools-island` is not a device rule: it claims no extension and names no rule
# module, so the edge states `host-module = true` itself.
[build-dependencies.mcpp]
plugins = { version = "0.5.2", features = ["tools-island"], host-module = true }

[build]
sources = ["src/*.cpp", "src/kernels/**/*.c"]
```

**The complete build program** [examples/09-heterogeneous/boundary/build.mcpp:16-45]:

```cpp
import std;
import mcpp;
import mcpp.tools.island;

int main() {
    mcpp::tools::island::options opt;
    opt.module_name  = "boundary.kernels";
    opt.out_dir      = std::string(mcpp::out_dir()) + "/island";
    opt.produced_by  = "the boundary example";
    opt.roots        = { std::string(mcpp::manifest_dir()) + "/src/kernels" };
    opt.strip_prefix = "boundary_";

    const auto entries = mcpp::tools::island::scan(opt);
    if (!entries) return 1;
    const auto out = mcpp::tools::island::emit(*entries, opt);
    if (!out) return 1;

    // `cflag`, not `cxxflag`: the island is C, and forcing a header into every
    // C++ translation unit would put declarations ahead of a module interface's
    // `export module` line, which is ill-formed.
    for (auto const& f : mcpp::tools::island::force_include_flags(
             out->header_file, mcpp::compiler()))
        mcpp::cflag(f.c_str());
    mcpp::generated(out->interface_file.c_str());
    return 0;
}
```

**Run it:**

```bash
cd examples/09-heterogeneous/boundary
mcpp run                 # 6 12 18 24
```
[examples/09-heterogeneous/boundary/README.md:6-9]

The island here is an ordinary `.c` file, and that is the **only** simplification. What makes it an island is the
property the boundary exists for: it is compiled separately, it cannot import a module, and its interface is
`extern "C"`. Substituting a `.cu` and a device rule is what `../cuda` shows, and nothing about the boundary changes
[examples/09-heterogeneous/boundary/README.md:84-90].

**What `mcpp.tools.island` writes**, into the build directory, from entry points marked `MCPP_EXPORT_C`
[examples/09-heterogeneous/boundary/README.md:25-51]:

```cpp
// generated
module;
#include "boundary.kernels.h"
export module boundary.kernels;

export namespace boundary::kernels {
using ::boundary_ran_on;
inline constexpr auto ran_on = boundary_ran_on;
using ::boundary_saxpy;
inline constexpr auto saxpy = boundary_saxpy;
}

export namespace boundary::kernels::vec {
using ::boundary_scale;
inline constexpr auto scale = boundary_scale;
}
```

Re-exporting names rather than restating signatures is what lets the generator work **without a C parser**: it needs
only the identifier before the `(`. It is also why no second copy of a signature exists.

**The naming rule, and it is one rule for both lanes** [docs/42-heterogeneous-builds.md:223-259]:

> The module name is the root. Each directory below the group's base extends the **namespace**. The leaf identifier is
> decided by the lane: the data lane derives it from the file name, because a payload has no name of its own; the
> island lane takes the entry point's name, because the author wrote one.

| written | reached as |
|---|---|
| `[package] name = "myapp"` | module root `myapp` |
| `shaders/scale.comp` | `myapp::shaders::scale_comp()` |
| `shaders/a/scale.comp` | `myapp::shaders::a::scale_comp()` |
| `myapp_saxpy` in `kernels/saxpy.cu` | `myapp::kernels::myapp_saxpy(...)` |
| `myapp_blur` in `kernels/image/blur.cu` | `myapp::kernels::image::myapp_blur(...)` |

The root is the **package's** name with non-identifier characters replaced, not its directory's. On the island lane
the **file name reaches nothing**: an entry point already carries a name its author wrote, and two entry points
sharing one are one symbol whatever directory each sits in — so moving a function between two files in one directory
renames nothing a consumer wrote.

`strip_prefix` is a **spelling, not a second entity**: it emits `inline constexpr auto blur = app_blur;` beside
`using ::app_blur;`. The authored name stays canonical — it is the symbol, and it is what `nm`, a link error, a
profiler and `dlsym` show [docs/42-heterogeneous-builds.md:333-338].

**The three refusals the generator performs** [docs/42-heterogeneous-builds.md:320-331]:

| situation | why it is refused |
|---|---|
| one name declared twice in **one** root | C linkage does not mangle, so those are one symbol; a namespace that appeared to separate them would promise an isolation the linker does not provide |
| one name in **several** roots whose declarations differ | that is one entry point implemented several times, and the declarations must agree verbatim — the check nothing else in the toolchain can perform |
| roots that **overlap**, or a root with no marked entry point | a file reachable from both has two namespace paths; an empty module fails later and less clearly than a misspelled path does here |

### 2.2 The four rungs, and what each costs

[docs/42-heterogeneous-builds.md:340-360; examples/09-heterogeneous/boundary/README.md:92-113]

| rung | written by hand | the consumer writes | the consumer gets | examples |
|---|---|---|---|---|
| **L0** | nothing but the marked entry points | `import boundary.kernels` | the island's own C-shaped interface: pointers and a count | `boundary/` |
| **L1** | a seam module over the generated one | `import app.saxpy` | the interface the project designed | `cuda/`, `sycl/` |
| **L2** | a seam, plus entries built with `island::declared` | the same | the same, for entry points a scan cannot see | — |
| **L3** | the header and the module | the same | the same, with the signature written twice | `hip/`, `vulkan/`, `cann/` |

**What L0 does not have**: the interface is C-shaped (`boundary::kernels::saxpy(2.0f, x, y, out, 4)` rather than a
span), and there is **no place for a `cfg(accelerator = …)` section to apply**, because a seam is the single point at
which one implementation is exchanged for another. A project with one island and one backend can stop at L0; a
project that will swap backends needs L1.

**Neither the generated nor the hand-written form is deprecated.** A project whose boundary is stable, or whose island
is compiled somewhere mcpp cannot reach, writes the header; the generated form is the default because the copy it
removes is the one that goes wrong silently [examples/09-heterogeneous/hip/README.md:39-41].

The failure a hand-written header permits, written out
[docs/42-heterogeneous-builds.md:160-191]:

```cpp
// the seam
extern "C" int saxpy_device(float a, const float* x, const float* y,
                            float* out, unsigned n);
// the island, after someone widened the count
extern "C" int saxpy_device(float a, const float* x, const float* y,
                            float* out, std::size_t n);
```

C language linkage does not mangle, so those are **one symbol**. The link is clean, each side reads the arguments by
its own ABI: no compile error, no link error, and a run that reads past the end of the arguments. The same mistake
across a C++ boundary is caught by mangling at link time.

### 2.3 `cuda/` — a device compiler behind a seam

```
examples/09-heterogeneous/cuda/app/
├── mcpp.toml
├── build.mcpp                 hands the device sources to `mcpp.rules.cuda`
└── src/
    ├── main.cpp               an ordinary consumer; imports the seam, never sees a header
    ├── app.cppm               the seam: turns the C interface back into a C++ one
    ├── kernels/saxpy.cu       the island
    └── cpu/saxpy.cpp          the same interface for the host
```
[examples/09-heterogeneous/cuda/README.md:7-24] — note there is **no header in this source tree**; the `extern "C"`
boundary and the module over it are generated.

**The complete manifest**, comments condensed [examples/09-heterogeneous/cuda/app/mcpp.toml:1-79]:

```toml
[package]
name         = "cuda-saxpy"
namespace    = "example"
version      = "0.1.0"
description  = "A CUDA kernel behind a seam module, with a CPU fallback"
accelerators = ["cuda"]

[language]
standard   = "c++23"
modules    = true
import_std = true

# The primary route is clang: the toolchain's own clang++ compiles the device
# unit (`-x cuda`), so there is no second host compiler and no host-compiler
# bound to satisfy. With a GCC toolchain the rule takes the nvcc route instead.
[toolchain]
default = "llvm@22.1.8"

[build-dependencies.mcpp]
plugins = { version = "0.5.2", features = ["rules-cuda", "tools-island"], host-module = true }

# The driver's userspace library, reached through an index package. mcpp's
# private loader does not consult /usr/lib, so without it the statically linked
# CUDA runtime cannot dlopen the driver.
[dependencies.compat]
cuda-driver = "2026.09.05"

# NO [xlings.workspace]: the toolkit is declared by the rule itself.

[build]
accel = "cuda12.9+{sm_89} ptx>=89"
sources = [
  "src/*.cppm",
  "src/*.cpp",
  { glob = "src/kernels/**/*.cu", accel = "cuda12.9+{sm_89}" },
]
# NO include_dirs: this project has no header of its own.

[target.'cfg(accelerator = "cuda")'.build]
ldflags = ["-lcudart_static", "-lrt", "-lpthread", "-ldl"]

[target.'cfg(not(accelerator = "cuda"))'.build]
sources = ["src/cpu/*.cpp"]

[targets.cuda-saxpy]
kind = "bin"
main = "src/main.cpp"
```

**The build program's essential half** [examples/09-heterogeneous/cuda/app/build.mcpp:34-101]:

```cpp
import std; import mcpp; import mcpp.tools.island; import mcpp.rules.cuda;

static std::optional<mcpp::tools::island::emitted> generate_boundary() {
    const std::string root = std::string(mcpp::manifest_dir());
    mcpp::tools::island::options opt;
    opt.module_name = "app.kernels";              // the seam is `app.saxpy`
    opt.out_dir     = std::string(mcpp::out_dir()) + "/island";
    // TWO ROOTS, named UNCONDITIONALLY: both trees exist on disk in either
    // build, and which one compiles is the manifest's decision.
    opt.roots       = { root + "/src/kernels", root + "/src/cpu" };
    opt.layout_root = root + "/src/kernels";      // this one supplies the shape
    const auto entries = mcpp::tools::island::scan(opt);
    if (!entries) return std::nullopt;
    auto out = mcpp::tools::island::emit(*entries, opt);
    if (!out) return std::nullopt;
    mcpp::include_dir(out->include_dir.c_str());  // the host half #includes it
    mcpp::generated(out->interface_file.c_str());
    return out;
}

int main() {
    const auto boundary = generate_boundary();
    if (!boundary) return 1;
    mcpp::rerun_if_env_changed("MCPP_EXAMPLE_CUDA_ROUTE");
    mcpp::rules::cuda::options opt;
    // These flags go on the DEVICE compiler's command line, not mcpp::cxxflag.
    opt.flags = mcpp::tools::island::force_include_flags(boundary->header_file,
                                                        mcpp::compiler());
    return mcpp::rules::cuda::compile(opt) ? 0 : 1;
}
```

**Run it:**

```bash
cd examples/09-heterogeneous/cuda/app
mcpp run                 # on the device
mcpp run --no-accel      # the same numbers, on the CPU
```

Measured on an NVIDIA RTX 4080 (compute capability 8.9), driver 550.144.03 reporting CUDA 12.4, LLVM 22.1.8
[examples/09-heterogeneous/cuda/README.md:213-235]:

```
$ mcpp run
     Running `target/x86_64-linux-gnu/<accel>/bin/cuda-saxpy`
12 24 36 48

$ mcpp run --no-accel
     Running `target/x86_64-linux-gnu/<host>/bin/cuda-saxpy`
12 24 36 48
```

The two artifact directories differ, and the CPU one contains no `cudaMalloc`.

**What has to be on the machine, and what does not.** The toolkit does not: the rule declares nvcc, cudart, cuRAND's
headers, CCCL and the driver sentinel **for itself**, under `cfg(accelerator = "cuda")` and the feature that selects
it, so a build naming no accelerator installs none of them
[examples/09-heterogeneous/cuda/README.md:95-123]. What does is the **driver**, which is not redistributable and is in
ABI lockstep with the kernel module. Two packages reach it, one per layer:

- `xim:libcuda-host-link` owns *where the host's copy is* — it installs a symlink to whatever the machine has, so
  every GPU consumer reads one path instead of reimplementing an `ldconfig` probe;
- `compat.cuda-driver` owns how a **built artifact** reaches it, by declaring a directory on the artifact's runtime
  search path.

Without the second the program builds and links, then reports
`cudaMalloc: CUDA driver version is insufficient for CUDA runtime version`, which is what the runtime says when it
cannot open the driver at all [examples/09-heterogeneous/cuda/README.md:237-267].

**The rule reports two machine facts through the build program's own channel, and mcpp compares them**
[examples/09-heterogeneous/cuda/README.md:184-211]:

```
mcpp:fact=cuda.driver=12.4
mcpp:floor=cuda.driver >= 12.0
```
```
error: `cuda-saxpy` requires cuda.driver >= 13.0, and this machine has 12.4.
```

A separate advisory covers PTX: embedded PTX emitted by a toolkit newer than the driver cannot be JIT-compiled by it,
so hardware outside the named architecture set will not run — the named architectures still do, so it is a **warning**
rather than a refusal.

**Two routes, and why the default is clang** [examples/09-heterogeneous/cuda/README.md:133-182]:

- **clang** (`-x cuda --cuda-path=<payload>`) is what `[toolchain] default = "llvm@22.1.8"` selects. The compiler that
  builds the rest of the project builds the device unit too: no second host compiler, no host-compiler bound. It does
  pass one NVIDIA flag of its own — a device unit including `<cuda_runtime.h>` otherwise stops at
  `crt/host_defines.h:67` with `"libc++ is not supported on x86 system"`, because that guard reads `__CUDACC__`,
  which clang defines when compiling CUDA — so the rule passes `-D_ALLOW_UNSUPPORTED_LIBCPP` **on this route only**.
- **nvcc** (`-ccbin <host g++>`) is taken when the project's toolchain is GCC, and drives a second compiler.

`MCPP_EXAMPLE_CUDA_ROUTE=clang|nvcc` overrides the choice, and the rule declares `rerun_if_env_changed` for it.

Two pairings nvcc cannot have, both stated **before** the compile:

| pairing | what happens, and the way out |
|---|---|
| a host compiler past nvcc's bound | the rule reads the maximum GCC major from `crt/host_config.h`, uses the project's toolchain when it fits, else a `xim:gcc` payload the project declared, else refuses naming the declaration to add. Measured: GCC 16 under nvcc 12.9 fails inside GCC's own `<type_traits>` **even with** `-allow-unsupported-compiler` — that escape hatch admits a compiler one step past the bound, not a standard library two majors newer |
| an old toolkit and a new C library | toolkit 12.9's `crt/math_functions.h` redeclares the C23 `cospi`, `sinpi`, `rsqrt` for the host **without** `noexcept`; glibc 2.41+ declares them with it, and since C++17 that is part of the function type. Six `exception specification is incompatible` errors and no decision. The rule reads the C library's `bits/mathcalls.h` through `mcpp::toolchain_sysroot()` and refuses the pair, naming the 13.x toolkit as the way out |

A second compiler also has to be told where it is: `mcpp::toolchain_sysroot()` and `mcpp::toolchain_binutils_dir()`
are the `--sysroot` and `-B` mcpp passes to its own compiler, and without forwarding them NVIDIA's
`crt/host_config.h` stops at `features.h: No such file or directory`.

WARNING: **the payload's headers have to be named.** nvcc adds `<its own directory>/../include` by itself, and on the
12.x line that holds `crt/` but **not** `cuda_runtime.h`, which lives in the `cuda-cudart` component. An earlier
revision of the rule left it out, nvcc resolved `cuda_runtime.h` from `/usr/include`, then read the host's
`crt/host_config.h` beside it — and the build failed with the *host* toolkit's complaint while using the *payload's*
compiler [examples/09-heterogeneous/cuda/README.md:125-131].

Hermeticity check worth copying [examples/09-heterogeneous/cuda/README.md:120-123]:

```bash
mcpp build -v | grep -c '/usr/local/cuda\|/usr/bin/nvcc'     # expected: 0
```

### 2.4 `vulkan/` — the other lane: the device output is data, not an object

```
examples/09-heterogeneous/vulkan/app/
├── mcpp.toml
├── build.mcpp                  hands the shaders to `mcpp.rules.spirv`
├── include/saxpy/saxpy.h       the island's interface — WRITTEN BY HAND here
├── shaders/scale.comp          the island: GLSL, compiled by glslang
└── src/
    ├── main.cpp                an ordinary consumer
    ├── app.cppm                the seam
    ├── vulkan/saxpy.cpp        the host side: Vulkan calls
    └── cpu/saxpy.cpp           the same interface for the host
```
[examples/09-heterogeneous/vulkan/README.md:9-27]

**The complete manifest**, comments condensed [examples/09-heterogeneous/vulkan/app/mcpp.toml:1-69]:

```toml
[package]
name         = "vulkan-saxpy"
namespace    = "example"
version      = "0.1.0"
accelerators = ["vulkan"]

[language]
standard   = "c++23"
modules    = true
import_std = true

[build-dependencies.mcpp]
plugins = { version = "0.5.2", features = ["rules-spirv"], host-module = true }

# The Khronos loader, built by the index rather than taken from the host, and
# the adapter that makes the host's own ICDs reachable from a binary running
# under mcpp's private loader. Neither one is a driver.
[dependencies.compat]
vulkan         = "1.4.357.0"
vulkan-runtime = "2026.09.11"

# ONE payload, and the shader compiler is not it: `mcpp.rules.spirv` declares
# `xim:glslang` for itself. What stays is a DEVICE.
[xlings.workspace]
"xim:mesa-lavapipe" = "26.2.1"

[build]
accel = "vulkan1.2"
sources = [
  "src/*.cppm",
  "src/*.cpp",
  { glob = "shaders/*.comp", accel = "vulkan1.2" },
]
include_dirs = ["include"]

[target.'cfg(accelerator = "vulkan")'.build]
sources = ["src/vulkan/*.cpp"]

[target.'cfg(not(accelerator = "vulkan"))'.build]
sources = ["src/cpu/*.cpp"]

[targets.vulkan-saxpy]
kind = "bin"
main = "src/main.cpp"
```

**The complete build program** [examples/09-heterogeneous/vulkan/app/build.mcpp:19-28]:

```cpp
import std; import mcpp; import mcpp.plugins; import mcpp.rules.spirv;

int main() {
    mcpp::rerun_if_changed_glob("shaders/**/*.comp");
    mcpp::rerun_if_changed_glob("shaders/**/*.glsl");

    mcpp::rules::spirv::options opt;
    opt.includes = { "shaders" };          // a shader may #include another
    opt.surface  = mcpp::plugins::surface::kind::module_;
    return mcpp::rules::spirv::compile(opt) ? 0 : 1;
}
```

**Run it:**

```bash
cd examples/09-heterogeneous/vulkan/app
mcpp run                # whatever device the loader finds
mcpp run --no-accel     # the CPU implementation behind the same seam
```

**This is the one example whose DEVICE leg runs on a machine with no GPU.** The same binary was measured on three
[examples/09-heterogeneous/vulkan/README.md:63-74]:

| where | how | output |
|---|---|---|
| NVIDIA RTX 4080 | the host's own ICD, through `compat.vulkan-runtime` | `12 24 36 48` |
| CPU (`llvmpipe`) | `xim:mesa-lavapipe`, a payload, with `VK_DRIVER_FILES` naming only it | `12 24 36 48` |
| no device at all | `mcpp build --no-accel`, the CPU implementation behind the seam | `12 24 36 48` |

The middle row is why the payload exists: a machine with no GPU — every CI runner in this ecosystem — still has a
Vulkan device, so the Vulkan lane is something a test can assert on. Select it explicitly with
`VK_DRIVER_FILES=<payload>/share/vulkan/icd.d/lvp_icd.x86_64.json`
[examples/09-heterogeneous/vulkan/app/mcpp.toml:33-38].

**Three differences from the island lane, and all three are the point of this example:**

1. **The device output is a header (or a module), not an object.** A SPIR-V module is *data* the program hands to
   `vkCreateShaderModule`. `mcpp.rules.spirv` submits its actions with `role = "source"` — the one role the engine
   orders **before** compilation — and adds the directory it writes to the include path, so the artifact carries its
   shaders, `mcpp pack` has nothing further to collect, and the program reads no file at run time. An `artifact` role
   would not do: its outputs are ordered against the **link**, which is after the translation unit that includes the
   header is compiled [examples/09-heterogeneous/vulkan/README.md:52-62].
2. **The interface is generated and named by nobody.** `opt.surface = module_` makes the rule write a module rather
   than a header, so this project names no generated file. `src/vulkan/saxpy.cpp` used to open with
   `#include "scale_comp.h"` — a name no line in the project produced and no reader could derive without opening the
   rule. The module name defaults to `<package with '-' as '_'>.shaders`, so `shaders/scale.comp` is reached as
   `vulkan_saxpy::shaders::scale_comp()` [examples/09-heterogeneous/vulkan/app/build.mcpp:6-18]. The accessor answers
   with **the address and the byte count together**: `sizeof` is not merely awkward at this boundary, it is
   unanswerable, because the words may be in an object rather than an array
   [docs/42-heterogeneous-builds.md:257-260].
3. **`vulkan1.2` carries no architecture set, and that is not an omission.** SPIR-V is the portable form and which
   device executes it is decided by the driver when the program runs; a rule demanding an architecture would be
   inventing a requirement its device API does not have. `vulkan1.2` reaches `--target-env` the same way `sm_89`
   reaches `-gencode` [examples/09-heterogeneous/vulkan/README.md:44-48].

**Where the split between project and rule falls**: a rule declares what it needs to **compile** (`xim:glslang` on
Linux, `xim:shaderc` on macOS/Windows); a project declares what it needs to **run** (the software device). A rule
that shipped a software renderer would force one onto every consumer that has a GPU
[examples/09-heterogeneous/vulkan/README.md:84-89].

This example shows **no graphics**: no swapchain, no window, no surface. The device API is here for compute, which is
the half a build system has to carry; a shader that draws is compiled by exactly the same rule
[examples/09-heterogeneous/vulkan/README.md:91-95]. `examples/10-graphics/offscreen` is the rendering one
[docs/03-examples.md:76].

### 2.5 `sycl/` — a second compiler with its own standard library

Layout is `cuda/`'s, one file name apart: `src/kernels/saxpy.sycl` in place of `saxpy.cu`
[examples/09-heterogeneous/sycl/README.md:7-28]. **That is the point of the example** — SYCL is a different
compilation model and reaches the build through the same seam, the same constrained glob and the same rule mechanism.

The manifest differs from `cuda/`'s in exactly three places
[examples/09-heterogeneous/sycl/app/mcpp.toml:1-84]:

```toml
[package]
accelerators = ["sycl", "cuda"]        # BOTH: the glob below names the NVIDIA target

[build-dependencies.mcpp]
plugins = { version = "0.5.2", features = ["rules-sycl", "tools-island"], host-module = true }

[dependencies.compat]
sycl-runtime = "2026.09.11"            # not cuda-driver: see below

[build]
# Two chunks: the programming model, and the device. Written `sycl` alone, the
# unit compiles to SPIR-V and the runtime picks a device at run time; with the
# second chunk it is compiled ahead of time for that architecture.
accel = "sycl, cuda12.9+{sm_89}"
sources = [
  "src/*.cppm", "src/*.cpp",
  { glob = "src/kernels/**/*.sycl", accel = "sycl, cuda12.9+{sm_89}" },
]

[target.'cfg(not(accelerator = "sycl"))'.build]
sources = ["src/cpu/*.cpp"]
```

**Run it** [examples/09-heterogeneous/sycl/README.md:116-126]:

```bash
mcpp build                 # ahead of time for sm_89, through the dpcpp payload
mcpp run                   # 12 24 36 48, on the device
mcpp build --no-accel      # the constrained glob is left out
mcpp run --no-accel        # 12 24 36 48, from src/cpu/saxpy.cpp
```

**What makes a `.sycl` file a device unit is not its content.** Open it and it is ordinary C++ — no `__global__`, no
launch syntax. What makes it a device translation unit is that it goes to a compiler with a device back end, which
mcpp does not drive and which does not accept C++20 modules. Naming it `.cpp` and routing it by glob was possible and
was **rejected**: one extension would then mean two things depending on which glob matched first
[examples/09-heterogeneous/sycl/README.md:30-41].

**Two edges per build, not one per source.** A SYCL object carries its device image and nothing registers that image
with the runtime; the registration comes from a **device link** (`-fsycl-link`) that reads every device object and
emits one further host object. So the rule submits one action per source *and* one that consumes their outputs, and
the engine orders them by the graph rather than by declaration order. Without the second, the program links, starts,
and finds no kernel [examples/09-heterogeneous/sycl/README.md:43-51].

**Five payloads, none declared by the project** [examples/09-heterogeneous/sycl/README.md:53-71]:

```toml
"xim:dpcpp"         = ">=7.1.0"   # the compiler: its clang has the SYCL front end
"xim:gcc"           = "15.1.0"    # the C++ standard library the unit compiles against
"xim:glibc"         = ""          # …and the C library underneath it, unpinned
"xim:linux-headers" = ""
"xim:cuda-nvcc"     = "12.9.86"   # the NVIDIA back end's libdevice, only when accel names cuda
```

`xim:gcc` is **not a second toolchain**. Left alone, the SYCL compiler takes its C++ standard-library headers from the
host's GCC and finds the host's CUDA installation the same way — and neither says anything when it happens, being
visible only in the compiler's own include search list and only on a machine that has those directories. That is why
the rule refuses without them and names the line to add. The C library entries are **unpinned deliberately**: the
version is the runtime binding's choice, not the project's, and a pinned entry resolves for exactly that version or
for nothing [examples/09-heterogeneous/sycl/app/mcpp.toml:42-57].

**Two C++ runtimes in one image, and the seam is what makes it safe**
[examples/09-heterogeneous/sycl/README.md:73-114; docs/42-heterogeneous-builds.md:679-700]:

`libsycl.so` is compiled against libstdc++ while an mcpp artifact links libc++, so both are in the image. The
unwinder is the one part a `catch` cannot police. Measured on this lane: **ten of libgcc's eighteen `_Unwind_*` entry
points came from the artifact and eight stayed in libgcc_s**, including the accessors a personality routine uses — so
libstdc++'s personality read an LLVM libunwind context through libgcc's accessors, found no landing pad, and called
`std::terminate` past a handler three frames up. The program was correct until something threw.

mcpp's fix: when the link line names libstdc++ and the toolchain's own library is libc++, link the unwinder from
libgcc (`--unwindlib=libgcc`) instead of the payload's `libunwind.a`, and hide the static archives' symbols with
`--exclude-libs`. libgcc_s is already in the process, so this **names** a library rather than adding one.

Three things were needed to make "nothing crosses the seam" true, and only two are a `catch`:

- the catch sits **inside** the buffer scope, because a `sycl::buffer` destructor blocks until the work reading it
  finishes, and unwinding through three of those is a second throw during unwinding;
- the queue takes an **asynchronous handler**, because a queue constructed without one gets the default handler, and
  the default handler calls `std::terminate` — which no `catch` can intercept;
- **one unwinder in the process.** Measured on one machine, same source, same device: with two unwinders, exit 134
  and no output; with one, `sycl: The program was built for 1 devices` followed by `device unavailable`, exit 1.

Example 09's island can promise not to touch the standard library at all; this one cannot — **SYCL *is* a C++
library** — so the discipline moves from "no standard library" to "nothing crosses". The island catches its own
`sycl::exception` and returns a code.

### 2.6 `hip/` — the same computation, with the boundary written by hand

```
examples/09-heterogeneous/hip/app/
├── mcpp.toml
├── build.mcpp
├── include/saxpy/saxpy.h      extern "C", no std types — WRITTEN BY HAND
└── src/{main.cpp, app.cppm, kernels/saxpy.hip, cpu/saxpy.cpp}
```
[examples/09-heterogeneous/hip/README.md:7-18]

**The entire build program** [examples/09-heterogeneous/hip/app/build.mcpp:1-9]:

```cpp
import std; import mcpp; import mcpp.rules.hip;

int main() {
    mcpp::rules::hip::options opt;
    opt.includes = { "include" };
    return mcpp::rules::hip::compile(opt) ? 0 : 1;
}
```

Nine lines, because the boundary is a file in the source tree rather than something to generate. The manifest is
`cuda/`'s with `accel = "hip, cuda12.9+{sm_89}"`, `features = ["rules-hip"]`, `include_dirs = ["include"]`, and the
same `[dependencies.compat] cuda-driver` [examples/09-heterogeneous/hip/app/mcpp.toml:1-65].

```bash
mcpp build                 # sm_89, through mcpp.rules.hip
mcpp run                   # 12 24 36 48, on the device
mcpp run --no-accel        # 12 24 36 48, from src/cpu/saxpy.cpp
```

**Two chunks in `accel`, and the second is character for character what `cuda/` writes.** The first names the
programming model, the second names the device — so a device has **one** spelling in this ecosystem however many
models reach it, and `sm_89` does not acquire a second one because the file is called `.hip`
[examples/09-heterogeneous/hip/README.md:77-87].

**HIP on the NVIDIA platform is a header layer, not a second runtime.** Every entry point is an inline wrapper over
the CUDA one — `hipMalloc` resolves to `cudaMalloc` through the header, `hipError_t` is `cudaError_t` under a typedef
— so the object links against the CUDA runtime and nothing of ROCm's. Three consequences, all visible in the
manifest: the compiler is the project's own clang invoked `-x cuda` with `-D__HIP_PLATFORM_NVIDIA__`;
`xim:hip-nvidia` **contains no binaries**, because on this platform there are none to contain; and the payloads are
CUDA's [examples/09-heterogeneous/hip/README.md:48-64].

**The AMD platform is refused by name**, with the reason: it needs a ROCm runtime and device library this ecosystem
does not publish, so compiling for it would produce an object nothing on the machine can link or run. That refusal is
the honest answer; the alternative is a build that succeeds and an artifact that does not
[examples/09-heterogeneous/hip/README.md:89-94].

WARNING: **`hipcc` is deliberately not used.** It is a driver that reads `HIP_PLATFORM`, picks nvcc or amdclang and
forwards — every decision it makes is one the rule has already made from the declaration, and it would make them again
from the environment [examples/09-heterogeneous/hip/README.md:72-75].

One payload in this lane exists because CI found it missing: `nvidia_hip_runtime_api.h` includes
`<cuda_profiler_api.h>` on its **second line**, and CUDA ships that header in a separate component — so a machine
with a host CUDA installation supplies it from `/usr/include` and the build works while depending on something it
never declared [examples/09-heterogeneous/hip/README.md:66-70]. That class of bug is exactly what the
declare-everything discipline is for.

### 2.7 `cann/` — a vendor outside the NVIDIA and Khronos lineages

`op_kernel/` beside `op_host/` is how CANN's own operator libraries are already laid out — every operator in
`ops-math` splits that way on disk. The island is therefore **not a shape mcpp imposes on Ascend**; it is the shape
Ascend already has [examples/09-heterogeneous/cann/app/README.md:1-11].

Manifest differences from `cuda/` [examples/09-heterogeneous/cann/app/mcpp.toml:1-65]:

```toml
[package]
accelerators = ["ascend"]

[build-dependencies.mcpp]
plugins = { version = "0.5.2", features = ["rules-ascendc"], host-module = true }

[build]
accel = "ascend8.5+{dav-c220}"         # dav-c220 is the device architecture
sources = [
  "src/*.cppm", "src/*.cpp",
  { glob = "src/kernels/*.asc", accel = "ascend8.5+{dav-c220}" },
]
include_dirs = ["include"]

# `accelerator = "none"` rather than `not(accelerator = "ascend")`.
[target.'cfg(accelerator = "none")'.build]
sources = ["src/cpu/*.cpp"]

# The HOST half: launches the kernel through ACL, declines when no NPU is
# present -- which is every machine that is not an Ascend one.
[target.'cfg(accelerator = "ascend")'.build]
sources = ["src/ascend/*.cpp"]
ldflags = ["-lascendcl"]
```

```bash
mcpp run --no-accel                        # builds and runs
mcpp build --accel "ascend8.5+{dav-c220}"  # compiles the kernel, links, then
                                           # stops on the missing driver
```

**Measured on an x86_64 machine with no Ascend hardware and no Ascend driver**
[examples/09-heterogeneous/cann/app/README.md:15-50]:

| step | result |
|---|---|
| `xim:cann-toolkit` provisioned | **2.9 GB**, no root, no driver |
| `build.mcpp` compiles and runs | `mcpp.rules.ascendc` imported from `mcpp:plugins` |
| the kernel compiles | `bisheng -x asc --cce-aicore-arch=dav-c220` |
| the object joins the ordinary link | mixed mode: an x86-64 object carrying the device binary |
| the host half links | ACL, plus the six-library closure the rule names |
| the runtime-closure check | names `libascend_hal.so` and nothing else (2026.9.6.6+) |
| **the artifact starts** | **no** — `libascend_hal.so` is missing |
| `--no-accel` | builds and runs: `12 24 36 48`, `device: cpu` |

`libascend_hal.so` belongs to the **driver**, not the toolkit, and plays the role `libcuda.so.1` plays for CUDA. A
device build of this example therefore completes everywhere and *runs* only on an Ascend machine. The payloads are
gated on the accelerator, so `mcpp run --no-accel` installs nothing: the CPU leg costs a C++ compile and no download.

The closure row is a measurement that once disagreed with the loader: before 2026.9.6.6 mcpp named **eight**
libraries and the artifact resolved seven, because the toolkit's shared libraries depend on each other by bare SONAME
with no search path while the directory holding them is named once, in the executable's `DT_RPATH` — which is
inherited down the whole chain. The engine now models that, so the refusal names exactly what the loader will fail on.

Two further facts worth carrying:

- **The toolkit turned out to be easy to obtain**, contrary to the design's expectation. Every CANN toolkit from
  8.0.RC1 to 8.5.0 is a plain `.run` on Huawei's own OBS, answering 200 to an anonymous HEAD request, installing
  unattended with `--install --install-path=<dir> --quiet`. Inside it are both halves the lane needs: the device
  compiler at `<arch>-linux/ccec_compiler/bin/{ccec,bisheng}` (clang 15.0.5), and
  `<arch>-linux/simulator/<SoC>/lib/libpem_davinci.so` for **38 SoCs, no hardware required** — which is why the lane
  is verifiable without an NPU, and is the next thing this example should use
  [examples/09-heterogeneous/cann/app/README.md:52-72].
- **The seam is a C function for a measured reason, not a stylistic one.** BiSheng's own launcher for a `__global__`
  function is **C++-mangled even when the kernel is declared `extern "C"`**. Calling it from the host half would make
  the program depend on BiSheng and the project's C++ compiler agreeing about mangling — two different compilers, one
  of them clang 15. The `.asc` file therefore exports an `extern "C"` wrapper and the `<<<…>>>` launch spelling never
  leaves the translation unit the device compiler owns [examples/09-heterogeneous/cann/app/README.md:74-82].

### 2.8 `multi-backend/` — several backends in one artifact, chosen at run time

The other shape from §1.11, in the smallest form that still shows it. Everything above it is **one seam**; this is
**additive** [examples/09-heterogeneous/multi-backend/README.md:1-10].

**The complete manifest**, comments condensed [examples/09-heterogeneous/multi-backend/mcpp.toml:1-160]:

```toml
[package]
name         = "opkit-multi-backend"
namespace    = "example"
version      = "0.1.0"
accelerators = ["cuda", "vulkan"]

[language]
standard = "c++23"; modules = true; import_std = true      # (written as three lines)

[toolchain]
default = "llvm@22.1.8"

# BOTH rules, in one build program.
[build-dependencies.mcpp]
plugins = { version = "0.5.2", features = ["rules-cuda", "rules-spirv"], host-module = true }

# ── payloads and adapters, gated on the device they are for ────────────────
# `cfg(accelerator = ...)` in an `[xlings]` table is what keeps `mcpp build`
# free: a CPU-only build installs neither the CUDA toolkit nor the shader
# compiler. Unconditional pins -- the only spelling before mcpp 2026.9.6.5 --
# would have made the cheapest build the most expensive one.
[target.'cfg(accelerator = "cuda")'.xlings.workspace]
"xim:cuda-nvcc" = "12.9.86"        # the one override in this repository's examples

[target.'cfg(accelerator = "cuda")'.dependencies.compat]
cuda-driver = "2026.09.05"

[target.'cfg(accelerator = "vulkan")'.xlings.workspace]
"xim:mesa-lavapipe" = "26.2.1"

[target.'cfg(accelerator = "vulkan")'.dependencies.compat]
vulkan         = "1.4.357.0"
vulkan-runtime = "2026.09.11"

[build]
# `accel` is deliberately ABSENT, so a plain `mcpp build` is the CPU-only
# variant and needs no payloads at all.
sources = [
  "src/*.cppm",
  "src/main.cpp",
  "src/cpu/*.cpp",
  { glob = "src/backends/cuda/*.cu",     accel = "cuda12.9+{sm_89}" },
  { glob = "src/backends/vulkan/*.comp", accel = "vulkan1.2" },
]
include_dirs = ["include"]

# ── the backends, additive: several may activate at once ───────────────────
[target.'cfg(accelerator = "cuda")'.build]
defines = ["OPKIT_HAVE_CUDA=1"]
ldflags = ["-lcudart_static", "-lrt", "-lpthread", "-ldl"]

[target.'cfg(accelerator = "vulkan")'.build]
sources = ["src/backends/vulkan/*.cpp"]
defines = ["OPKIT_HAVE_VULKAN=1"]

# ── the dispatcher, and neither predicate enumerates ───────────────────────
[target.'cfg(not(accelerator = "none"))'.build]
sources = ["src/dispatch/registry.cpp"]

[target.'cfg(accelerator = "none")'.build]
sources = ["src/dispatch/cpu_only.cpp"]

[targets.opkit-multi-backend]
kind = "bin"
main = "src/main.cpp"
```

**Build it four ways** [examples/09-heterogeneous/multi-backend/README.md:24-42]:

```bash
mcpp run                                          # CPU only, no payloads
mcpp run --accel "vulkan1.2"                      # + the Vulkan island
mcpp run --accel "cuda12.9+{sm_89}"               # + the CUDA island
mcpp run --accel "cuda12.9+{sm_89}, vulkan1.2"    # both, one artifact
```

Measured on a machine with an RTX 4080 and a 12.4 driver — all four print `12 24 36 48`, which is exactly why the
backend is printed first:

| build | prints |
|---|---|
| `mcpp run` | `backend: cpu (only backend in this build)` |
| `--accel "vulkan1.2"` | `backend: vulkan (NVIDIA GeForce RTX 4080)` |
| `--accel "cuda12.9+{sm_89}"` | `backend: cuda` |
| both | `backend: cuda` — the chain's first entry answers |

**Naming a subset is not a mismatch.** `--accel "vulkan1.2"` leaves the `.cu` glob out the way `--no-accel` leaves
both out, and the `cfg(accelerator = "cuda")` section carrying that backend's host half does not activate either, so
the two halves stay together. Only an accelerator this build *does* name whose architecture it does not cover is
refused (mcpp 2026.9.6.5) [examples/09-heterogeneous/multi-backend/README.md:44-48].

**`defines` is what keeps the registry and the compiled sources from drifting apart.** Each backend block carries the
host half **plus** the define that admits it to the dispatcher; the device half is gated by its constrained glob
above, and the two must agree — which is why the define lives beside the host file that implements the entry point
the dispatcher will call [examples/09-heterogeneous/multi-backend/mcpp.toml:123-142].

**The build program, and the one thing two rules change**
[examples/09-heterogeneous/multi-backend/build.mcpp:20-39]:

```cpp
int main() {
    mcpp::rerun_if_changed_glob("src/backends/**/*.cu");
    mcpp::rerun_if_changed_glob("src/backends/**/*.comp");

    mcpp::rules::cuda::options cu;
    cu.includes = { "include" };
    if (!mcpp::rules::cuda::compile(cu)) return 1;

    mcpp::rules::spirv::options sp;
    sp.includes    = { "src/backends/vulkan" };
    sp.surface     = mcpp::plugins::surface::kind::module_;
    sp.module_name = "opkit.shaders";     // named, so the package's modules share a root
    return mcpp::rules::spirv::compile(sp) ? 0 : 1;
}
```

Both rules are called **unconditionally** and neither is told which backends this build named — each parses
`[build] accel` itself and returns immediately when its own is absent, so `mcpp build` with no accel runs both and
compiles nothing. That is also why the order carries no meaning. Each rule takes the device sources whose extension it
claims and leaves the rest: `mcpp::device_sources()` is the package's **whole** device set, so in a build naming both
backends that one list holds a `.cu` and a `.comp` — which is what `mcpp:plugins` 0.2.2 fixed
[examples/09-heterogeneous/multi-backend/README.md:92-105].

A device source **no rule claims is not silently dropped** [src/build/prepare.cppm:10964-10981]:

```
`opkit-multi-backend`: device sources that no action compiles:
         src/backends/metal/saxpy.metal
       A device-kind source is compiled by this package's build program
       and by nothing else -- the engine has no rule for these extensions
       and never will.
       `build.mcpp` ran but declared no action taking them as inputs.
       fix: import the rule package that claims these extensions and
       call it, or drop them from `[build] sources`. A rule that
       compiles a file must also declare it as an action input, or the
       action will not rerun when the file changes.
```

(When the package has no `build.mcpp` at all, the last paragraph is replaced by one naming `mcpp.rules.cuda` for
`.cu` and `mcpp.rules.spirv` for shaders.) Machine channel: `device-source-unconsumed`
[src/build/refusal.cppm:134-135].

**Why this example pins a payload version and the others do not**: `mcpp.rules.cuda` declares the whole toolkit, so
this project would build with no `[xlings.workspace]` at all. The line is kept to show the **escape hatch** working —
the declaration nearer the artifact wins, one version is installed either way, and a pin failing a floor the rule
stated is refused naming both sides. Which CUDA line matters is what makes it a plausible override: a runtime must not
be newer than the driver it will meet, so a project whose machines are older or newer than the rule's default is
exactly the project that should say so [examples/09-heterogeneous/multi-backend/mcpp.toml:68-82].

**The CUDA leg takes the clang route, and the reason is measured**: on the 12.9 line the nvcc route is refused by
nvcc's own front end (the `cospi`/`sinpi`/`rsqrt` `noexcept` clash of §2.3), and driving an older `xim:gcc` payload
does **not** help, because the declarations come from the C library rather than the host compiler — this was tried.
The 13.x line fixes it and raises the driver floor to r580, which is a requirement on the machine rather than a
decision the project gets to make [examples/09-heterogeneous/multi-backend/README.md:63-73].

### 2.9 The lane table

| feature of `mcpp:plugins` | module | compiler it drives | payloads it declares | `[build] accel` |
|---|---|---|---|---|
| `rules-cuda` | `mcpp.rules.cuda` | the project's own clang (`-x cuda`), or nvcc with a GCC toolchain | `xim:cuda-nvcc`, `xim:cuda-cudart`, `xim:libcurand`, `xim:cuda-cccl` | `cuda12.9+{sm_89} ptx>=89` |
| `rules-hip` | `mcpp.rules.hip` | the project's own clang (`-x cuda`), NVIDIA platform | the above plus `xim:hip-nvidia` | `hip, cuda12.9+{sm_89}` |
| `rules-sycl` | `mcpp.rules.sycl` | the `xim:dpcpp` payload's clang (`-fsycl`) | `xim:dpcpp`; on Linux also `xim:gcc`, `xim:glibc`, `xim:linux-headers`; `xim:cuda-nvcc` for an NVIDIA target | `sycl` or `sycl, cuda12.9+{sm_89}` |
| `rules-spirv` | `mcpp.rules.spirv` | `glslangValidator` or `glslc` | `xim:glslang` on Linux, `xim:shaderc` on macOS/Windows | `vulkan1.2` |
| `rules-slang` | `mcpp.rules.slang` | `slangc` | `xim:slang` | `vulkan1.2` |
| `rules-ascendc` | `mcpp.rules.ascendc` | `bisheng` (`-x asc`) from the CANN toolkit | `xim:cann-toolkit` | `ascend8.5+{dav-c220}` |

[docs/42-heterogeneous-builds.md:727-734]

| lane | Linux | macOS | Windows | the deciding factor |
|---|---|---|---|---|
| `rules-spirv` | yes | yes | yes | the shader compiler is published for all three |
| `rules-cuda` | yes | no | yes | NVIDIA has published no macOS toolkit since CUDA 10.2 |
| `rules-sycl` | yes | no | Level Zero and OpenCL only | Intel publishes `sycl_linux` and `sycl_windows` from one tag and nothing for macOS; the CUDA and HIP plugins are not built for Windows |
| `rules-hip` | yes | no | no | the NVIDIA-platform header package is Linux-only; the AMD platform needs a ROCm runtime nobody here publishes |
| `rules-ascendc` | yes | no | no | the CANN toolkit is published for Linux alone |

[docs/42-heterogeneous-builds.md:772-778]

WARNING: **"yes" is three conditions, not a CI run.** It means the device compiler is published for the platform, the
runtime the artifact needs can be reached, and the rule's own host-dependent code compiles there. What has actually
been **RUN** on all three platforms is `rules-spirv` alone (and on Linux it also renders, with pixels compared against
a software rasteriser). The CUDA and SYCL lanes have been **installed and compiled** on Windows with no runner
driving `nvcc` or `dpcpp` end to end [docs/42-heterogeneous-builds.md:780-788].

**A vendor that does not publish for a platform ends the question.** No amount of engine work makes a CUDA toolkit
exist for macOS. What the ecosystem can do is state the boundary at the point where a build asks to cross it — the
SYCL rule refuses an ahead-of-time NVIDIA target on Windows and names the upstream release note that decides it,
rather than compiling something the runtime cannot load [docs/42-heterogeneous-builds.md:790-795].

**Where a lane reaches a platform it reaches it the same way**, and four host differences are the whole of what a rule
does differently: the suffix on a program name (`nvcc` vs `nvcc.exe`); where the libraries are (`lib`/`lib64` on ELF
hosts, `lib/x64` in NVIDIA's Windows layout); which host compiler the device compiler drives (on Windows the CUDA rule
takes its clang route whatever the project's compiler is, because the nvcc route's `-ccbin` accepts only MSVC's
`cl.exe`); and which of the host's libraries have to be kept out (the three SYCL declarations do not exist on Windows,
where there is one C++ runtime and both compilers use it) [docs/42-heterogeneous-builds.md:797-816].

### 2.10 Current limitations of the axis

[docs/42-heterogeneous-builds.md:869-882]

- Device targets, and the device linking (RDC) they imply for the island shape.
- OpenMP `target` offload, and stdpar — §1.10, a property of the model.
- The AMD platform of HIP; `rules-hip` reaches the NVIDIA platform only.
- Metal (`.metal`) and OpenCL C (`.cl`): both are classified as device sources and **no published rule package claims
  either**, so a build naming one is refused naming the file.
- The 13.x CUDA line on Windows; Windows carries the 12.x line.
- `mcpp pack` does not emit the `accel` field (§1.9).

### 2.11 One scaling lesson, from llama.cpp's Vulkan backend

The five lanes prove a rule package can drive five compilers. Whether the mechanism carries something a person would
deploy has a separate answer, measured on `ggml-org:llamacpp`
[docs/42-heterogeneous-builds.md:826-867]:

- **A framework brings its own generator, and the ecosystem should drive it rather than replace it.** llama.cpp
  produces its shaders with a tool it keeps beside the backend that consumes them; a rule package that reimplemented
  the generation would be a second version of that contract, drifting on its own schedule. `mcpp.rules.spirv` exists
  for a project that *writes* shaders; a project that already has a pipeline needs its pipeline **declared**, not
  replaced.
- **Declaring is the whole difference at that scale.** 134 shader sets generated inside a build program are serial,
  run once per prepare, and report a failure as `build.mcpp exited 1`. The same 134 as `mcpp::action` edges are
  incremental, parallel, and each names itself when it fails. The threshold is low — `mcpp.rules.sycl` already
  declares two.
- **A capability probe belongs in the build program, and only once.** Which extensions a shader compiler accepts is a
  property of how it was built, not of its version, and that answer has two readers — the generator and the backend
  source. Asking twice would make one truth into two.
- **The optional backend is a feature, and everything it needs hangs off that feature** (`[feature-deps.<f>]` for
  packages, `[feature-xlings.<f>]` for tools). The criterion is not that the CPU build still works; it is that the
  CPU build's **resolution names no package belonging to the backend**.
- **A software device is not automatically a substitute for hardware.** ggml keeps only Vulkan devices whose type is
  not `eCpu`, so Mesa's lavapipe is excluded for its type alone even though it advertises every feature the backend
  requires. That is the framework's policy, not a packaging defect.

## 3. The build-plugin framework

mcpp's build surface is extended **from packages rather than from releases**, and the engine holds no name that comes
through any extension point [docs/31-authoring-a-rule-package.md:19-44].

### 3.1 The five extension points

| point | effect | declared on |
|---|---|---|
| `mcpp::action` | one edge in the build graph: a command with declared inputs and outputs | a build program, or a rule module it imports |
| `device_extensions` | an extension the engine classifies as a **device source** instead of refusing it | a **feature** of a package |
| `rule_module` | the module a consumer's build program imports to reach the rule | the same feature |
| `tools = [...]` | a generator or compiler **built from source for the build machine**, reached with `mcpp::dep_bin` | a dependency edge |
| `[xlings]`, `[feature-xlings]` | a **prebuilt** tool the rule runs, installed on demand | the package, or one of its features |

What the ecosystem has built out of them [docs/31-authoring-a-rule-package.md:29-43]:

| surface | package | points used |
|---|---|---|
| CUDA, HIP, SYCL, Ascend C | `mcpp:plugins`, one feature each | actions driving a vendor compiler, plus payloads gated on the accelerator |
| Slang | `mcpp:plugins`' `rules-slang` | `device_extensions = [".slang"]` — the first language mcpp supports without naming it in the engine |
| GLSL and HLSL to SPIR-V, and the module over the result | `mcpp:plugins`' `rules-spirv` | one action per shader, plus a generated module |
| the island boundary between a device and C++ | `mcpp.tools.island` | a generator, plus `mcpp::generated` |
| an asset as a linkable object | `examples/08-build-rules` | `role = "object"` |
| a check that can fail the build | `examples/08-build-rules` | `role = "check"` |
| a language the engine has never heard of | `examples/12-a-new-device-language` | `device_extensions`, plus a compiler built through `tools = [...]` |

### 3.2 The three shapes the model expresses

[docs/31-authoring-a-rule-package.md:45-68]

- **A new language, whatever compiles it.** A rule claims the extension, submits one action per source, and declares
  the compiler among that action's inputs. The compiler may be a vendor toolkit, an LLVM front end, an interpreter
  that emits a device binary, or a program the rule package builds from source. Whether it produces a device binary,
  an object or C++ is the action's `role` and nothing else. **The engine never learns the language**: it learns that
  an extension is a device source and that an action claims it.
- **Preprocessing and code generation.** An action with `role = "source"` produces C++ that the declaring package then
  compiles, and every compile edge of that package waits for it. The input can be a template, an interface
  definition, a table, or another action's output — chaining is ordinary, because actions are ordered and
  fingerprinted by their files.
- **A file that is partly C++ and partly another language.** Classification happens **before any rule runs**, so a
  file with an extension the engine owns is compiled as C++ and never reaches a rule. A source carrying a foreign
  block therefore uses an extension the rule claims, and the rule splits it: the C++ it extracts goes through
  `role = "source"`, the foreign half through its own compiler, and the seam between them is the `extern "C"`
  boundary of §2. **No package in the mcpp repository ships that shape today.**

### 3.3 Three boundaries the model will not cross

[docs/31-authoring-a-rule-package.md:70-96]

- **A declaration cannot reclassify what the engine already owns.** A dependency's `device_extensions` is consulted
  *after* the built-in roles, so a rule package cannot claim `.cpp`, `.cppm`, `.c` or `.S` — those are the engine's
  own vocabulary. WARNING: claiming one is **not diagnosed and has no effect**, measured by adding `".cpp"` to a
  rule's `device_extensions`, after which the consumer's `main.cpp` was still compiled as C++ and the build succeeded.
- **Module-interface extensions are the project's axis, not a rule's.** A project spelling its interfaces `.ixx`
  declares `[build] module_extensions`; no rule-package key adds one, because a module interface is scanned for
  imports, produces a BMI and joins the link — three engine behaviours rather than a command to run.
- **An extension in neither table is refused by name**, which is why a mistyped `device_extensions` surfaces at once
  instead of dropping a source:

  ```
  error: scanner errors:
    .../orphan.zzz: 'orphan.zzz' is listed in [build] sources, and mcpp has no role
    for the extension '.zzz'.
    Its object would be compiled and then linked by nothing, so this is refused rather
    than built.
  ```

### 3.4 The anatomy of a rule package

Three parts, none special to mcpp [docs/31-authoring-a-rule-package.md:97-109]:

| part | content |
|---|---|
| a package | an ordinary `mcpp.toml` with a version and a licence |
| a module | a `.cppm` exporting `options` and a function that submits build edges |
| a feature | the switch that selects it, and the place its own dependencies hang |

**The manifest: three keys on the feature** [docs/31-authoring-a-rule-package.md:110-128]:

```toml
[features]
default = []

[features.rules-toy]
sources           = ["src/rules-toy.cppm"]
rule_module       = "example.rules.toy"
device_extensions = [".toy"]
```

| key | effect on a consumer | since |
|---|---|---|
| `sources` | the module is compiled only when the feature is active | — |
| `rule_module` | the module the consumer's build program imports. **It implies `host-module = true`** | 2026.9.7.1 |
| `device_extensions` | those extensions are classified as device sources: never scanned, never producing a BMI, and refused if no action claims them | 2026.9.7.1 |

A rule that **generates or checks** rather than compiling a language declares no `device_extensions`;
`examples/08-build-rules` is that shape, and its consumer writes `host-module = true` on the dependency edge itself.

WARNING: **a rule feature that is in the package's own `[features] default` does not imply `host-module`.**
`mcpp:plugins` declares `default = []` for this reason; a rule package whose rule is on by default is refused with a
message naming the module and the key to add [docs/31-authoring-a-rule-package.md:375-379].

**The module a consumer imports** — the convention every shipped rule follows
[docs/31-authoring-a-rule-package.md:140-160]:

```cpp
export module example.rules.toy;
import std;
import mcpp;

export namespace example::rules::toy {

struct options {
    std::string out_dir  = std::string(mcpp::out_dir());
    std::string rule_dir = std::string(mcpp::dep_dir("rules-toy"));
};

bool compile(options opt = {});

}
```

A rule that plans its edges in one function and submits them in another gives a consumer a way past its last knob
without hand-writing the action; `examples/08-build-rules`' `plan` / `submit` pair is that shape.

**A rule takes the extensions it claims and leaves the rest.** `mcpp::device_sources()` is one string, one
package-root-relative path per line, holding the package's **whole** device set — a build with two backends puts both
backends' sources in that one list, and every rule in the build program reads the same value
[docs/31-authoring-a-rule-package.md:161-170].

### 3.5 `mcpp::action`, and the four roles

```cpp
mcpp::action a;
a.id          = id.c_str();          // stable, unique within the package
a.role        = "source";
a.description = desc.c_str();
a.arg("sh").arg(script.c_str()).arg(input.c_str()).arg(output.c_str());
a.input(input.c_str());
a.input(script.c_str());
a.output(output.c_str());
a.submit();
```

| `role` | outputs | ordering |
|---|---|---|
| `source` | compilable ones join the compile set | every compile edge of the declaring package waits for them |
| `check` | a stamp file | runs alongside compilation; `blocking = true` makes compiles wait |
| `object` | join the **link** set | the link edge consumes them |
| `artifact` | a new file | its inputs are link outputs, so it runs **after** the link |

[docs/31-authoring-a-rule-package.md:172-199]

**Four traps, each measured upstream:**

1. **The strings must outlive the action.** `a.id = ("toy:" + stem).c_str()` hands `submit()` a pointer into a
   temporary that is already gone [docs/31-authoring-a-rule-package.md:185-188].
2. **An action's command runs from the BUILD directory, not the package root.** `mcpp::device_sources()` answers
   package-root-relative, so a rule joins `mcpp::manifest_dir()` to each path before putting it on a command line.
   Measured: the relative path reached the compiler unchanged and the read failed there
   [docs/31-authoring-a-rule-package.md:207-210].
3. **The tool the command invokes is an input.** Without `a.input(compiler)`, editing the rule's own compiler leaves
   every edge clean and the artifact keeps the bytes the previous compiler produced — a green build over a stale
   result [docs/31-authoring-a-rule-package.md:200-206].
4. **A depfile is for inputs the rule cannot enumerate** — a shader or kernel that includes another file. Every
   compiler involved emits one: `glslangValidator --depfile`, `glslc -MD -MF`, `slangc -depfile`, and `-MD -MF` for
   the clang-family drivers [docs/31-authoring-a-rule-package.md:211-224]:

   ```cpp
   a.depfile = dep.c_str();          // a path the command writes
   a.arg("--depfile").arg(dep.c_str());
   ```

   **The depfile must not also be declared as an `output()`.**

**Chaining.** One action may consume what another produced; the engine orders and fingerprints them. That is the whole
engine-side content of a device link: N `artifact` actions whose outputs stay out of the link, and one `object` action
that reads them and produces the object that joins it [docs/31-authoring-a-rule-package.md:225-231].

WARNING: **an action's command is argv with no shell.** `cp` / `copy` were never portable from an action; the portable
spelling is `${mcpp.self} stage --verify content --output <dst> <src>`, and that argument shape is a contract (see
`../SKILL.md` §3).

### 3.6 The environment a rule brings with it

A rule owns the list of packages it drives, because it is the code that runs the compiler and puts the library
directory on the link line [docs/31-authoring-a-rule-package.md:232-251]:

```toml
[target.'cfg(accelerator = "cuda")'.feature-xlings.rules-cuda]
"xim:cuda-nvcc"   = "12.9.86"
"xim:cuda-cudart" = "12.9.79"
```

**Two gates, and both must open before a byte is downloaded**: the feature says whether the rule is *wanted*, and the
`cfg(accelerator = …)` selector says whether this build *compiles for the device*. A build with no accelerator opens
neither — which is what keeps the cheapest build cheap, and that is the build CI runs
[docs/42-heterogeneous-builds.md:396-400].

**A bare version is a choice a project may override; `>=` is a requirement a project may not go below**
[docs/31-authoring-a-rule-package.md:249-251]. See *One package, one version* in `docs/23-the-project-environment.md`.

### 3.7 Reporting, and finding the rule's own files

| channel | purpose |
|---|---|
| `mcpp::warning(...)` | a rule that **finished its job** and found something worth saying — a host compiler it had to choose, a payload it fell back to. A build program's output is otherwise printed only on a non-zero exit |
| `mcpp::fact(name, ver)` / `mcpp::floor(name, ver)` | the probe channel of §1.7; the engine reads a name, a relation and a version |

[docs/31-authoring-a-rule-package.md:270-289]

| object | accessor |
|---|---|
| the rule package's own tree | `mcpp::dep_dir("<name>")` — under the name the **consumer** declared in `[dependencies]` |
| a payload declared under `[xlings.workspace]` | `mcpp::xpkg_dir("<name>")` |
| a host tool built from a dependency | `mcpp::dep_bin("<pkg>", "<tool>")` |

[docs/31-authoring-a-rule-package.md:290-302]

WARNING: `dep_dir` answers under the spelling in the **consumer's** manifest. A rule that ships files beside its
module should expose the directory as an option so a consumer declaring the edge under another key can supply it, and
should refuse with a message naming what it looked for rather than running a command with an empty path.

### 3.8 An island's boundary is generated, and not by a rule

`mcpp.tools.island` is **not** a rule package and nothing in `mcpp:plugins` calls it: a project calls it from its own
`build.mcpp`, because the module name and the shape of the namespace are the **project's** decisions rather than the
rule's [docs/31-authoring-a-rule-package.md:252-268].

What a rule owes it is one field: `options::flags` on `cuda`, `hip`, `sycl` and `ascendc`, where
`mcpp::tools::island::force_include_flags` goes — because that driver inherits nothing from `mcpp::cxxflag`, and
because forcing a header into every C++ translation unit would put declarations ahead of a module interface's
`export module` line.

### 3.9 Beside a rule: distribution members (mcpp 2026.9.11.1+)

A `dist-*` member is neither a rule nor a tool: it does not compile a translation unit and does not work while the
build program runs. It consumes **link outputs** and produces something a user installs — an `.msi`, a `.deb`, an
AppImage, a signed `.app` — through an `artifact` action plus `mcpp pack --format <name>`
[docs/31-authoring-a-rule-package.md:304-330].

Everything in §3 applies unchanged; three things bind harder:

- **Declare unconditionally, submit conditionally.** `provides_pack_format` is what the engine reads to answer "which
  formats does this graph provide" on a build that asked for none. A member that declares only when asked works for
  its author, who always passes their own format, and makes the set unknowable for everyone else.
- **Expose a plan and a submit.** A distributable is the last thing before a user's hands and so the most likely part
  of a build to need a project-specific edit. `generate_all(opt)` being exactly `submit(plan_all(opt))` is what keeps
  such an edit from becoming a reimplementation of the member.
- **Name the input; do not harvest a directory.** A path that resolves to nothing is silent; a named input that is
  missing is an error. Measured: a WiX action that bound a directory and harvested it produced a **valid, empty**
  installer.

Related: `mcpp pack --format` takes `tar` / `dir` engine-side and dispatches any other name to a package in the
resolved graph, so an unknown value is refused **after** resolution, naming what is actually available
(`mcpp pack --help`; `version-notes.md` §8 row A12). A dispatched format runs `prepare` **twice** — budget for it on a
throttled machine (`references/commands.md`:225).

## 4. `examples/12-a-new-device-language` — teaching mcpp a language, end to end

The complete worked recipe for the extension points of §3. `.toy` is **not** in the engine's built-in
device-extension table and never will be; no mcpp release is involved
[examples/12-a-new-device-language/README.md:1-5].

```bash
cd examples/12-a-new-device-language/app
mcpp run
```
```
       Rules example.rules.toy (example:rules-toy)
    Building host tool toyc:toyc from toyc v0.1.0 (once per package source and host toolchain)
   Compiling toyapp v0.1.0 (.)
    Finished dev [unoptimized + debuginfo] in 0.65s

gcd(1071, 462) = 21
scale(21, 2)   = 42
answer()       = 42
```
[examples/12-a-new-device-language/README.md:7-21] — **this runs on any machine**: `toyc` is ordinary C++ and there is
no device anywhere in it.

### 4.1 The four directories

| directory | what it is | who builds it |
|---|---|---|
| `toyc/` | the compiler for `.toy`: a lexer, a recursive-descent parser, semantic checks and a C++ emitter | mcpp, **for the build machine**, as a host tool |
| `rules-toy/` | the rule: declares the extension, the module a consumer imports, and one action per `.toy` | the consumer's build program |
| `app/` | the project | mcpp, for the target |

[examples/12-a-new-device-language/README.md:23-30]

### 4.2 The compiler package — an ordinary mcpp package

[examples/12-a-new-device-language/toyc/mcpp.toml:1-19]

```toml
[package]
name        = "toyc"
namespace   = "example"
version     = "0.1.0"
description = "The compiler for the toy device language"
license     = "Apache-2.0"

[language]
standard = "c++23"

[build]
sources = ["src/lexer.cppm", "src/compile.cppm"]

[targets.toyc]
kind = "bin"
main = "src/main.cpp"
```

Nothing in it knows it is a device-language compiler. It is a `kind = "bin"` target, and that is the entire
requirement.

The language it implements has integers, `let`, assignment, `if`/`else`, `while`, calls between kernels, and the
arithmetic and comparison operators; every kernel takes and returns an integer
[examples/12-a-new-device-language/README.md:32-52]. `toyc` emits one `extern "C"` function per kernel and
forward-declares them all first, so kernels may call each other in any order:

```cpp
extern "C" int toy_gcd(int v_a, int v_b) {
    while ((v_b != 0)) {
        int v_t = v_b;
        v_b = (v_a % v_b);
        v_a = v_t;
    }
    return v_a;
}
```

**Three decisions in that output an author of any such emitter will face**
[examples/12-a-new-device-language/README.md:85-91]:

- **`extern "C"`**, because the two sides are produced by different compilers and share no C++ ABI — the same reason a
  device island's boundary is;
- **`v_` on every local**, because a kernel that names a variable `class` must not become a C++ file that fails to
  compile for a reason the source language cannot express;
- **parentheses around every binary expression**, because the AST already holds the grouping and the emitter does not
  reproduce C++'s precedence table.

**And it rejects what it cannot compile, with a location** [examples/12-a-new-device-language/README.md:93-109]:

```console
$ toyc bad.toy -o bad.cpp
bad.toy:1:1: error: kernel `scale` can reach its end without a `return`
bad2.toy:2:12: error: `b` is not a kernel in this file
bad3.toy:2:12: error: `x` is not declared
bad4.toy:3:5: error: expected `;`, found `return`
```

The first is the one worth its code: a block satisfies "returns on every path" if it ends in a `return` or in an
`if`/`else` whose branches both do — `while` never counts, because the language cannot state that a loop runs at all.
Emitting `return 0;` at the end instead would have compiled everything and given a wrong answer for the kernel whose
author forgot a branch.

### 4.3 The rule package — the whole manifest

[examples/12-a-new-device-language/rules-toy/mcpp.toml:1-40]

```toml
[package]
name        = "rules-toy"
namespace   = "example"
version     = "0.1.0"
description = "A rule package that teaches mcpp a device language the engine has never heard of"
license     = "Apache-2.0"

[features]
default = []

[features.rules-toy]
sources           = ["src/rules-toy.cppm"]
rule_module       = "example.rules.toy"
device_extensions = [".toy"]

# The request hangs on the FEATURE, so a project that depends on this package
# without activating the rule builds no compiler.
[feature-deps.rules-toy]
example.toyc = { path = "../toyc", tools = ["toyc"], reexport = true }
```

| part | what it does |
|---|---|
| `tools = ["toyc"]` | mcpp builds that target **for the build machine**, even when the project around it is cross-compiling |
| `reexport = true` | the tool reaches whoever activated the feature. **Without it the tool stays with this package** — the supply-chain default: an arbitrary transitive dependency must not put entries in a build program's tool namespace |
| on `[feature-deps]` | a project that depends on this package **without** activating the rule builds no compiler |

[examples/12-a-new-device-language/README.md:143-156]

**That gating was measured.** With `features = ["rules-toy"]` removed from the consumer, the build stops before any
tool is built, and the tool store holds no `toyc` entry afterwards
[examples/12-a-new-device-language/README.md:158-166]:

```
error: build.mcpp imports 'example.rules.toy', and no dependency provides it as a host module.
       declared without `host-module = true`: rules-toy (in [dependencies])
```

(Machine channel: `host-module-missing` [src/build/refusal.cppm:136].)

### 4.4 The rule module — the whole of it

[examples/12-a-new-device-language/rules-toy/src/rules-toy.cppm:7-91], comments condensed:

```cpp
export module example.rules.toy;

import std;
import mcpp;

export namespace example::rules::toy {

struct options {
    std::string out_dir = std::string(mcpp::out_dir());
    // `dep_bin` answers under the name in the manifest that DECLARED the tool --
    // this package's `[feature-deps]` entry -- and the answer travels to the
    // consumer because that entry says `reexport = true`.
    std::string compiler = std::string(mcpp::dep_bin("toyc", "toyc"));
};

inline bool compile(options opt = {}) {
    const std::string root = mcpp::manifest_dir();
    if (root.empty()) { /* not running from build.mcpp */ return false; }
    if (opt.compiler.empty()) { /* feature not activated; message names the fix */ return false; }

    // `device_sources()` is the package's WHOLE device set. A rule selects by
    // the extension it claims and leaves the rest.
    std::vector<std::string> mine;
    std::string_view all(mcpp::device_sources());
    for (std::size_t i = 0; i <= all.size();) {
        const auto sep = all.find('\n', i);
        const auto one = all.substr(i, sep == std::string_view::npos ? all.size() - i : sep - i);
        i = sep == std::string_view::npos ? all.size() + 1 : sep + 1;
        if (one.ends_with(".toy")) mine.emplace_back(one);
    }

    bool any = false;
    for (auto const& src : mine) {
        const std::string stem = std::filesystem::path(src).stem().string();
        const std::string gen  = opt.out_dir + "/toy_" + stem + ".cpp";
        const std::string id   = "toy:" + stem;      // outlives the action
        const std::string desc = "toyc " + src;
        const std::string abs  = root + "/" + src;   // ABSOLUTE: see §3.5 trap 2

        mcpp::action a;
        a.id          = id.c_str();
        a.role        = "source";   // this produces C++ that mcpp then compiles
        a.description = desc.c_str();
        a.arg(opt.compiler.c_str()).arg(abs.c_str()).arg("-o").arg(gen.c_str());
        a.input(abs.c_str());
        a.input(opt.compiler.c_str());               // the compiler is an input
        a.output(gen.c_str());
        a.submit();
        any = true;
    }
    if (!any) std::println(std::cerr, "example.rules.toy: no `.toy` source in this package");
    return any;
}

}
```

`role = "source"` because what this produces is C++ that mcpp then compiles. **A rule whose compiler emitted an object
directly would use `object`.**

### 4.5 The consumer — two files

[examples/12-a-new-device-language/app/mcpp.toml:1-18]:

```toml
[package]
name    = "toyapp"
version = "0.1.0"

[language]
standard = "c++23"

# ONE EDGE. `rule_module` on the feature implies `host-module = true`, and the
# feature's own `[feature-deps]` brings the compiler.
[dependencies]
example.rules-toy = { path = "../rules-toy", features = ["rules-toy"] }

# `.toy` IS NOT IN THE DEFAULT SOURCE GLOB.
[build]
sources = ["src/*.cpp", "src/kernels/*.toy"]
```

[examples/12-a-new-device-language/app/build.mcpp:1-11]:

```cpp
import std;
import mcpp;
import example.rules.toy;

int main() {
    // The rule reads the device set from the graph, so this program names no
    // file. What it must track is the SET of paths: a `.toy` appearing or
    // disappearing changes what the graph should be.
    mcpp::rerun_if_changed_glob("src/kernels/**/*.toy");
    return example::rules::toy::compile() ? 0 : 1;
}
```

### 4.6 Host-tool caching — the boundary this example measured

Four changes, each made one at a time from the same starting state
[examples/12-a-new-device-language/README.md:185-224]:

| what changed | the artifact | how it was changed |
|---|---|---|
| the `.toy` source | follows: `42` → `63` | `scale(…, 2)` → `scale(…, 3)` |
| the compiler's **bytes**, at the path the action names | follows: `42` → `168` | overwriting the binary in the tool store |
| the compiler's **sources**, version unchanged | **follows: `42` → `168`, and the tool is rebuilt** | editing the emitter |
| the compiler's **version** | follows, and the tool is rebuilt | `0.1.0` → `0.1.1` |

Rows two and three separate two things that are easy to merge:

- **the action's input tracking** — `rules-toy` declares the compiler beside the source, and changing that file's
  bytes re-runs the edge;
- **the store's key** — the tool package's identity, version, host triple, compiler identity, profile, features, the
  versions of its transitive dependencies, **and the tool's source in the form its kind offers**. For a package from
  an index the version alone identifies the sources, because a published version is immutable. For a `path`
  dependency being edited the key carries a **stamp of the tree** (every file's relative path, size and modification
  time), so row three rebuilds the tool.

Row three **used to read** "does not follow: the previous answer stands", and that reading was the measurement
`mcpp#630` (item 6) removed.

The store lives at `<mcpp cache dir>/tool/<index>/<name>@<version>[+<source>]/`; entries accumulate as a tree is
edited, one per stamp, and `mcpp cache clean` empties it.

WARNING: `mcpp run` printing `Finished dev in 0.00s` is **mcpp's own summary rather than evidence** — row two prints
it too, and the artifact changed.

WARNING: **row four does not test row two.** The tool's path is on the action's command line, so a new version re-runs
the edge whether or not the compiler is also a declared input; removing `a.input(compiler)` and bumping the version
left the artifact following anyway. The isolating change is different bytes at the *same* path — row two — and it
takes **both** directions: with the input removed, the artifact followed the overwrite and then stopped following the
restore. CI runs that pair.

WARNING: **going backwards in version does not work.** Returning `0.1.1` → `0.1.0`, whose clean tool was still in the
store, left the artifact at the `0.1.1` answer: the build program did not re-run, so the plan still named the `0.1.1`
binary, which had not changed. `rm -rf target` cleared it. **Iterating on a compiler means the version goes forward
only** [examples/12-a-new-device-language/README.md:226-230].

### 4.7 Three things the first version of this example got wrong

Recorded upstream because each is a mistake a rule author will make once
[examples/12-a-new-device-language/README.md:232-250]:

1. **An action's command does not run from the package root** (§3.5 trap 2).
2. **The compiler was a shell script, and its exit status lied.** The first `toyc` summed with
   `sed … | grep … | paste -sd+ - | bc`. A pipeline's status is its last command's: when an earlier stage produced
   nothing, `bc` still exited 0, `set -e` never fired, and the script wrote a program that compiled, linked, ran and
   printed `0`. **Replacing the script with a compiled program removed the class, not just the instance.**
3. **The strings must outlive the action** (§3.5 trap 1).

### 4.8 Checklist: adding your own device language

1. Write the compiler as an ordinary mcpp package with a `kind = "bin"` target (§4.2). Not a shell script.
2. In the rule package, put `sources`, `rule_module` and `device_extensions` on **one feature**, and keep
   `[features] default = []` (§4.3).
3. Hang the compiler on `[feature-deps.<f>]` with `tools = [...]` and `reexport = true` (§4.3).
4. In the rule module, filter `mcpp::device_sources()` by **your** extension, make paths absolute with
   `mcpp::manifest_dir()`, keep every string alive to `submit()`, and declare the compiler as an input (§4.4, §3.5).
5. Pick the role by what your compiler emits: `source` for C++, `object` for an object, `artifact` for something the
   link produces inputs for (§3.5).
6. If your compiler discovers its own includes, use a depfile — and do not also declare it as an output (§3.5).
7. In the consumer, activate the feature on the dependency edge and **name the sources** — device extensions are never
   in the default glob (§4.5).
8. Have the build program `rerun_if_changed_glob` the source set, because a file appearing or disappearing changes
   what the graph should be (§4.5).

WARNING: the maintainer's link to this example may point at branch `docs/architecture-three-trees`, and **that copy is
stale**. Same four-part layout, different README blob (`bcaba486` on the branch vs `daf4703c` on `main`; GitHub
contents API, 2026-09-16). The branch text states the **opposite** of §4.6 ("the compiler's sources, its version
unchanged → does not follow: the previous answer stands") and writes the dependency keys un-namespaced
(`rules-toy = {…}`, `toyc = {…}` rather than `example.rules-toy` / `example.toyc`). **Cite `main`.**

## 5. The Wasm, Android and iOS target rows

These are **not** part of the accelerator axis — they are ordinary target rows, reached with `--target`. They are on
this page because the same three mechanisms govern them (capability pins, platform floors, `--format`) and because
`examples/13-platform-targets` teaches all three at once.

### 5.1 Tiers, and what a tier claims

`verified` / `preview` / `planned`, across **29 registered rows** — the registered rows are the entire vocabulary, and
`mcpp toolchain list` prints the same table [docs/21-the-target-triple.md:494-525].

| tier | claim |
|---|---|
| `verified` | an artifact was built **and run** for the row. It does **not** state which emulator ran it |
| `preview` | it builds and links; no run has been recorded |
| `planned` | registered in the vocabulary, nothing wired yet — **refused rather than attempted** |

[docs/40-baremetal.md:44-46; docs/21-the-target-triple.md:560-566]

| row | tier | pin | reachable from |
|---|---|---|---|
| `wasm32-emscripten` | verified | `emsdk@6.0.9` | every host |
| `aarch64-linux-android` | verified | `android-ndk@30.0.16248370` | linux-x86_64, linux-aarch64, macos-arm64 |
| `x86_64-linux-android` | verified | `android-ndk@30.0.16248370` | the same three |
| `aarch64-ios` | preview | `llvm@22.1.8` | macos-arm64 (SDK) |
| `aarch64-ios-sim` | verified | `llvm@22.1.8` | macos-arm64 (SDK) |
| `x86_64-ios-sim` | preview | `llvm@22.1.8` | macos-arm64 (SDK) |

[docs/21-the-target-triple.md:519-525]

Wasm and both Android rows reach **every host** because the SDK ships its own sysroot and upstream publishes it per
host: one archive serves every guest architecture [docs/21-the-target-triple.md:543].

WARNING: **the Android rows nonetheless read `—` on Windows, and that is the INDEX's answer, not the engine's.**
Google publishes a Windows NDK and it downloads; what it does not contain is the **libc++ module surface** (measured:
no `std.cppm` and no `std/*.inc`, against 110 on the other two hosts), so `xim:android-ndk` declares no Windows table
— an entry that can never serve a module-first build is worse than none. A Windows user therefore still **sees** the
row in `mcpp toolchain list`, the pin resolves, and xim refuses with `no payload for this platform` before anything is
fetched, naming the package [docs/21-the-target-triple.md:545-556].

WARNING: **both Android rows are `verified` by different vehicles.** The x86_64 artifact executes on the platform's
own emulator; the device row's artifact runs under **qemu-user over the system image's own bionic**, because the
platform emulator refuses a foreign guest (`QEMU2 emulator does not support arm64 CPU architecture`)
[docs/21-the-target-triple.md:558-566].

### 5.2 Nothing has to be declared

A target row names its own payload, and that pin is the default. Neither of these needs a line in `mcpp.toml`
[docs/20-toolchains.md:507-525]:

```bash
mcpp build --target wasm32-emscripten     # resolves emsdk@6.0.9
mcpp build --target aarch64-linux-android # resolves android-ndk@30.0.16248370
```

The payload installs **on demand** the first time a target needs it, and the build reports which archive answered:

```
Resolved emsdk@6.0.9 → wasm32-emscripten → …/xim-x-emsdk/6.0.9/emscripten/em++
Resolved android-ndk@30.0.16248370 → aarch64-linux-android → …/prebuilt/linux-x86_64/bin/clang++
```

Declaring one anyway works, and naming the row's own payload is always accepted — use it to pin a version across
machines, or to opt into a payload newer than the row's convention [docs/20-toolchains.md:527-543]:

```toml
[target.aarch64-linux-android]
toolchain = "android-ndk@30.0.16248370"

[target.wasm32-emscripten]
toolchain = "emsdk@6.0.9"
```

### 5.3 Capability pins — the payload NAME is fixed, the version is open

For these rows the pin is a **capability rather than a convention**: not mcpp's preference among several payloads that
could serve the target, but the only thing that can [docs/20-toolchains.md:545-570].

```toml
[target.aarch64-linux-android]
toolchain = "llvm@22.1.8"        # refused
```
```
error: target 'aarch64-linux-android' cannot be emitted by 'llvm@22.1.8'.
       An Android target needs bionic, not just an aarch64 or x86_64 back end:
       its headers, its per-API-level stubs and its loader path are inside the
       NDK, and no package adds them to another compiler.
```

**The refusal is not about code generation.** A stock clang emits aarch64 ELF perfectly well; what it cannot supply is
the **system**. Saying so at the declaration is better than resolving llvm and failing deep inside the build, which is
what happened before the gate existed — first `'__config' file not found`, then
`Unversioned target triples are not supported!` from bionic's own header, neither naming the toolchain that could not
serve the row.

`wasm32-emscripten` refuses on the same rule with its own sentence: **nothing but Emscripten emits WebAssembly.**
Machine output classifies both as `capability-pin` [docs/50-machine-output.md:385]. The capability-pinned rows are
wasm, Android, and PE+musl (`../SKILL.md` §7).

### 5.4 The deployment floor belongs to the project

```toml
[target.aarch64-linux-android]
min_api_level = 24
```

One NDK serves a **range** of API levels, so the level is a project decision and naming `android-ndk@<version>` pins
none. Left out, mcpp reads the floor the NDK declares in its own `meta/platforms.json` (21 for r30)
[docs/20-toolchains.md:572-592; examples/13-platform-targets/README.md:79-82].

**Where the level goes, and where it does not** [docs/04-mcpp-toml.md:831-861]:

| | value |
|---|---|
| canonical triple (names the output directory, `cfg(env = "android")`, the packed ABI tag) | `aarch64-linux-android` |
| what clang receives | `aarch64-unknown-linux-android24` |

The level rides the **effective** triple and the **build fingerprint** only — the level decides which bionic symbols
are visible, so **two levels are two ABIs and must never share a build directory**.

The Apple equivalents are `[build] ios_deployment_target` and `macos_deployment_target`; a target is either Apple or
Android, so both share one fingerprint slot [examples/13-platform-targets/README.md:84-86]. The deployment target is
carried by the **effective triple and nowhere else** — `arm64-apple-ios18.0` and `arm64-apple-ios18.0-simulator`,
Apple's own spelling. `-miphoneos-version-min` is deliberately not emitted: the triple already said it, and a flag
would become a second place saying it [examples/13-platform-targets/README.md:141-143].
Which one applies is decided by the **target**, not by the machine running mcpp: the macOS value (`MACOSX_DEPLOYMENT_TARGET` >
`macos_deployment_target` > `14.0`) reaches the triple, the fingerprint and `-mmacosx-version-min` whenever the target's `os` is
`macos`, on a Linux or Windows host as well, and never reaches a non-Apple row [src/build/prepare.cppm:2111-2113;
modules/platform/src/macos/macos.cppm:125-132 @ b4824697]. A real macOS build off a Mac still needs the macOS SDK; a plan-only
`mcpp build --target aarch64-macos --configure-only` with an explicit `[target.aarch64-macos] toolchain = "llvm@..."` needs none and
is enough to check the effective triple (`arm64-apple-macos11.0` for `"11.0"`).

Any package may state a requirement against these through the ordinary version-floor channel of §1.7
[docs/06-features-and-capabilities.md:344-355]:

```toml
[[runtime.requirements]]
kind  = "version-floor"
value = "android.api-level >= 23"
```
```
error: `fw` requires android.api-level >= 23, and this build targets 21.
         set by: [target.x86_64-linux-android] min_api_level
```

**The floor is not raised on the dependency's behalf**: the value the key sets is the one the compiler targets, and
which devices an application installs on is the application's decision. A row that states no such fact leaves the
requirement silent, so the requirement needs no selector.

### 5.5 `examples/13-platform-targets` — one source, three platforms, no `cfg`

The whole example is one `src/main.cpp` with **no platform-aware anything**: no `cfg`, no preprocessor branch, no
per-target source file. Only `--target` on the command line changes
[examples/13-platform-targets/README.md:1-10]. NOTE: this README is written in **Chinese**, unlike every other example
README in the tree.

```bash
cd examples/13-platform-targets
mcpp build && mcpp run                       # the host
mcpp run   --target wasm32-emscripten        # Web
mcpp build --target x86_64-linux-android     # the emulator
mcpp build --target aarch64-linux-android    # a device
mcpp build --target aarch64-ios              # a device artifact
mcpp run   --target aarch64-ios-sim          # the simulator, through a runner
```

**Measured, Web** (linux-x86_64, `xim:emsdk` 6.0.9) [examples/13-platform-targets/README.md:18-24]:

```
bin/platform-targets        65389 bytes   the JavaScript
bin/platform-targets.wasm  447183 bytes   the module
node bin/platform-targets   ->  1-2-3
```

**Measured, Android** (same machine, `xim:android-ndk` 30.0.16248370)
[examples/13-platform-targets/README.md:42-64]:

```
aarch64-linux-android  ->  ELF 64-bit LSB pie, ARM aarch64, interpreter /system/bin/linker64
x86_64-linux-android   ->  ELF 64-bit LSB pie, x86-64, same interpreter

adb push target/x86_64-linux-android/*/bin/platform-targets /data/local/tmp/
adb shell /data/local/tmp/platform-targets
#  ->  1-2-3
```

**One pin serves both rows**, because the NDK does not name an architecture — `--target` does — so
`[target.<triple>] toolchain` need not be written at all.

WARNING: a load-time warning on API 24 is **not a defect**: `unsupported flags DT_FLAGS_1=0x8000001`. API 24's bionic
loader does not recognise the `DF_1_PIE` bit lld sets, warns once, and loads the program normally
[examples/13-platform-targets/README.md:62-64].

**Measured, iOS** (macos-15, Xcode 16.4, iPhoneOS/iPhoneSimulator 18.5, `ios_deployment_target = "18.0"`)
[examples/13-platform-targets/README.md:117-129]:

```
aarch64-ios      ->  Mach-O 64-bit executable arm64
                     LC_BUILD_VERSION  platform 2 (IOS)          minos 18.0
aarch64-ios-sim  ->  Mach-O 64-bit executable arm64
                     LC_BUILD_VERSION  platform 7 (IOSSIMULATOR) minos 18.0
mcpp run --target aarch64-ios-sim  ->  1-2-3
```

**`platform 2` versus `platform 7` is the one reading worth checking**: a successful build cannot separate the two, and
an artifact reporting `IOSSIMULATOR` on the device row is a wrong artifact that no later step will refuse.

**On iOS the compiler is the ecosystem's and only the SDK is Apple's.** All three iOS rows pin `llvm@22.1.8` — the
same ordinary payload `aarch64-macos` uses. Any sufficiently new clang produces arm64 Mach-O for an iOS deployment
target; what cannot be packaged is the iPhoneOS / iPhoneSimulator SDK, which lives in Xcode and is not
redistributable — so mcpp **locates** it through `xcrun --sdk <name> --show-sdk-path`, exactly as it has always
located the macOS SDK [examples/13-platform-targets/README.md:111-115].

The simulator runner is declared beside the line that uses it
[examples/13-platform-targets/README.md:131-150]:

```toml
[build]
ios_deployment_target = "18.0"

[target.aarch64-ios-sim]
runner = ["simctl-run"]

[target.aarch64-ios-sim.xlings.workspace]
"xim:apple-simulator-tools" = ""
```

`ios` is the **device vs simulator** axis in the `env` slot — Apple spells it with a trailing `-simulator` on the OS
segment and Rust as `aarch64-apple-ios-sim`; both spellings parse and both canonicalise to `aarch64-ios-sim`
[docs/21-the-target-triple.md:53-61].

### 5.6 The wasm artifact contract

`wasm32` is the first target in mcpp's vocabulary whose object format is neither ELF nor Mach-O nor PE
[docs/21-the-target-triple.md:93-108]. The consequences are a contract, not conventions
[docs/21-the-target-triple.md:110-129]:

| target `kind` | the artifact | the rest |
|---|---|---|
| `bin`, `app` | `bin/<name>.js` — **the JavaScript launcher**, and the file a runner executes | `bin/<name>.wasm` is an **implicit output of the same link edge**, staged with it. Any further file emcc writes with the same stem (`<name>.data` from `--preload-file`, `<name>.worker.js`, `<name>.wasm.map`) travels exactly when the link produced it |
| `shared` | **refused**, naming `-sSIDE_MODULE` | a wasm side module needs a link contract mcpp does not render |

The `.js` suffix is not mcpp's invention: it is what `emcc` defaults to, what CMake pins with
`CMAKE_EXECUTABLE_SUFFIX ".js"`, and what Rust's `wasm32-unknown-emscripten` target spec states
(`exe_suffix: ".js"`). Before this the row used a bare host-borrowed name [CHANGELOG.md:280-298].

`--no-entry` — Emscripten's flag for a module with no `main` — is **not** a switch mcpp interprets; it is an ordinary
`[target.'cfg(os = "emscripten")'.build] ldflags` entry, and `main` keeps naming a translation unit regardless
[docs/22-target-side.md:701-705].

**What `mcpp pack` stages** [docs/10-pack-and-release.md:420-439]:

```
target/dist/myapp-0.1.0-wasm32-emscripten.tar.gz
└── myapp-0.1.0-wasm32-emscripten/
    ├── bin/myapp.js              ← the launcher; the file a runner executes
    ├── bin/myapp.wasm            ← implicit output of the link, staged with it
    ├── bin/myapp.data            ← present only when the link carries --preload-file
    ├── README.md
    └── LICENSE
```

`myapp.wasm` is **required**: the link edge declares it as an implicit output, so its absence names a build directory
that does not match the graph, and `mcpp pack` refuses rather than staging a launcher with no module.

**The runner is a payload fact, not a toolchain one.** Neither an emulator nor a device is part of the toolchain axis;
a wasm module needs an *interpreter*. `xim:emsdk` writes `.mcpp-toolchain.json` beside itself whose `runner` key names
the `node` of the `xim:node` payload it depends on, and `mcpp run` / `mcpp test` use that program when neither the
project nor a dependency declares a runner — **so no `node` on `PATH` is involved**
[docs/20-toolchains.md:594-600].
WARNING: this needs mcpp **2026.9.12.2** and an emsdk payload installed **after** that recipe update; an older payload
has no descriptor, and the artifact's `#!/usr/bin/env node` first line then picks whatever `node` is on `PATH`
[examples/13-platform-targets/README.md:26-29].

### 5.7 `[target.<sel>.abi]` — a switch the whole artefact shares

```toml
[target.'cfg(os = "emscripten")'.abi]
threads    = true
exceptions = true
```

Some properties of a target are **not a flag a translation unit may choose**. On WebAssembly every object, the
precompiled standard-library module and the link must agree on shared memory and atomics, and one translation unit
built without them makes the link fail or the module refuse to load. Exceptions are the same shape: clang records the
exception model in a BMI and refuses an importer that disagrees. Such a property is therefore a **typed member** of
`[target.<selector>.abi]` rather than a flag in `cxxflags` [docs/22-target-side.md:594-612].

| member | type | renders as | reaches | since |
|---|---|---|---|---|
| `threads` | boolean | `-pthread` on a target that is neither PE nor freestanding; **nothing** on PE and on freestanding | the std-module prebuild, the dependency scan, every C and C++ TU of every package, and the link | 2026.9.12.2 |
| `exceptions` | boolean | `-fexceptions`, on `os = "emscripten"` **only** (elsewhere exceptions are already the default) | the same set | 2026.9.12.3 |

Both enter the dependency cache key through the dialect flags, so a dependency built without one is never reused by a
build with it. An unknown member, and a member that is not a boolean, are refused naming both.

WARNING: **without `exceptions`, the observed failure is at RUN time, not at link.** A Web program that throws across
an `import std` boundary builds and links with no complaint — Emscripten's compile-time exception support does not
depend on the flag — and aborts only when the `throw` executes
[docs/22-target-side.md:621-631]:

```
Aborted(Assertion failed: Exception thrown, but exception catching is not
enabled. Compile with -sNO_DISABLE_EXCEPTION_CATCHING or
-sEXCEPTION_CATCHING_ALLOWED=[..] to catch.)
```

**Only the root manifest decides.** The switch belongs to the artefact, and the root is the only package that builds
one. A dependency writing `[target.<selector>.abi]` is reported (`abi/dependency-table`) and changes nothing. A
dependency states what it **needs** instead [docs/22-target-side.md:632-690]:

```toml
[package]
requires_abi = { threads = true }          # the package needs threads

[features]
mt = { requires_abi = { threads = true } } # only this feature needs them

# scoped to a platform -- the per-target form (2026.9.12.3+)
[target.'cfg(linux)']
requires_abi = { threads = true }

[target.'cfg(linux)'.feature-requires-abi]
mt = { threads = true }
```

The requirement set is the **union** of `[package] requires_abi`, the active features' tables, and every matching
selector's; it is unioned only for a selector that matches the resolved target. An unsatisfied requirement is refused
before anything compiles, naming the selector exactly as written:

```
error: `wasmrt` requires the artefact's ABI to have threads ([target.'cfg(linux)']), and this build does not state it.
       Add to the root manifest, for the targets that need it:

           [target.'cfg(os = "<os>")'.abi]
           threads = true
```

Without the refusal the mismatch surfaces as a precompiled-module configuration error naming neither the package nor
the switch.

WARNING: **an engine older than 2026.9.12.3 reads `[target.<sel>] requires_abi` silently** — neither a warning nor an
error. It is a table-valued key under a target selector, and an older engine's schema sweep skips every table-valued
key on the assumption that a table is the conditional channel; `requires_abi` there is an inline table, the same TOML
shape, and falls through unreported. A package relying on that refusal must state its own engine floor
[docs/22-target-side.md:692-700]:

```toml
[build-dependencies.mcpp]
version = ">= 2026.9.12.3"
```

### 5.8 `pack` and `run --format` on these rows

**`mcpp run --format <name>`** (2026.9.12.3+) exists for the case a plain `mcpp run` cannot reach: an Android
application is a `.apk` and an installed iOS application a `.app`, and neither is the link output `run` executes by
default. It packs the target for `<name>` — the same two passes and staged tree as `mcpp pack --format <name>` — then
runs the artifact the pack reported, through the runner resolved for a program (the project's
`[target.<triple>] runner`, then a dependency's `mcpp::runner(...)`, then the payload descriptor's)
[docs/10-pack-and-release.md:224-240]:

```bash
mcpp run --target x86_64-linux-android --format apk
mcpp run --target aarch64-ios-sim      --format app
```

Verified on the binary: `--format` is present on `mcpp run` and is **refused together with `--no-runner`**
(`mcpp run --help`, `2026.9.15.2`). The artifact a pack reports is the request's **terminal** one: among the
`artifact` actions the request introduced, the output no other introduced action consumes.

**On an Android row `kind = "app"` links as a shared library**, because the platform loads an application as a shared
library into a Java process (`System.loadLibrary("myapp")`, `android:name` in the manifest). `main` still names a
translation unit; it is compiled as one of the library's units [docs/04-mcpp-toml.md:175-186].

```
target/dist/myapp-0.1.0-x86_64-linux-android/
├── lib/libmyapp.so             ← the application object
├── lib/libmydep.so             ← a dependency's shared library
├── lib/libc++_shared.so        ← the NDK's C++ runtime, when the object needs it
└── bin/<to>/…                  ← files `[runtime] deploy` placed
```

The closure is read from the files and staged beside it (2026.9.14.2+). **A name the device provides is not staged** —
one present in the API level's stub directory, which mcpp takes from the row's own compiler (the directory it finds
`libc.so` in): `libc.so`, `libm.so`, `libdl.so`, `liblog.so` and the other platform libraries. Every other name must
resolve in a directory the link used, and **a name that resolves nowhere makes `tar` and `dir` refuse**, naming it and
the directories searched. `--mode` does not apply on this row [docs/10-pack-and-release.md:542-565].

**A `kind = "app"` target whose artifact is a shared object accepts more than one `--target`** (2026.9.13.2+): both
Android ABIs stage into one tree at `lib/<abi>/lib<name>.so` (`aarch64` → `arm64-v8a`, `x86_64` → `x86_64`), each with
its own closure, the declared deploy files staged once, and one dispatch running against the combined tree — which is
what lets a member such as `dist-apk` build one universal APK. A single `--target` keeps the flat
`lib/lib<name>.so` layout. **An executable on any requested row is still refused a second `--target`**: packing one
executable for several triples would need several executables, which is a different mechanism (`lipo`'s universal
binary) that this does not provide [docs/10-pack-and-release.md:201-223].

### 5.9 `[package] platforms` — the vocabulary, and the Android trap

```toml
[package]
platforms = ["linux", "macos", "windows", "ios", "android", "emscripten"]
```

`ios`, `android` and `emscripten` are new members as of **2026.9.12.3** [docs/04-mcpp-toml.md:1325-1339].

WARNING: **Android rows are `os = "linux"` with `env = "android"`, so `linux` in this list does NOT cover them.** A
package that serves Android must state `android` as well. Conversely, `os = "linux"` **predicates** *do* match Android
rows — the two mechanisms disagree on purpose, and `../SKILL.md` §7 states the same trap from the predicate side. The
Web row keeps its `os` word, `emscripten`, the same word the `cfg(...)` selector grammar uses.

## 6. Bare metal and the embedded ecosystem

### 6.1 A freestanding target is one whose `os` field is `none`

Thirteen of them [docs/40-baremetal.md:25-42]:

| triple | tier | C library |
|---|---|---|
| `riscv64-none-elf` | verified | `xim:picolibc-riscv` |
| `riscv32-none-elf` | verified | `xim:picolibc-riscv` |
| `aarch64-none-elf` | preview | none by default — the zero-libc tier; `xim:picolibc-aarch64` is declarable |
| `x86_64-none-elf` | preview | none by default — the zero-libc tier; `xim:picolibc-x86` is declarable |
| `thumbv6m-none-eabi` | verified | none by default — Cortex-M0/M0+/M1 |
| `thumbv7m-none-eabi` | verified | none by default — Cortex-M3 |
| `thumbv7em-none-eabi` | preview | none by default — Cortex-M4/M7, soft float |
| `thumbv7em-none-eabihf` | verified | none by default — Cortex-M4F/M7F, hard float |
| `thumbv8m.base-none-eabi` | preview | none by default — Cortex-M23 |
| `thumbv8m.main-none-eabi` | verified | none by default — Cortex-M33/M55, soft float |
| `thumbv8m.main-none-eabihf` | preview | none by default — Cortex-M33F/M55F, hard float |
| `armv7a-none-eabi` | verified | none by default — Cortex-A 32-bit, soft float |
| `armv7a-none-eabihf` | verified | none by default — Cortex-A 32-bit, hard float |

**Such a target needs no per-host cross toolchain.** clang and lld are cross-compilers by construction — one binary
emits every target it was built with — so the table pins `llvm@22.1.8` on every host, and any machine that can install
the LLVM payload can produce an image for any of these rows [docs/40-baremetal.md:132-135].

Four table decisions that look like over-specification and are not:

- **M-profile is seven rows, not one.** An object built for `thumbv7em` uses instructions a Cortex-M0 does not have,
  and the two spellings produce **incompatible objects** rather than expressing a preference. The table exists so that
  `--target <triple>` alone suffices to produce a correct object file; one `arm-none-eabi` row plus a per-project
  `-mcpu` would move a correctness decision out of the table and into every manifest
  [docs/40-baremetal.md:69-81].
- **The float ABI does not settle whether the FPU is used.** It governs how floating-point values cross a function
  boundary, not what the compiler may emit inside one. Measured: under the soft-float ABI clang still emits
  `vmul.f32` for a float multiply, which on a Cortex-M4 without an FPU **faults at run time after a clean compile and
  a clean link**. Every soft-float row therefore carries `-mfpu=none`, including rows for architectures that have no
  FPU at all — a row states the property it guarantees rather than inheriting it from a default
  [docs/40-baremetal.md:83-90].
- **`x86_64-none-elf` needed engine code**, and the reason is a property of clang rather than of the instruction set.
  clang has a *BareMetal* toolchain for arm, aarch64 and riscv, which links with `ld.lld` directly; it has **none for
  x86_64**, so every spelling of a bare x86_64 triple falls through to the generic GCC toolchain — whose linker is the
  **host's `g++`**: `g++: error: unrecognized command-line option '-fuse-ld=/…/llvm/22.1.8/bin/ld.lld'`. Measured for
  six spellings and unchanged by `-fuse-ld=lld`, `--ld-path=`, `--gcc-toolchain=` or `-B`; the only thing that changes
  it is putting `linux` in the OS position, which adds eight host `-L` paths to a bare-metal link. Hence the row's
  fifth column, `lldEmulation`, and a link driven by `ld.lld` itself, with a different flag vocabulary (`-Map=` rather
  than `-Wl,-Map=`, `-m elf_x86_64` rather than `--target=`) and driver-only flags dropped rather than translated
  [docs/40-baremetal.md:137-168].
- **`-mno-red-zone` is part of the target, not a preference.** The System V x86-64 ABI reserves 128 bytes below `rsp`
  that a leaf function may use without adjusting the stack pointer. On bare metal the processor pushes an interrupt
  frame at `rsp` — into the red zone — and the interrupted leaf resumes to find its locals overwritten. **No fault and
  no diagnostic**, and it happens only when an interrupt arrives inside a leaf
  [docs/40-baremetal.md:170-184].

**ARMv7-A is the first 32-bit row with an MMU.** Every other 32-bit row is M-profile — an MPU describing regions by
base and limit, and no page-table entry at all — so A-profile is the first target on which an address-space
abstraction can be asked what a *32-bit* machine's entry looks like (short descriptors are 32 bits wide, long/LPAE
ones 64). That question cannot be put to a machine with no entries, which is why `openarch`'s Cortex-M backend
declines the capability [docs/40-baremetal.md:47-54].

### 6.2 Two commands to a booting image

```bash
mcpp new blinky --template riscv-virt-rt
cd blinky
mcpp run
```
[docs/40-baremetal.md:192-201] — `mcpp new --template` verified on the binary (`mcpp new --help`, `2026.9.15.2`:
`-t, --template <SPEC>  bin (default) | [ns.]pkg[@ver][:template]`; `--list-templates <PKG>` lists a package's).

Measured output [docs/40-baremetal.md:203-222]:

```
   Resolving toolchain
    Resolved llvm@22.1.8 → riscv64-none-elf → @mcpp/registry/data/xpkgs/xim-x-llvm/22.1.8/bin/clang++
    Resolved host toolchain for build.mcpp: clang 22.1.8 (x86_64-unknown-linux-gnu)
  build.mcpp compiling
  build.mcpp running
    Inferred sources [src/**/*.{cppm,cpp,cc,c,S,s,asm}]
    Inferred target blinky (bin from src/main.cpp)
   Compiling blinky v0.1.0 (.)
      Cached riscv-virt-rt v0.3.0 (1 unit)
    Finished dev [unoptimized + debuginfo] in 0.05s
        Size blinky  text 8572  data 80  bss 5668  total 14320
     Running `…/xim-x-qemu-riscv/9.2.4-1/bin/qemu-system-riscv64 … target/riscv64-none-elf/…/bin/blinky`

hello from blinky
float 3.1416
heap ok
```

**The `Size` line is printed after every freestanding link** and is silent on hosted targets and whenever the tool is
absent. Capacity is the governing constraint on a bare-metal target and the number is already known the moment the
link finishes; an informational line has no standing to fail a build.

**The generated project is four declarations** [docs/40-baremetal.md:230-249]:

```toml
[package]
name    = "blinky"
version = "0.1.0"

[build]
target = "riscv64-none-elf"

[dependencies]
riscv-virt-rt = "0.3.0"
```

There is **no `[target.*]` section, no linker script path, no load address, no `-nostdlib`, no
`-march`/`-mabi`/`-mcmodel`, no crt0, no C library name and no emulator command line.** The ISA flags come from the
engine's target table; the remainder comes from the board-support package named in `[dependencies]`.

`src/main.cpp` is an ordinary `main` [docs/40-baremetal.md:251-270]:

```cpp
import mcpplibs.riscv_virt_rt;

extern "C" int main() {
    board::println("hello from blinky");
    board::printf("float %.4f\n", 3.14159);
    void* p = board::alloc(64);
    board::println(p ? "heap ok" : "heap FAILED");
    board::release(p);
    return p ? 0 : 1;
}
```

No `_start` and no assembly entry point, because the BSP selects picolibc's semihosting `crt0` — the C runtime is
initialised before `main` and the return value reaches the host through semihosting. Only a board with **no C library
at all** needs an explicit entry point, declared by pointing `main` at the source file carrying `_start`.

**Switching ISA width is a flag** [docs/40-baremetal.md:317-335]:

```bash
mcpp run --target riscv32-none-elf
```
```
        Size blinky  text 10412  data 48  bss 5400  total 15860
hello from blinky
```

Neither the project's sources nor the BSP changed: the package selects its profile from `MCPP_TARGET_ARCH`, and the
ISA parameters come from the engine's table, which is **data rather than code** — supporting a further width is one
row.

### 6.3 What a freestanding target changes

[docs/40-baremetal.md:272-284]

| aspect | behaviour |
|---|---|
| link line | **built from nothing rather than extended**: `-nostdlib -nostartfiles -static`, no crt files, no dynamic linker, no C++ runtime. Appending `-nostdlib` to a hosted line would rely on the driver discarding earlier flags in the right order |
| linker selection | `ld.lld` addressed by **absolute path**, derived from the driver's own directory. `-fuse-ld=lld` resolves by name and finds GNU ld on any machine with binutils earlier on `PATH`, which then fails with `unrecognised emulation mode: elf64lriscv` |
| ISA flags | `-march`, `-mabi`, `-mcmodel` from one row per target in `src/freestanding/target.cppm` |
| C library | the **target's**, resolved by mcpp from the target's own table row exactly as the compiler is. A bare-metal project declares no libc, just as a hosted project declares no glibc. The engine puts the sysroot's library directory on the link search path, so a BSP selects out of it by bare name (`-lc`, `-lcrt0-semihost`) |
| exceptions and RTTI | **off on every translation unit in the graph, including a dependency's**, unless a package supplies a C++ runtime built for this target. There is otherwise no unwinder and no `libc++abi`; `std::optional::value()` alone would reference `__cxa_throw` and three further undefined symbols. The setting belongs to the **target** rather than a project's `cxxflags` because a BMI records it, and a dependency compiled with exceptions cannot be imported by a unit without them. A package declaring `provides = ["hosted-standard-library"]` reverses the default |
| `import std` | available only when a package in the graph provides `hosted-standard-library` and names its own `std` module source; otherwise rejected **at configure time** |
| entry point | `int main()` is available whenever something supplies a `crt0`; a BSP normally does |
| default linkage | static, and not as a preference: there is no loader |

A project with **no dependencies at all** still builds, which is the evidence that the ISA row alone is sufficient:
`Size norunner  text 12  data 0  bss 0  total 12` [docs/40-baremetal.md:285-290].

**Dead-section elimination belongs to the engine, not to a project.** Freestanding builds compile with
`-ffunction-sections -fdata-sections` and link with `--gc-sections`, and both halves are the engine's because a
dependency's translation units must carry them and a project cannot reach those. It became necessary rather than
merely economical when a C library began arriving from the dependency graph: a dependency's object files enter the
link **unconditionally**, unlike an archive member, which is pulled only while its symbol is undefined — costless when
the target has megabytes, fatal on a Cortex-M part with kilobytes [docs/40-baremetal.md:96-108].

WARNING: **a linker script becomes load-bearing in a new way.** An interrupt vector table is referenced by nothing —
the hardware reads it by address — so `--gc-sections` collects it. A board's script must say `KEEP(*(.vectors))`.
Measured: with the `KEEP` present, a function nothing calls is dropped, the table survives, and the image boots
[docs/40-baremetal.md:110-114].

**The artifact set for flashing** — a freestanding link produces **three** files
[docs/40-baremetal.md:553-567]:

```
target/riscv64-none-elf/<fingerprint>/bin/blinky        91640 bytes   ELF, for a debugger or `qemu -kernel`
target/riscv64-none-elf/<fingerprint>/bin/blinky.bin     8664 bytes   flat image, what a flasher accepts
target/riscv64-none-elf/<fingerprint>/bin/blinky.map    253369 bytes  link map
```

The flat image comes from an `objcopy -O binary` edge derived from the same payload as the driver. The map is an
**implicit output of the link edge** rather than a bare `-Wl,-Map=` flag, so deleting it causes it to be regenerated;
it is the only artifact that answers why a section is where it is, and why something was or was not pulled in from an
archive.

### 6.4 The freestanding standard-library subset

`import std` is one module over the **entire** library — threads, filesystem and iostreams included — so there is no
subset of it to build without an operating system. The parts that need no OS arrive as an ordinary dependency
[docs/40-baremetal.md:337-347]:

```toml
[dependencies]
riscv-virt-rt    = "0.3.0"
std-freestanding = "0.2.0"
```
```cpp
import mcpplibs.riscv_virt_rt;
import mcpplibs.std.freestanding;      // not `import std;`
```

**103 of the 110 `std/*.inc` headers** the LLVM 22.1.8 payload ships, generated by mechanical selection rather than
written as an export list. Available entities include `array`, `span`, `optional`, `expected`, `atomic`,
`string_view`, `ranges`, `algorithm`, `bit`, `charconv`, `concepts`, `type_traits`, `tuple`, `utility` and
coroutines. What the subset excludes is excluded **at compile time** [docs/40-baremetal.md:383-399]:

```cpp
std::mutex m;
```
```
error: no type named 'mutex' in namespace 'std'
```

Measured for a program using `std::ranges::sort`, `std::optional`, `std::atomic`, `std::span` and `std::string_view`:
`Size blinky  text 19564  data 72  bss 5632  total 25268` [docs/40-baremetal.md:373-381].

**The allocating half is a separate axis.** The subset does not change what compiles — all headers are included
unconditionally and `std::vector` compiles today. What fails is the **link**, because a freestanding target has no
compiled `libc++` and therefore no `operator new` [docs/40-baremetal.md:401-416]:

```
ld.lld: error: undefined symbol: operator new(unsigned long)
>>> referenced by allocate.h:58
```

| needs nothing | needs an allocator |
|---|---|
| `array` `span` `optional` `expected` `atomic` `string_view` `ranges` `algorithm` `bit` `charconv` `tuple` | `vector` `string` `deque` `list` `map` `set` `unordered_*` `function` `any` `make_unique`, and the default coroutine frame |

An allocator arrives with a **feature**, and the choice belongs to the program because `operator new` is a
whole-program singleton [docs/40-baremetal.md:417-453]:

```toml
[dependencies]
riscv-virt-rt    = "0.4.0"
std-freestanding = { version = "0.3.0", features = ["alloc-libc"] }
```

| feature | forwards to | when to pick it |
|---|---|---|
| `alloc-libc` | the target's C library | the shorter path when the target has one |
| `alloc-kal` | openkal | when the same sources must also build for a target whose environment is not a C library |

On bare metal with `alloc-kal` the **board package supplies the openkal backend**, because the console and the heap
region are board facts:

```toml
riscv-virt-rt    = { version = "0.4.0", features = ["openkal"] }
std-freestanding = { version = "0.3.0", features = ["alloc-kal"] }
```

Both failure modes are reported **when the graph resolves**, naming packages rather than mangled symbols:

```
error: no package provides capability 'freestanding-allocator' required by 'std-freestanding'

error: capability 'freestanding-allocator' has multiple providers in the graph:
       [std-freestanding-alloc-kal, std-freestanding-alloc-libc]
```

### 6.5 The zero-libc tier

`[target.<triple>].sysroot` overrides the C library the target table binds, on the same axis as `toolchain` overriding
the compiler pin. (On a `*-windows-msvc` row the same key names the MSVC toolset instead and takes only `msvc@...` spellings,
2026.9.24.1+; see `mcpp-toml.md` §6.) **The empty string declines a C library altogether** [docs/40-baremetal.md:455-480]:

```toml
[target.riscv64-none-elf]
sysroot = ""
```

With that line the C headers leave the compile line and the C library leaves the link; `#include <stdio.h>` stops
resolving, and the image contains only what the project and its dependencies put in it. Measured: a self-contained
image with its own entry point and linker script links at **108 bytes** and boots.

**An absent key and an empty one are different answers.** Absent inherits the target table's C library;
present-and-empty declines it. A kernel or a bootloader wants the second:

```bash
mcpp new mykernel --template riscv-virt-rt:nolibc   # an entry point, a memory map, a device: 369 bytes
```

Declaring a *different* C library on a zero-libc-by-default row is the same key
[docs/40-baremetal.md:120-130]:

```toml
[target.aarch64-none-elf]
sysroot = "xim:picolibc-aarch64@1.8.12"
```

WARNING: **four C functions are an obligation, not a convenience.** `memcpy`, `memmove`, `memset` and `memcmp` must
exist because the compiler lowers structure assignment and array initialisation onto them.
`std-freestanding-nolibc` supplies those and `strlen` [docs/40-baremetal.md:482-486].

The subset composes with this tier: `std-freestanding` with `features = ["nolibc"]` compiles against no C library at
all, and **94 of its 103 headers do**. The obstacle was never that the subset wants a C library — libc++ ships
wrappers for the C headers (`string.h` and siblings) that reach the real header through `#include_next` to obtain
`size_t`, `mbstate_t`, `time_t` and `EOF`; with no C library the chain has nothing to continue to, and the wrapper
fails on a missing **type** rather than a missing header, which is why the cause is not evident from the error. Four
small headers restore the chain, and the feature pulls them in [docs/40-baremetal.md:487-495].

A BSP serves this tier too, for the same reason it is worth having at all — where a machine's UART is, where its RAM
begins and which emulator boots it are not C library facts [docs/40-baremetal.md:497-506]:

```toml
[dependencies]
riscv-virt-rt = { version = "0.5.0", features = ["nolibc"] }
```

WARNING: **adding `std-freestanding-nolibc` DIRECTLY alongside a C library fails silently rather than loudly.** A C
library ships as an archive, and an archive member is pulled only while its symbol is still undefined; a dependency
package's object files enter the link unconditionally. The package therefore defines `memcpy` first, the C library's
member is never pulled, and the build succeeds — with the byte-at-a-time implementations in place of the C library's
optimised ones, and **no report of the substitution**. Measured with picolibc present: a cold build links, and `nm`
finds one definition [docs/40-baremetal.md:506-514].

### 6.6 Running and testing on the target

**mcpp ships no default runner.** Which emulator, which machine model and which firmware mode are **board facts** —
two boards on the same ISA need different argv (`-bios default` for an OpenSBI boot against `-bios none -semihosting`
for a picolibc image) — so an engine that guessed one would have to be fought by the other
[docs/40-baremetal.md:593-597].

```bash
mcpp run                        # the default runner
mcpp run --runner flash         # a named one
mcpp run --list-runners         # what this project supplies
mcpp why runners                # the same list, beside everything else resolved
mcpp run --features hardware    # the same board, reached the other way
```
[docs/41-devices.md:29-36] — `--runner <NAME>`, `--list-runners` and `--no-runner` verified on the binary
(`mcpp run --help`, `2026.9.15.2`). `mcpp why runners` is a **topic argument**, not a flag: `mcpp why --help` lists
only `--target`, `--toolchain` and `--format`.

`mcpp run` takes `--features` and `--profile`, the same axes `build` and `test` take — which is what makes selecting
an environment a command rather than a manifest edit [docs/41-devices.md:38-44].

**`mcpp run` is the whole of the common case, including on real hardware.** On a device, running a program means
writing it, resetting, attaching to its output and reading its exit status — which is **one** command
(`probe-rs run`, `qemu-system-* -kernel`), not several. A board therefore supplies that as its **default** runner, and
the command a developer types does not change when they move from an emulator to a board. Named runners exist for
what remains: writing an image without running it, observing a console, starting a debug server, erasing a part,
deploying without starting [docs/41-devices.md:46-51].

**The engine knows no runner names.** `flash`, `serve`, `deploy`, `submit` and `logcat` are equally unknown to it: it
knows only that a package may supply named runners, and performs the argv it finds. A fixed set in the engine would
decide, in the engine, which domains are expressible [docs/41-devices.md:52-57].

**A project override wins, and is reported rather than applied silently**
[docs/40-baremetal.md:569-591]:

```toml
[target.riscv64-none-elf]
runner = ["qemu-system-riscv64", "-machine", "virt", "-nographic",
          "-no-reboot", "-bios", "default",
          "-s", "-S",                    # wait for a debugger on the first instruction
          "-kernel"]
```
```
        note [target.riscv64-none-elf].runner overrides the runner a dependency supplied
```

The artifact path is **appended** to the template, or substituted for `{}` when the template contains that token.
Appending is the common shape, because `-kernel <image>` ends the line.

**When no runner is configured** [docs/40-baremetal.md:625-640]:

```
error: no runner is configured for 'riscv64-none-elf' — a freestanding artifact cannot execute on this machine.
       Declare how to run it:

           [target.riscv64-none-elf]
           runner = ["qemu-system-riscv64", "-machine", "virt",
                     "-nographic", "-no-reboot", "-bios", "default", "-kernel"]

       The artifact path is appended, or substituted for `{}` if the template contains it.
       A board-support package normally supplies this so you do not have to.
```

**And when `import std` is written on such a target** — at configure time, not at link
[docs/40-baremetal.md:601-621]:

```
error: `import std;` is not available on 'riscv64-none-elf' — a freestanding target has no hosted standard library.
       … Use the freestanding subset instead …
           [dependencies]
           std-freestanding = "0.2.0"
       then `import mcpplibs.std.freestanding;` in place of `import std;`.
```

Reporting a missing `std` module source instead would send the reader to look for a broken payload, when nothing is
missing from the toolchain.

**`[target.<triple>].runner` is not bare-metal-specific.** A hosted cross target — an `aarch64-linux-musl` artifact on
an x86_64 host — takes the same key with a **user-mode** emulator such as `qemu-aarch64-static` in place of the system
emulator; on such a target an absent runner is not an error until the kernel refuses the artifact
[docs/40-baremetal.md:642-648].

**Testing works exactly as `docs/08-testing.md` describes it.** Each `tests/*.cpp` becomes **its own image**, and the
board's runner executes it. What makes the verdict work is semihosting, which propagates the firmware's `main` return
value to the emulator's exit code — which is why the model is *identical* to a hosted run rather than merely similar
[docs/40-baremetal.md:516-551]:

```
$ mcpp test
   Compiling boots (test)
     Running bin/boots
boots: console
boots ... ok (0.02s)

 test result ok. 1 passed; 0 failed; finished in 0.58s (build 0.05s + run 0.02s)
```

WARNING: **the AArch32 semihosting exit call has two spellings and only one carries a status.** `SYS_EXIT` (`0x18`)
takes its reason code in `r1` **directly**; the `{reason, code}` block is `SYS_EXIT_EXTENDED` (`0x20`), which exists
because a 32-bit `r1` cannot carry both a reason and a status. Passing the block to `0x18` **prints everything
correctly and then reports the wrong exit status**. Measured twice: an ARMv7-A image exiting 0 reported 1, and an
`openarch` Cortex-M example printed `both tasks observed preemption` and exited 1 with every assertion on its output
passing. A board that only checks what it printed cannot see the difference, which is why `tests/e2e/332` and `336`
both read `$?`, and both take it from the emulator rather than from the tail of a pipeline
[docs/40-baremetal.md:56-67].

Three further runner facts [docs/41-devices.md:145-173, 224-231]:

- **Termination is declared, not inferred.** `mcpp::runner_longlived("monitor")` marks a runner with no natural end; a
  long-lived runner that does not say so is waited on until the operator ends it.
- **Runs that cannot overlap say so**: `mcpp::run_exclusive()`.
- **Exactly one dependency may supply a given runner name.** A second is an error naming both packages; there is no
  ordering rule that picks a winner. A runner the selected environment does not supply **stays absent**, and
  `mcpp run --runner debug` then reports that no such runner exists and lists the ones that do.

### 6.7 Writing a board-support package

**Location is a target fact, selection is a board fact** [docs/40-baremetal.md:292-310]:

| layer | owns | example |
|---|---|---|
| engine | the ISA profile, the freestanding link line, the artifact set, the single read point for how an artifact is executed | `-march=rv64gc -mabi=lp64d -mcmodel=medany -ffreestanding` |
| target | which compiler and which C library, both resolved from the target's row and installed on demand | `pin = llvm@22.1.8`, `sysroot = xim:picolibc-riscv@1.8.12` |
| BSP | which startup object and libraries to select, which linker script, which emulator invocation | `-lcrt0-semihost`, `picolibcpp.ld`, `qemu-system-riscv64 -machine virt …` |

**A second board on the same ISA is a change of the three values in the bottom row. It requires no engine change.**
The middle row is what keeps a package from having to name a C library: earlier versions of both ecosystem packages
named a libc package in the environment table directly, which bound a package to one libc, one architecture and one
compiler implementation.

**What a BSP supplies** [docs/34-authoring-a-bsp.md:17-32]:

| | content |
|---|---|
| the memory map | a linker script — the one fact a program can neither derive nor guess |
| the startup code | what runs before `main`, and the vector table |
| an exported module | what the program imports to reach the board's console and peripherals |
| **the runner** | how `mcpp run` and `mcpp test` reach the board at all — the one that is easy to leave out, and without it every consumer writes its own emulator invocation |

**One package, two environments.** A board reached through an emulator and the same board through a debug probe differ
**in the argv of their runners and in nothing else** — the linker script, the startup code, the memory map and the
exported module are the same board. So the environment is a **feature**
[docs/34-authoring-a-bsp.md:33-68]:

```toml
[features]
default  = ["emulator"]
emulator = {}
hardware = {}

[feature-xlings.emulator]
"xim:qemu-arm" = { version = "9.2.4-1", when = "run" }

[feature-xlings.hardware]
"xim:probe-rs" = { version = "", when = "run" }
```

`emulator` is the default, and that is **a decision about who is reading**: someone meeting the package has no board
on their desk; someone who does has a reason to say so. **Both are on the `run` tier, a second and independent
gate** — the feature says *who* needs the tool, the tier says *when* — so a CI job that builds and never flashes
downloads nothing at all.

The C library is a feature too, on the zero-libc rows [docs/34-authoring-a-bsp.md:70-88]:

```toml
libc = {}

[feature-deps.libc]
picolibc.picolibc = "1.8.12.3"
```

A C library arrives as a **source** package compiled with the program's own flags, so there is no multilib to match
and no ABI convention to get wrong. `mcpp run --features libc` is the whole of it.

**The directives a BSP emits, and their scope** [docs/40-baremetal.md:689-718]:

| directive | effect | scope | reaches the consumer |
|---|---|---|---|
| `mcpp:link-lib=<name>` | `-l<name>`. Bare names suffice: the target sysroot's library directory is already on the search path | `LinkGlobal` | yes |
| `mcpp:link-search=<dir>` | `-L<dir>`, for a library the package carries itself | `LinkGlobal` | yes |
| `mcpp:link-script=<abs path>` | `-T <path>`. A relative path resolves against the package root, so a script belonging to the target's C library must be named **absolutely** | `LinkGlobal` | yes |
| `mcpp:runner=<token>` | appends **one** argv token — argv is ordered, so the template is built by repetition, one directive line per token | `RunGlobal` | yes |
| `mcpp:include-dir=<dir>` | an include directory **for this package only** | `PackagePrivate` | **no** |

**The asymmetry is what lets the engine work without a sysroot concept in the directive layer at all**: a BSP includes
the target's C headers privately and exports what it wants visible as a C++ module. Consumers import that module; they
do not inherit an include path.

Three engine queries supply the paths a BSP must not hardcode [docs/40-baremetal.md:699-703]:
`mcpp::sysroot_dir()` (the target's C library root), `mcpp::xpkg_dir(ns, name)` (an installed payload's directory),
`mcpp::target_arch()` (the architecture being built for).

**A complete `build.mcpp`** — the QEMU RISC-V `virt` board's whole build logic, comments removed
[docs/40-baremetal.md:719-758]:

```cpp
import mcpp;
import std;

int main() {
    const std::string arch = mcpp::target_arch() ? mcpp::target_arch() : "";
    const bool rv32 = (arch == "riscv32");

    // Selected out of the target's C library, by bare name.
    mcpp::link_lib("crt0-semihost");
    mcpp::link_lib("c");
    mcpp::link_lib("semihost");
    mcpp::link_lib(std::format("clang_rt.builtins-{}",
                               rv32 ? "riscv32" : "riscv64").c_str());

    // This machine's memory layout, asked for rather than declared.
    if (const char* sysroot = mcpp::sysroot_dir(); sysroot && *sysroot)
        mcpp::link_script(std::format("{}/lib/{}/picolibcpp.ld", sysroot,
                                      rv32 ? "rv32imac/ilp32" : "rv64gc/lp64d").c_str());

    // The emulator is named by ABSOLUTE path, because a bare name resolves
    // through PATH to a shim that dispatches against its own owner home.
    if (const char* qemu = mcpp::xpkg_dir("xim", "qemu-riscv"); qemu && *qemu) {
        mcpp::runner(std::format("{}/bin/qemu-system-{}", qemu,
                                 rv32 ? "riscv32" : "riscv64").c_str());
        for (auto a : {"-machine", "virt", "-nographic", "-no-reboot",
                       "-semihosting", "-bios", "none", "-kernel"})
            mcpp::runner(a);
    }

    mcpp::rerun_if_env_changed("MCPP_TARGET_ARCH");
    return 0;
}
```

and the manifest declares the emulator and nothing else:

```toml
[xlings.workspace]
"xim:qemu-riscv" = "9.2.4-1"
```

**A declaration there provisions the package on the first build** (since 2026.8.29), and is also what lets
`mcpp::xpkg_dir` answer *"where did that package land"*. Both halves matter: the same declaration installs the
emulator and tells the build program where it went [docs/40-baremetal.md:654-666].

WARNING: **a build program must still not assume the directory exists.** Provisioning runs for the package that
**declares** the deps, and a build program can be reached through paths where that has not happened — a dependency of
a project that declares nothing, or an environment where `--offline` / `MCPP_NO_AUTO_INSTALL` refused
[docs/40-baremetal.md:667-687]:

```cpp
if (const char* dir = mcpp::xpkg_dir("xim", "qemu-riscv"); dir && *dir) {
    mcpp::runner(std::format("{}/bin/qemu-system-riscv64", dir).c_str());
    // … the rest of the argv …
} else {
    mcpp::warning("qemu-riscv is not installed, so `mcpp run` has no runner. "
                  "Install it once:  xlings install qemu-riscv -y");
}
```

Without that line the build succeeds, configures no runner, and `mcpp run` reports a missing runner with advice about
writing a `runner` key — **true in general, and not the cause here.**

NOTE: `docs/41-devices.md:58-80` gives the alternative and now-preferred spelling for the runner program itself:
**name the program, not its path.** mcpp locates it in the `bin/` of a payload declared under `[xlings.workspace]` by
**any** package in the graph (the consuming project first, then its dependencies) and then on `PATH` — and naming it
lets mcpp report exactly which directories it searched, where an absolute path computed from `xpkg_dir` can silently
return empty. Both spellings appear in upstream docs; the BSP chapter's is the older one. `[unverified]` which is
preferred at this baseline.

Two board-specific traps worth keeping [docs/40-baremetal.md:767-777]:

- **Linking `clang_rt.builtins` is not optional on the RISC-V board.** picolibc formats floating-point values through
  ryu, which performs 128-bit shifts, and rv64 has no instruction for them; without the builtins the link fails on
  `__ashlti3` and `__lshrti3`. A check for 64-bit division does not reach this case, because rv64gc has a hardware
  `divu`.
- **An mcpp older than the one a package was written for cannot be detected from within the package.**
  `if constexpr (requires { mcpp::runner("x"); })` is a hard error on an unknown qualified name rather than `false`,
  so the language offers no feature test. The engine compensates by appending an upgrade note when a `build.mcpp`
  fails to compile with an error naming a non-member of `mcpp`.

BSP limitations [docs/34-authoring-a-bsp.md:128-133]: a BSP declares its emulator and probe driver as payloads, so a
board whose tooling is not published for a platform cannot be reached from it; and the machine table is per-triple, so
a board needing a model the table does not carry is a change to the BSP, not a project-side override.

### 6.8 The ecosystem packages, and where they live

Verified against the GitHub org listing, 2026-09-16 (`gh repo list mcpplibs`):

| package | what it is |
|---|---|
| [`mcpplibs/riscv-virt-rt`](https://github.com/mcpplibs/riscv-virt-rt) | BSP for QEMU's RISC-V `virt` — picolibc, startup, memory layout, emulator runner. Ships the `riscv-virt-rt` and `riscv-virt-rt:nolibc` templates |
| [`mcpplibs/aarch64-virt-rt`](https://github.com/mcpplibs/aarch64-virt-rt) | BSP for QEMU's aarch64 `virt` — **zero-libc tier** |
| [`mcpplibs/cortex-m-rt`](https://github.com/mcpplibs/cortex-m-rt) | BSP for Cortex-M — startup, memory layout, semihosting console, and the runners that reach a board; the `emulator`/`hardware` feature pair of §6.7 is its shape [docs/41-devices.md:211] |
| [`mcpplibs/std-freestanding`](https://github.com/mcpplibs/std-freestanding) | the 103-header subset (§6.4) |
| `std-freestanding-alloc-libc` / `-alloc-kal` / `-nolibc` | the three allocator / no-libc providers |
| [`mcpplibs/picolibc`](https://github.com/mcpplibs/picolibc), `compiler-rt-builtins`, `libcxx` | source packages compiled with the consuming program's own flags |
| [`mcpplibs/openkal`](https://github.com/mcpplibs/openkal) | the portable **kernel-ABI specification**, with the C++ modules that declare it |
| `openkal-linux` / `-macos` / `-windows` / `-uefi` / `-opensbi` / `-emscripten` | six backend implementations |
| `openkal-musl`, `openkal-llvm-runtime` | musl 1.2.5 redirected onto openkal; libc++/libc++abi/libunwind configured for it |
| [`mcpplibs/openarch`](https://github.com/mcpplibs/openarch) | the **architecture-mechanism** layer: execution contexts, traps and address spaces, as one interface over several instruction sets |
| [`mcpplibs/sbase`](https://github.com/mcpplibs/sbase) | 97 suckless tools recompiled above `openkal-musl`, **sources unmodified**, on Linux, macOS and Windows |

**openkal is a target-side layer, not a target.** `kernel-abi` is one of the five resolved layer names, `openkal` is
the **interface** and `openkal-windows` an **implementation** of it — collapsing the two would conceal which is which
[docs/22-target-side.md:29, 187-188]. The layer table [docs/24-openkal-cross.md:66-73]:

| package | layer it provides | on what |
|---|---|---|
| `openkal` | — | the specification, and the C++ modules that declare it |
| `openkal-linux` | `kernel-abi` | Linux system calls (the reference implementation) |
| `openkal-macos` | `kernel-abi` | the macOS system-call surface |
| `openkal-windows` | `kernel-abi` | Win32 and the object manager, **using no C runtime symbol** |
| `openkal-opensbi` | `kernel-abi` | the RISC-V Supervisor Binary Interface, no operating system |
| `openkal-uefi` | `kernel-abi` | UEFI Boot Services, before an operating system exists |
| `openkal-musl` | `c-abi` | musl redirected onto openkal, ported once |
| `openkal-llvm-runtime` | `compiler-runtime`, `c++-abi` | compiler-rt builtins, libunwind, libc++abi and libc++ configured for `openkal-musl` |

A project's whole declaration is two lines [docs/24-openkal-cross.md:41, 435]:

```toml
[dependencies]
openkal-llvm-runtime = "0.1.3"   # → openkal-musl → openkal-<os>
```

plus `[toolchain] default = "llvm@22.1.8"`; `examples/06-openkal-cross` is one source built for four machines from any
host [docs/03-examples.md:58]. The version in that line is the docs' illustration (docs/24 itself writes `0.1.1` at 2026.9.21.3);
the real chain is at 0.15.x - see §6.10 for the pairs and what changed.

WARNING: **openkal dependencies must be target-scoped.** Putting them in a plain `[dependencies]` drags the **host
graph** into openkal too; the correct form is `[target.x86_64-linux-musl.dependencies]` (`../SKILL.md` §7, with
configure-time evidence).

`openkal-emscripten` is the odd one and worth knowing why: Emscripten supplies its **own** C library over a JavaScript
host, so an implementation for it cannot be written the way `openkal-linux` is — beneath a C library. It is the first
implementation in this ecosystem written **above** one, which is where the vocabularies of a C library and of openkal
do not correspond [docs/24-openkal-cross.md:252-265].

`openarch` is what a **kernel or raw bare-metal program** builds on, beneath even openkal: for `x86_64-none-elf` with
"the reset vector, with nothing beneath", the layer is `none` or `openarch`
[docs/24-openkal-cross.md:394, 408; docs/40-baremetal.md:54, 117-119].

### 6.9 What is NOT verified on the bare-metal chain

[docs/40-baremetal.md:779-813]

- **Continuous verification is Linux-only.** Engine CI runs a `baremetal` job covering four end-to-end scripts, and
  the two ecosystem packages run RISC-V 64 and 32 under QEMU in their own repositories — all on `ubuntu-24.04`. macOS
  and Windows hosts are *expected* to work, because the payload is a cross-compiler and `xim:qemu-riscv` publishes
  assets for five host targets, but **that expectation is not covered by a test**.
- **`std::format`, `std::sort` over builtin scalar types, and a complete `std::string` fail at LINK time**, naming the
  undefined symbol. libc++ places those entities in the compiled library — the scalar `__sort` instantiations are
  `extern template`, with no macro that disables them — so a target-built `libc++.a` is required and **no such payload
  is published**.
- **Exceptions and RTTI stay disabled across the whole graph** unless a package provides `hosted-standard-library`,
  which `mcpplibs/openkal-llvm-runtime` does by carrying libc++, libc++abi and libunwind configured for the target.
- **Board coverage is one board family.** `riscv32-none-elf` demonstrates that the ISA table is data, not that a
  second machine has been ported.
- **C library substitution is verified only for the empty value.** Pointing `sysroot` at a *different* C library is
  accepted and installed through the same channel, but no second bare-metal C library is published, so that path is
  untested.
- **`qemu-riscv` on `win32-arm64`** publishes no asset, so installation fails there. The failure is correct rather
  than silent, but that host cannot run a bare-metal image.
- **An ecosystem CI breadth gap**: mcpp-index's `tests/examples/` workspace members run unconditionally on three
  platforms with no capability gate, so a package requiring an emulator and a target sysroot cannot be added there.
- The document's worked transcripts were measured on **2026.8.20.1**, not at this baseline, and sizes are explicitly
  "illustrative of magnitude rather than fixed values" — the same project measured `text 8844` under 2026.8.19.4 and
  `text 8572` under 2026.8.20.1.

### 6.10 The openkal chain after 2026.9.16: versions, interfaces, and what the C library now does

Verified 2026-09-23 against `mcpplibs/mcpp-index` `origin/main @ 9c6ec87` and against each tag's own `mcpp.toml` (GitHub
contents API). **Read tags and the index, not the Releases pages**: at that date openkal-musl's newest Release page still said
0.16.0 while tags and the index went to 0.19.1, and the README's own pairing table stops at 0.16.0.

**Pin only the top of the chain.** `openkal-llvm-runtime` pins `openkal-musl` **exactly**, and openkal-musl pins the specification
and the per-OS implementations. A C++ program names `openkal-llvm-runtime` and nothing else; naming openkal-musl as well is
"irreconcilable versions", not redundancy. The pairs, read from the tags:

| `openkal-llvm-runtime` | pins `openkal-musl` | that openkal-musl pins: `openkal` spec / `-linux` / `-macos` / `-windows` |
|---|---|---|
| 0.10.0 | 0.14.0 | 0.13.0 / ... |
| 0.11.0 | 0.15.0 | 0.13.0 / ... |
| 0.12.0 | 0.16.0 | **0.14.0** / 0.14.0 / 0.11.0 / 0.9.0 |
| 0.13.0 | 0.18.0 | 0.14.0 / 0.15.0 / 0.12.0 / 0.10.0 |
| 0.14.0 | 0.19.0 | 0.14.0 / 0.15.0 / 0.12.0 / 0.10.0 |
| 0.15.0 | 0.19.0 | same as above |
| 0.15.1 | 0.19.1 | 0.14.0 / 0.15.0 / 0.12.0 / **0.10.1** |

(No `openkal-llvm-runtime` tag pins openkal-musl 0.17.0. The index's `min_mcpp` at that commit is `2026.9.18.3`, `latest_mcpp`
`2026.9.21.2`.) What each step changed, as far as a consumer can observe:

- **openkal specification 0.14** (pinned from openkal-musl 0.16.0): the terminal mode word gains a third position,
  **`KAL_TERM_PASS_CONTROL`** - whether the environment keeps keystrokes (interrupt and friends) for itself. It is spelt so that an
  implementation released before it reads as zero. The same release **withdrew the one name it had given a set of interfaces**
  (`hosted`) in favour of consumers enumerating what they need - which is what `[kernel-abi] requires-interfaces` in mcpp 2026.9.20.1
  carries (`mcpp-toml.md` §17.3).
- **openkal-musl 0.16.0 - terminals and signal dispositions reach reality** (closes mcpplibs/openkal-musl#36):
  - `tcgetattr` / `tcsetattr` go through `openkal.terminal`: `TCGETS`, `TCSETS`/`TCSETSW`/`TCSETSF` and `TIOCGWINSZ` really act, so
    `cfmakeraw` + `tcsetattr` enters raw mode and the interrupt key arrives as byte `0x03`. Only the three positions openkal names
    (line assembly, echo, reserved keystrokes = `ISIG`) are applied. `OPOST`, line speed, control characters, `VMIN`/`VTIME` and
    the drain semantics of the `W`/`F` forms are **accepted with no effect** - measurably, raw-mode output still gets a carriage
    return before each newline, unlike the same program on the system C library. Before 0.16.0, `TCGETS`/`TIOCGWINSZ` returned
    success without filling the structure and `TCSETS` was refused (ENOTTY).
  - `sigaction` accepts a disposition **only where it is already in effect**: `SIG_DFL` succeeds for every signal but `SIGPIPE`,
    `SIG_IGN` succeeds for `SIGPIPE` alone, and the enquiry reports `SIG_IGN` for `SIGPIPE`. Any real handler is still `ENOSYS` -
    openkal has no asynchronous delivery. Before 0.16.0, `SIG_IGN` was accepted for **every** signal and installed for none, so a
    program that asked not to be killed by Ctrl+C was told it had succeeded and was killed by it.
  - Consequence for a TUI above openkal-musl: raw mode and "Ctrl+C is a byte" work from 0.16.0; window-size changes still cannot be
    delivered as `SIGWINCH` and have to be polled with `TIOCGWINSZ`; graceful shutdown cannot rely on a signal handler.
- **openkal-musl 0.17.0**: a top-level `[c-abi-absent]` table of 24 rows, each asserted against the built objects by the package's
  own CI, and implementation pins moved to openkal-linux 0.15.0 / openkal-windows 0.10.0. It needs no engine floor (mcpp below
  2026.9.20.1 ignores the table).
- **openkal-musl 0.19.0 / openkal-llvm-runtime 0.14.0**: the installed headers that size `jmp_buf` (`bits/setjmp.h`) and
  `unw_context_t` (`__libunwind_config.h`) test `__MCPP_TARGET_WINDOWS__ || __CYGWIN__`, so they are right on engines before and
  after mcpp 2026.9.21.2 withdrew `__CYGWIN__`. **Below these versions on an engine >= 2026.9.21.2, a Windows target silently gets
  the wrong record size** - the one residual window upstream names.
- **openkal-llvm-runtime 0.15.0** makes `thread_local` destructors run on PE and Apple targets (it exports `__cxa_thread_atexit` and
  keeps the pending list in the TLS key's own value, because emutls freed the old storage first); `doctest` and `spdlog` had stopped
  at `undefined symbol` on `x86_64-windows-gnu`.

Engine side of the same period (details in `../SKILL.md` §7 and `version-notes.md` §2): openkal-musl declares `[c-abi]
presents = "posix"` from 0.15.0, which on Linux realises to nothing (so GCC stays usable, 2026.9.18.2) and on Windows substitutes
the compile triple; the engine defines `__OPENKAL__` for every target-side unit; and on Clang a graph-supplied C library closes the
host header search (`-nostdlibinc`, 2026.9.17.3), so code that leaned on host headers fails loudly instead of mixing two C
libraries.

## 7. Roadmap: what is planned, and what exists

### 7.1 `mcpp-community/mcpp#403`

[https://github.com/mcpp-community/mcpp/issues/403](https://github.com/mcpp-community/mcpp/issues/403) — *"RFC: mcpp
对裸机/freestanding target 的支持（riscv64-none-elf 类，toy_kernel 用例）"*, by `lildengzi`, opened 2026-08-09,
**CLOSED as COMPLETED on 2026-08-18**, last touched 2026-08-20, two comments (GitHub API, checked 2026-09-16).

**It is a historical requirements document, not a live roadmap.** Against mcpp 2026.8.8.4 it recorded five pain points
from building a RISC-V 64 freestanding kernel (`toy_kernel`, qemu `virt`, `-kernel` boot):

| pain point | what it looked like then |
|---|---|
| mcpp could not express a bare-metal target at all | the project was treated as an x86_64 host, so `-march=rv64gc` / `-mcmodel=medany` / `-mstrict-align` were parsed against `x86_64-unknown-linux-gnu` and a plain `mcpp build` **failed outright**: `unsupported argument 'medany' to option '-mcmodel='`, `unknown target CPU 'rv64gc'` |
| no freestanding link model | no custom linker script, no `-nostdlib` mode; a Makefile did the link by hand |
| `mcpp run` assumed a hosted executable | run/debug/test were hand-written in the Makefile |
| artifact directories collided | hosted-musl output and bare-metal hack output shared `target/`, and the Makefile picked one with `find target -name "*.a" \| head -1` |
| `.S` bare-metal flags were smuggled through a glob | `flags = [{ glob = "src/**/*.S", asmflags = [...] }]`, and assembly was parsed against the host too |

and asked five open questions: how to express the target (a `riscv64-none-elf` row, or a `cfg(freestanding)`
predicate); how `CLibMode::None` would reach a custom `-T link.ld`; whether `mcpp run` could take a
"qemu `-kernel`"-shaped runner or at least a configurable command template; whether `import std` needed a degradation
path; and how `riscv64-none-elf` toolchains (newlib / picolibc) would be packaged in xim.

**All five are answered in shipping mcpp**, which is why the issue is closed — §6 is the answer sheet: the thirteen-row
target table, the freestanding link line built from nothing, `[target.<triple>].runner`, the configure-time
`import std` refusal that names `std-freestanding`, and `xim:picolibc-*` as a target sysroot resolved from the row.

The issue also notes its own relations: `#276` covers **hosted** embedded Linux SDKs (Buildroot/Yocto, with libc and
sysroot) and is a different line; and an earlier official embedded-platform design (decision #15) had **deferred**
freestanding, which this RFC reopened.

The second comment (`Sunrisepeak`, 2026-08-20) is the maintainer's pointer list — `std-freestanding`,
`riscv-virt-rt`, `openkal` with its UEFI / OpenSBI / Linux / Windows / macOS backends, plus `openkal-musl` and
`sbase`. WARNING: **its doc link is `docs/zh/13-baremetal.md`, which 404s on `main`** (§0.2).

### 7.2 openhal — planned, unimplemented, and not in #403

WARNING: **`openhal` appears nowhere in `#403`, nowhere in `docs/`, and there is no `mcpplibs/openhal` repository**
(issue body and both comments, plus the org listing, checked 2026-09-16). Its only occurrences in the clone are in
**design records** under `.agents/docs/` — which upstream's own `docs/README.md` says are *not* user documentation and
carry no stability promise, and which the docs tree deliberately never cites.

What those records say, as **plan** [.agents/docs/2026-08-19-freestanding-baremetal-implementation-plan.md:266-290]:
the "D track" is a four-stage roadmap **explicitly excluded from the implementation plan's milestones**, ordered by
threshold × weight of precedent — openkal first (lowest threshold, thickest precedent, and the natural backend for the
std subset), openarch last (highest risk, two unverified hard primitives).

| stage | delivers | gate to continue | stop signal |
|---|---|---|---|
| **D0** probe | `openkal` minimal world (`io/streams`, `clocks/monotonic`, `memory/alloc`), two backends, conformance skeleton | **a third party implements a third backend** — the real variable | nobody does within six months ⇒ stop at D0 and use it as internal infrastructure |
| **D1** openkal SPEC v0.1 | frozen interface list, C ABI mapping, three official backends (linux / **windows** / bare), conformance suite | all three pass conformance; the Windows backend does **not** go through MSVC CRT's POSIX compat layer | the Windows backend cannot be built without emulation ⇒ the SPEC's shape is wrong, redesign |
| **D2 `openhal`** | device-service interfaces (Console / Serial / Spi / I2c / Gpio / Pwm / Adc / Delay) plus an `openhal-linux` implementation | **one driver package runs on both a bare-metal MCU and Linux** — the shape `linux-embedded-hal` already proved | driver authors do not come ⇒ stop; openhal does not affect openkal |
| **D3 `openarch`** | arch mechanism (Context / Trap / AddressSpace / Atomics / PerCpu / Tick / Boot), two arch implementations | two hardest primitives survive on two real architectures: one piece of generic kernel code type-correct **and** semantically correct on both, with no extra instructions after LTO | context switching or the page-table-entry abstraction breaks ⇒ stop; everything past it would be illusion |

Status in those records: **openhal is "designed, not implemented"**
[.agents/docs/2026-08-20-freestanding-ecosystem-positioning.md:35, 88]. NOTE: `openarch` (D3) **does** have a published
repository and is referenced by `docs/40` and `docs/24`, so it is further along than the plan's ordering implies —
treat the D-track sequence as a design record, not as current state.

Three disciplines in those records explain the engine's shape and are worth carrying even though the track is not
shipping [.agents/docs/2026-08-19-freestanding-baremetal-implementation-plan.md:292-299;
.agents/docs/2026-08-20-freestanding-ecosystem-positioning.md:103]:

1. **The engine will never know HAL / KAL / arch as concepts.** All three are **packages**; backend selection is a
   conditional dependency, with **zero new axes**. Once the engine begins to understand KAL, the "no board database"
   failure mode returns at much larger scale.
2. **A missing capability does not exist at compile time** — not a run-time `ENOSYS`. Silent degradation is
   forbidden; the measured example is §6.4's `no type named 'mutex' in namespace 'std'`.
3. **A conformance suite is a required companion to splitting repositories**, not an optional extra: without one, N
   repositories degrade into N implementations each interpreting the interface for itself.

## 8. Reading this from a CLI or desktop project

Two lines, because this page is a general reference and not a filter: on such a project the only row here likely to
become load-bearing is **`wasm32-emscripten`** — and specifically §5.7, because a missing `exceptions` switch fails at
**run time**, so a package that throws should state `requires_abi` and be refused early rather than aborting in a
browser. Everything else is know-it-exists: the `mcpp::action` mechanics of §3.5 are the same primitives any
`build.mcpp` uses, and §3.3's refusal is what to read when a build reports *"mcpp has no role for the extension"*.

## 9. `[unverified]` in this page

Everything above is cited to a doc line, a source line, an example file, the release binary's `--help`, or a GitHub
API read on 2026-09-16, **except**:

1. **No command on this page was executed against a real device, toolkit, emulator, phone or board.** Every measured
   transcript, size and "runs on this machine" claim reproduces what upstream's own doc or example README states it
   measured, at the date that document gives. Nothing was re-measured here, and no `mcpp build` of any example was
   run at all.
2. **The `rules-slang` platform row.** `docs/42`'s platform table names five lanes and omits `rules-slang`, so its
   Linux / macOS / Windows cells are unknown rather than "no" (§2.9).
3. **`mcpp:plugins` internals.** Every claim about `mcpp.rules.*` / `mcpp.tools.island` option names, payload version
   floors and feature names comes from the mcpp repository's docs and examples, **not** from the
   `mcpp-community/mcpp-plugins` repository, which was not read. The `0.5.2` version and the feature spellings are
   what the examples on `main @ 2fc7b5b0` declare.
4. **Which runner spelling is preferred at this baseline** — `mcpp::runner("<program name>")` per `docs/41`, or the
   absolute path from `xpkg_dir` per `docs/40`'s worked BSP. Both appear in current docs (§6.7).
5. **Whether `openarch`'s existence as a published repository supersedes the D-track ordering.** §7.2 reports the
   design record and the repository listing as two observations; no upstream reconciliation was found.
6. **`mcpp why runners` output shape.** The topic is documented [docs/41-devices.md:32] but `mcpp why --help` lists no
   topics, and the command was not run.
