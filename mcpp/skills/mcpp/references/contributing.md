# Contributing to mcpp itself

## 0. Version stamps and evidence baseline

- Evidence baseline: mcpp source repo `main @ 2fc7b5b0` (version `2026.9.15.2`), read-only recon, **date 2026-09-16**; the
  release-gate, PyPI and self-hosting notes in §8 were added against `main @ b30e70c4` (`2026.9.21.3`) on 2026-09-23. The commit
  style sample in §4.2 and the CI surface in §6 were **not** re-sampled for this refresh.
- Evidence markers: `[docs/xx:line]` = mcpp official English docs; `[src/xx:line]` / `[modules/xx:line]` /
  `[.github/xx:line]` = mcpp source and CI; `[field-tested <date>]` = measured directly, not read from a doc.
- Covers **filing issues / PRs against mcpp itself**. Submitting a package to **mcpp-index** is in `packaging.md`;
  day-to-day mcpp usage is in `../SKILL.md`.

---

## 1. Read first: where the bundled skills and the official docs are already stale

The mcpp repo ships `.agents/skills/mcpp-contributing/` and `mcpp-release/`, and copies of them circulate in other
projects. **The copies lag upstream, and the upstream originals are themselves partly wrong.** Verified item by item:

| Source | Claim | Reality (checked 2026-08-31) |
|---|---|---|
| `mcpp-contributing` copy, project-structure section | `src/platform/`, `src/manifest/` | **Neither exists**; moved to `modules/platform/`, `modules/manifest/`. `src/` has **14** subdirectories left, `modules/` has 9 standalone packages |
| Upstream `mcpp-contributing` (newer) | Has a `modules/` section | Older copies **lack that section** and are simply stale |
| `mcpp-release` copy | `src/xlings.cppm::kXlingsVersion` | Real source is `src/xlings/xlings.cppm:92` (`kXlingsVersion = "2026.9.14.1"`) |
| Upstream `mcpp-release` | `src/platform/xlings/xlings.cppm` | **Also wrong**, that path does not exist either |
| `mcpp-contributing` copy §6 | "merge commits by default (full history preserved)" | **Backwards.** Of the last 120 commits sampled, **0 were merge commits**; 105 titles ended in `(#N)`, i.e. squash merge |
| `docs/90-build-from-source.md` | Source Layout lists `manifest/`, `version_req.cppm`, `dyndep.cppm`, `platform/`, `libs/` under `src/` | **All five are in `modules/`** |
| `docs/90-build-from-source.md` | "commit titles in English imperative form" | Does not match the repo: a large minority of titles are in Chinese, and the English ones are generally **declarative** (`the answer was already resolved, and nothing consulted it`), not imperative |
| `docs/92-release.md` checklist | "version bumped in mcpp.toml + **fingerprint.cppm**" | Contradicts the §1 table in the same document. Real source is `modules/versioning/src/version.cppm:34`; the `fingerprint.cppm` line is only a `= mcpp::MCPP_VERSION` forward, editing it has no effect. The guard script checks `version.cppm` [.github/tools/check_version_pins.sh:103,109] |
| `mcpp-contributing` copy §1 | Three `gh issue create --body` templates | mcpp has **no issue/PR templates and no CONTRIBUTING.md under `.github/`** (`ls -R .github/` shows only `actions/`, `tools/`, `workflows/`). Those templates were invented by the skill, not an upstream convention |

WARNING: the four bundled skills are still `mcpp-contributing` / `mcpp-docs-style` / `mcpp-release` / `mcpp-usage`, so those copies are still
in circulation. The counts above (`120 commits`, the Chinese/English ratio) were measured on the earlier baseline and are **not** re-sampled
here - the *conclusions* hold, the numbers are indicative.

=> Treat those bundled skills as historical reference. This file is authoritative.

---

## 2. Repository shape and source-of-truth table

### 2.1 Version numbers: three persistent sites plus one derived value [docs/92-release.md]

| Site | Group | When it moves |
|---|---|---|
| `mcpp.toml` `[package].version` | **version being built** | when work on a new version starts |
| `modules/versioning/src/version.cppm` `MCPP_VERSION` | **version being built** | **same commit** as the line above |
| `.xlings.json` `[workspace].mcpp` | **bootstrap starting point** | separately, and only **after the new version is installable** |
| `ci-fresh-install.yml` `MCPP_PIN` | version under test | **do not touch — derived at runtime** [docs/92-release.md] |

Guard: `bash .github/tools/check_version_pins.sh` (**must be run with bash** — it uses process substitution, `sh`
reports `Syntax error: redirection unexpected`). It pins one more rule: **a literal `MCPP_PIN:` reappearing in
`ci-fresh-install.yml` is an error** [.github/tools/check_version_pins.sh:124-125].
There is also an xlings pin: source of truth `src/xlings/xlings.cppm:92` (`kXlingsVersion`, currently `2026.9.14.1`);
the same script scans all of `.github/` to keep it consistent [check_version_pins.sh:41-46].

### 2.2 Directory layout (checked 2026-09-16)

```
modules/          # 9 standalone packages, each with its own mcpp.toml, referenced by path
  buildmcpp/  dyndep/  libs/  log/  manifest/  platform/
  source-kind/  toolchain-model/  versioning/
src/              # 14 subdirectories; skeleton not yet split out
  bmi_cache/  build/  cli/  fallback/  fetcher/  freestanding/  modgraph/
  pack/  pm/  publish/  runtime/  scaffold/  toolchain/  xlings/
tests/unit/       # C++ unit/integration tests; `mcpp test` discovers them
tests/e2e/        # shell end-to-end scripts; run_all.sh is the CI entry point
docs/             # usage docs, renumbered into bands (docs/zh/ is the Chinese mirror)
docs/specs/       # specifications: package-identity (SPEC-001), target-side (SPEC-002),
                  # exit-codes (SPEC-003), manifest-semantics (SPEC-004), build-database (SPEC-005)
.agents/docs/     # design docs, named <YYYY-MM-DD>-<topic>.md
.agents/skills/   # mcpp-contributing / mcpp-docs-style / mcpp-release / mcpp-usage
```

**The direction is to shrink `src/`**: subsystems that can stand alone move into `modules/`, and the unit of movement
is **a subsystem, not a file** (wording from the newer upstream skill). WARNING: the Source Layout section of
`docs/90-build-from-source.md` still describes the pre-migration tree; do not copy it.

WARNING: **`docs/` was renumbered into bands and `docs/spec/` was renamed `docs/specs/`.** Any citation of the form
`docs/05-mcpp-toml.md` is a dead link, and some resolve to a different real document (`docs/11` was machine output and
is now publishing-a-library). The mapping is in `version-notes.md` §1. When changing docs, remember rule 3 of the style
gate: **`docs/X.md` and `docs/zh/X.md` must have the same heading structure**, so both change in the same commit.

The division of labour between the three doc trees is explicit [docs/specs/README.md]: `docs/*.md` usage /
`docs/specs/*.md` specification (semantics + constraints + **implementation-status markers**) / `.agents/docs/*.md`
the design of one particular change. Specification documents **must** carry a metadata table and a change record at
the end. Two of the newer specs are the ones a contributor is most likely to need: SPEC-003 (exit codes) and SPEC-004
(mcpp.toml semantics — the conditional-section shape, the resolution axes, naming).

---

## 3. Filing an issue

### 3.1 Official requirements [docs/90-build-from-source.md]

Three things, all of them in full: the **complete** output of `mcpp self env`; the **complete** output of the failing
command (`MCPP_LOG_LEVEL=debug` for more detail); OS / distribution / glibc version (`ldd --version`).
There is no issue template, so the structure is yours to choose. **Do not treat the three invented templates in the
bundled skill as a convention.**

### 3.2 An issue that demonstrably worked: `mcpp-community/mcpp#529`

`#529 mcpp test re-does dependency-closure planning on every invocation — 15s to 2.5min of silent work before
anything compiles` (filed 2026-08-29, **still OPEN**). What it got was not a comment but a **CHANGELOG entry and a
fix** [CHANGELOG.md, the `2026.8.30.2` section, which starts at :2831 - do not use a fixed line offset in this file: recent releases
live as `###` subsections under `[Unreleased]` (which opens at :6), so every number below it shifts on each release]. Reusable
technique:

1. **The title is the quantified symptom**, not a guessed cause: `15s to 2.5min of silent work before anything
   compiles` lets a reader decide without opening the body.
2. **Give the independent variable, not just numbers.** The report said cost tracks the total module-interface count
   of the dependency closure, with a counterexample: a member with only 8 cache units still took 154s, because a path
   dependency pulled in a much larger package. Upstream used that to locate a **different** mechanism (the memo of
   two post-link ELF passes being overwritten by `resolution.json` on every run). The attribution was wrong but
   **the independent variable was right**, so the report still worked.
3. **Write down the exclusions.** "Not BMI invalidation — repeated invocations recompile nothing", plus the criterion
   (one run writes 5 json files and 1 ninja file, zero `.pcm`/`.o`). Exclusions save the maintainer a dead end.
4. **Separate correlation from causation.** For a second symptom in the same batch the report said only "correlation
   stated, no causal evidence". Upstream later disproved that causal guess; since nothing had been asserted, nothing
   had to be retracted. [field-tested 2026-08-29/30]
5. WARNING: **fixed is not closed.** #529 is still OPEN, and upstream explicitly did **not** claim to have closed
   every gap observed. Check before citing upstream state (`gh issue view 529 -R mcpp-community/mcpp`).

### 3.3 When to open an issue before writing code [docs/90-build-from-source.md]

**Changes to the CLI or to the `mcpp.toml` schema must be aligned in an issue first.** Everything else is judgement.
mcpp describes itself as early-iteration with interfaces that may change, so discussing a large change first is cheap.

---

## 4. Branches and commit messages

### 4.1 Branches

Branch from the latest `main`, named `<type>/<short-description>`, type one of `feat|fix|refactor|test|docs|chore|ci`.
**Do not push to main directly.**

### 4.2 Commit titles: the real style (full sample of the last 120 commits, 2026-08-31)

| Dimension | Measured |
|---|---|
| Conventional prefix | 108/120. Distribution: `docs:` 33 / `fix:` 30 / `feat:` 27 / `chore:` 8 / `ci:` 5 / `test:` 3 / `release:` 2 |
| With scope `type(scope):` | 69/120. Frequent scopes: `docs(plan)` 14, `feat(freestanding)` 5, `fix(toolchain)` 4, `test(e2e)` 3 |
| No prefix | 12/120, **all of them release commits**, shaped like `2026.8.26.2 — the answer was already resolved, and nothing consulted it (#512)` |
| Contains Chinese | 54/120 (45%) |
| Ends with `(#N)` | 105/120, the default shape of a squash merge |
| Title length | min 18 / median 69 / p90 91 / max 121 — **clearly not following the 50-72 convention** |

**Style rule: the title is a declarative sentence saying what is true after the change, lowercase, not an
imperative.** Three examples; the first two are written in Chinese upstream and are given here in translation, the
third is verbatim:

```
fix: six sites of "the answer is already recorded and the deciding code does not read it" + system toolchains explicitly refused (#538)
feat(build.mcpp): rule-package specification, a portable check role, and the split from mcpp's own modules/ subsystem (#525)
fix(build): a package's generated inputs come before its compiles; an empty link is refused (#536)
```

All three state a **conclusion** ("X is now refused" / "X comes before Y"), not an action ("add" / "change").
Chinese and English are both accepted; **do not mix them within one title**. WARNING: `docs/90-build-from-source.md` says "English
imperative form", which does not match the repository (see the §1 table). Follow the actual repository style; an
English declarative sentence is the safe choice.

### 4.3 Pull requests

- Title in English; body may be English or Chinese. Link the issue (`Closes #N`). Include a test plan. One PR does
  one thing.
- **Always read `git diff --stat` before publishing**: `git add -A` sweeps in `compile_commands.json`, `mcpp.lock`,
  and `target/`. Field-tested on `mcpplibs/tinyhttps#12`, where a 2314-line `compile_commands.json` landed in the PR
  and had to be removed with amend plus force-with-lease.
- **Always re-read the published body online after posting.** On that same PR a "manually verified" sentence whose
  replacement had not taken effect went out, and was later corrected with `gh pr edit`. [field-tested 2026-08-29]

---

## 5. Local bootstrap build and tests

mcpp is **self-hosting**: an existing mcpp builds mcpp [docs/90-build-from-source.md].

```bash
mcpp build              # -> ./target/<triple>/<fp>/bin/mcpp
mcpp run -- --version   # run what you just built
mcpp test               # build and run tests/**/*.cpp (includes tests/unit)
```

- WARNING: **`mcpp test` does not run `tests/e2e/`** [docs/90-build-from-source.md]; run those separately against the
  new binary (on Windows the path means `mcpp.exe`):
  `MCPP=<absolute path to the binary you just built> bash tests/e2e/02_new_build_run.sh`
- WARNING: **`--profile` defaults to dev** (see `../SKILL.md` §1.1). To compare against a release artifact, pass
  `--profile release` explicitly; mcpp's own `mcpp.toml:10-14` pins `default-profile = "release"` and notes that
  otherwise the published binary would be built at -O0.
- Fully static artifact, the path `release.yml` takes: `mcpp build --target x86_64-linux-musl`
- **e2e is not guaranteed offline**: some scripts need a toolchain, the index, or a capability provider
  [docs/90-build-from-source.md]. Set `MCPP_HOME` the way CI does, mirror first, then run; do not let a cache hit or an
  empty workspace masquerade as coverage.
- **e2e numbering is a rough chronology, and the newest scripts are the best specification of a new behaviour.** When
  you need to know exactly what a recent change guarantees, the e2e script named in its CHANGELOG entry is usually
  more precise than the prose.

### 5.1 Known pitfalls when building the mcpp repo inside a sandbox

- WARNING: **the mcpp repo's own SubOS lock has been seen corrupted.** The workaround was to build the mcpp repo
  against a separate project-local home (`MCPP_HOME="$PWD/.mcpp"`) as a sandbox. [field-tested 2026-08-23]
- WARNING: **building an external project against a shared `MCPP_HOME` has side effects**: if that project pins no
  toolchain, mcpp installs gcc into the shared home and **makes it the default**. A project that pins its own
  toolchain does not take the default; another project will. [field-tested 2026-08-29]
- WARNING: **upgrading mcpp means a brand-new empty build directory** (`MCPP_VERSION` is input 7 of the 11
  whole-project fingerprint inputs [modules/toolchain-model/src/fingerprint.cppm:125]). Pin the version for any
  timing comparison.
- WARNING: **staleness is decided purely by mtime**: rolling a source tree back with `tar` / `cp -p` produces a false
  green. The criterion is whether the output contains `Compiling`. See `../SKILL.md` §1.7.

---

## 6. CI surface

There are **17** workflow files [`.github/workflows/`, listed 2026-09-16]:

| Workflow | Trigger | Content |
|---|---|---|
| `ci-linux` | push/PR to main + dispatch | **seven gate scripts** + bootstrap build + `mcpp test` + **per-member `mcpp test -p`** + gcc cold bootstrap + musl/llvm toolchains + "mcpp builds and runs xlings" integration |
| `ci-linux-e2e` | same | sharded e2e |
| `ci-macos` / `ci-macos-e2e` | same | macOS ARM64 |
| **`ci-macos-ios`** | same | the iOS rows (SDK located, not installed) |
| `ci-windows` / `ci-windows-e2e` | same | Windows x86_64 |
| `ci-windows-msvc-xlings` | same | MSVC + xlings path |
| `ci-target-matrix` | PR (any base) + push main | target matrix |
| `cross-build-test` | push/PR to main | cross build + MinGW/Wine checks |
| `openkal-cross` | **PR (any base)** + dispatch | openkal cross path |
| `ci-aarch64-fresh-install` | **path-filtered** PR + push main + weekly cron | native Linux ARM64 |
| `ci-fresh-install` | **`workflow_run` hook** (after release) + cron + dispatch | installs the latest published version and verifies it |
| `release` | **tag `v*` push** or dispatch | see §8 |
| `aur-publish` / `homebrew-publish` | `workflow_run` + cron/dispatch | downstream distribution |
| `bootstrap-macos` | **dispatch only** (dormant) | — |

**Trust the required checks on the actual PR**: `gh pr checks <n>`. Do not guess from names — the `pull_request:`
blocks of `ci-target-matrix` and `openkal-cross` declare no `branches`, so they run for **any** PR.

### 6.1 The seven gate scripts in `ci-linux` (what code changes hit most)

[.github/workflows/ci-linux.yml:56,63,78,96,102,109,121]

| Script | Enforces |
|---|---|
| `check_version_pins.sh` | the table in §2.1, mechanized |
| `check_modules_wiring.sh` | consistent wiring of each package under `modules/` |
| `check_narrow_conversions.sh` | "do not narrow a walk-derived path directly" |
| `check_matrix_reasons.sh` | the target-matrix rows carry stated reasons |
| `check_docs_style.sh` | doc style + **structural parity between Chinese and English headings** |
| `check_docs_structure.sh` | doc structure |
| `check_target_tiers.py` | the target tier table (`verified` / `preview` / `planned`) |

WARNING (stale-claim retired): older copies of this file say **four** scripts and give the 2026-08 line numbers. Running
only those four leaves CI red.

`check_docs_style.sh` checks **four** decidable things [.github/tools/check_docs_style.sh:4-11]: headings are not
questions or colloquial fragments; **reference documents do not use second person** (tutorials excepted, allowlist
hardcoded as `01-getting-started.md 03-examples.md 90-build-from-source.md` [:30]); `docs/X.md` and `docs/zh/X.md`
have the **same heading structure**; and **a table's header cells follow the same register as a heading** — rule 4
exists because rule 1 only read lines beginning with `#`, and a column header is a heading by every property that
matters. What it **deliberately does not check** is in its own comment: "whether a claim's strength matches its
evidence — the most important rule in the skill and it needs a reader" [:19-20].
=> Changing `docs/` requires changing `docs/zh/` in the same commit, or CI goes red. And the tutorial allowlist uses
the **new** file names; an older copy of this note lists three files that no longer exist.

---

## 7. Writing a CHANGELOG entry

`CHANGELOG.md` follows Keep a Changelog 1.1.0, **with Chinese body text**.

- Version heading: `## [2026.8.30.2] — 2026-08-30` (bracketed version + em dash + ISO date). Version numbers are
  `YYYY.M.D.N`, where `N` is the ordinal within that day.
- WARNING: **the newest releases live inside `## [Unreleased]` as per-version `### …(2026.9.15.2)` subsections**, not
  under their own `##` heading. `grep '^## '` therefore under-reports recent versions by a wide margin.
- Subsection headings are **written in Chinese**, except `### CI`. The recurring ones by meaning are Fixed / Added /
  Improved / Changed / Tests, which cover almost every case. **Do not invent new ones — copy the exact heading string
  from an existing entry.**
- Entry shape: **one bold sentence saying what was wrong, then the mechanism**, with the issue number. A typical
  opening, translated: "**mcpp test recomputes an unchanged answer on every invocation (#529).**" The original is
  in Chinese.
- If you have numbers, include a table. Large changes link at the top to the full analysis in
  `.agents/docs/<date>-<topic>.md`.

WARNING: **the CHANGELOG has blind spots, and so does the Releases page.** Capabilities have shipped with no entry at
all (`[hooks]` is the standing example), and **twelve of the releases between `2026.8.30.2` and `2026.9.15.2` publish
with no release notes whatsoever** — their content exists only in the merged pull request and in `CHANGELOG.md`.
=> To decide whether a capability is in a given version, read `git log`, the merged PR, and the source. Do not read the
Releases page, and do not treat a missing CHANGELOG entry as evidence of absence.

---

## 8. Release process (to the depth of "know the process")

The full maintainer-facing process is in [docs/92-release.md]. Key points:

- Trigger: push a `v*` tag, or `workflow_dispatch` with no input (the tag is derived from `mcpp.toml`).
- Pipeline: build on 4 platforms (linux x86_64 / linux aarch64 / macOS ARM64 / Windows x64) ->
  GitHub Release with `.sha256` sidecars -> **recompute every payload hash and publish an immutable
  `mcpp-release.json`** -> mirror to `xlings-res/mcpp` (GitHub and GitCode) -> open a version-bump PR against
  `openxlings/xim-pkgindex` -> a `workflow_run` hook starts `ci-fresh-install`.
- **Two steps are not automated**: (1) merging the xim-pkgindex bump PR (before that merge the new version is
  **downloadable but not installable**); (2) moving the bootstrap pin in `.xlings.json`.
- **The only hard constraint on the bootstrap pin is direction**: it must never point at a version that is not yet in
  the index, or every CI job fails with `package 'mcpp@<unreleased>' not found`. It **need not move every release** —
  the index keeps all historical versions.
- **Index propagation is not instantaneous**: xim-pkgindex reaches clients through a CDN artifact; measured about 5
  minutes, documented worst case about 40 minutes. **A clean room still reporting the old `latest` is not a failure,
  it has not caught up yet.**
- WARNING: **the doc carries two errata of its own**, both the same misdiagnosis: "the index deleted the old version"
  — neither time was that true; the real causes were a stale local index copy and workspace-scoped resolution. The
  original wording is worth remembering: **"read the index before concluding that the index deleted it."**
- The checklist is at the end of `docs/92-release.md`, but §1 already showed that its `fingerprint.cppm` line is wrong.
- *Since 2026.9.18.2* the release workflow **fails when `CHANGELOG.md` has no `## [<version>]` heading** for the version being tagged
  (`6bb2ffd9`, #670): `v2026.9.18.1` shipped with the release body "(no CHANGELOG entry found for 2026.9.18.1)" and that placeholder
  is now an error. => A version bump PR must add its `## [x.y.z.w]` section (not a `###` under someone else's heading) or the
  release job stops after building.
- Upstream's own post-release lesson from the xlings side applies here too: a verification script that reads **git main** can be
  green while the **published index pointer** still resolves `latest` to the old version. After a release, resolve `latest` the way
  a client does before declaring it installable.
- Since 2026.9.21.3 (`b30e70c4`, after the tag) `.github/workflows/pypi-publish.yml` also publishes the release binary as the PyPI
  distribution `mcpp-bin` (wheels built by `scripts/pypi/build_wheels.py`); the PyPI name `mcpp` belongs to an unrelated project.
- Self-hosting caveats open at 2026-09-23: a Clang-built mcpp SIGSEGVs in ELF runtime inspection (mcpp#666) and a GCC self-host can
  ICE when a new consumer imports `mcpp.targetside` under a parallel build (mcpp#667). The self-host pins are `gcc@16.1.0`
  (default), `llvm@22.1.8` (macOS), `llvm@20.1.7` (Windows) in mcpp's own `[toolchain]`. If a local self-build crashes in either
  of those two shapes, check those issues before blaming your change.
- A release also moves the **bundled xlings pin** (`kXlingsVersion`; `2026.9.14.1` at the 2026-09-16 baseline, **`2026.9.16.1`** at
  `2026.9.21.3` [src/xlings/xlings.cppm:99]) when it needs to.
  That pin is load-bearing beyond version hygiene: before xlings `2026.9.14.1`, a package with no `install()` received
  the entire download directory rather than its own archive, so a long-lived registry can be carrying gigabytes of
  other packages' downloads. `xlings self doctor` reports such directories read-only and `--fix` reinstalls them.

---

## 9. Norms for outward communication (issues / PRs / comments)

The following applies to **everything you publish**.

### 9.1 Style

**Plain English prose. No emoji. Almost no bold.** Use a table only when the data is genuinely two-dimensional; do
not write a slide skeleton of "three conclusion lines plus N tables". Write self-corrections as they are — they raise
credibility rather than lower it. [field-tested repeatedly]

### 9.2 Do not mention internal names

**Do not include your project's package names, file paths, test names, internal document names, or ledger ids.** If
the project is not open source, the reader cannot see them and there is no reason to disclose its structure.
**What you may paste verbatim**: the code fragments needed to reproduce (without paths they disclose no structure),
version numbers, syscall numbers, register/stack dumps, third-party library names. Field-tested: two of four
published comments leaked such names and had to be rewritten with
`gh api -X PATCH repos/<o>/<r>/issues/comments/<id> -f body=…`.

### 9.3 Adversarial review before publishing (a hard step)

**Before publishing, run a review whose orientation is set to "refute".** On a fourth-round musl report this caught
**30 items that did not pass and 13 that had to change**, two of them at the "upstream sees it on first read" level.
**The previous report skipped this step and went out wrong.** The two most expensive lessons:

- **Enumerative claims require exhaustive sampling.** "Only X is left" / "the only Y" from a single sample point is a
  **lower bound, not a list**. A single trace of a single binary produced the claim "the only absent call left is
  fchmodat"; scanning all 108 binaries showed **four are still absent**.
- **Get the confession right too.** The review found the self-criticism of the previous report was **overstated** —
  that report had in fact said "correlation only, causation not established". **Admitting too much is as inaccurate
  as admitting too little.**

A related one: **"the signature is bit-identical" is not evidence that the fix failed, it is evidence that this is
the same binary.** A third-round musl report went out wrong on that, and upstream saw through it in one sentence.

### 9.4 Thread routing

**Route reply-shaped content by where the conversation is, not by which repository owns the code.** A reply was once
opened as a new issue while the maintainer had asked for that feedback in a thread on another repository. If you post
in the wrong place: move it, close the wrong one, leave a pointer, and apologize.

### 9.5 Check upstream state before citing it

**Do not copy PR/issue/upstream-version state out of a handoff document; check it once.**
`gh pr view <n> -R <owner>/<repo>` / `gh issue view <n> -R <owner>/<repo>`. WARNING: **the GitHub Releases page
lags.** To determine an upstream package's current version, read `[package].version` in the repository's
`mcpp.toml`, not the Releases page.

### 9.6 Who presses send

**Recommended policy: find and report upstream issue/PR/new-package opportunities on your own initiative, but wait
for your user to approve before publishing anything.**
