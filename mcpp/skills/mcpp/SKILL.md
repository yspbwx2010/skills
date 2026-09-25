---
name: mcpp
description: Use for any hands-on work with the mcpp C++23 build tool - building, testing, gating, mcpp.toml configuration, workspaces, toolchains, cross-compilation, caching, build.mcpp/hooks, machine-readable output and CI wiring, or diagnosing a build that misbehaves. Also covers contributing to mcpp itself (issues, branch and commit conventions, self-hosted build, CI surface, release flow, upstream communication rules) and packaging a library into mcpp-index (descriptor .lua fields, features, GLOBAL+CN mirrors, lint rules, validate/publish CI, local verification, namespace conventions).
license: MIT
metadata:
  mcpp-version: "2026.9.24.1"
---

# Complete mcpp usage guide

## 0. Version stamp and scope

- **Evidence baseline**: mcpp source `main @ b4824697` (version `2026.9.24.1`, tag `v2026.9.24.1`, read-only), dated 2026-09-24.
  What `2026.9.24.1` introduced was verified against source and docs only - the diff `b30e70c4..b4824697`, the English docs and
  `docs/specs/toolchain-management.md` at that commit; no release binary was downloaded, built or run for this pass. Citations
  written `path:line @ b4824697` are from that tree. The layer below it is `main @ b30e70c4` (`2026.9.21.3`, 2026-09-23, also
  source and docs only), which covers the twelve releases `2026.9.16.1` .. `2026.9.21.3`; facts carried over from `main @ 2fc7b5b0`
  (`2026.9.15.2`, which *was* cross-checked on its release binary) keep that baseline's line citations unless a citation below says
  it was re-read; source line numbers drift between releases, so re-grep before quoting one.
- **Current, not comparative.** Statements describe `2026.9.24.1`. Where behaviour genuinely changed, the change is recorded once as
  `changed in <version>: …` in the per-version history in `references/version-notes.md`; that file is the entry point for "this is new,
  how do I use it".
- **Citation discipline**: the Chinese pages under `docs/` lag the English ones, so this skill cites the English docs only. The
  specs under `docs/specs/` (SPEC-001 .. SPEC-006) exist once, written in Chinese, and are cited as they are.
  WARNING: the whole `docs/` tree was renumbered into bands (`0x` basics, `1x` release, `2x` toolchains and targets, `3x` extension,
  `4x` devices, `5x` machine contract, `9x` mcpp itself) and `docs/spec/` was renamed `docs/specs/`. Pre-**2026.9.9.1** citations of the
  form `docs/05-mcpp-toml.md` are dead links - the renumbering landed in one commit (`9a71c9a6`, 2026-09-08), first released in
  `2026.9.9.1`, so **every** citation written against a tree older than that - 2026.9.4 through 2026.9.8.1 included - carries the old flat
  numbering and must be mapped before use. (Those paths were correct in the tree the citing document was written against; they are dead in
  today's tree, and a stale `docs/11-…` is worse than a 404 because that number now names a different page.) The `docs/spec/` ->
  `docs/specs/` half landed earlier, in `2026.9.6.4` (`91ab128e`). The mapping is in `references/version-notes.md` §1.
- **Evidence markers**: `[docs/xx:line]` = official English docs; `[src/xx:line]` / `[modules/xx:line]` = mcpp source; `[field-tested
  <date>]` = observed in a real project. Items marked `[unverified]` keep that marker and are not facts.

### 0.1 What changed since `2026.9.15.2`

If you know the older engine, read `references/whats-new.md` first.

## 1. Dangerous-misconception corrections (read this section first)

Places where doing the common-sense thing, or following `--help`, gets it wrong.

### 1.1 `build` / `test` / `run` default to **dev**; only `pack` falls back to release
Truth chain: `--profile`/`--release`/`--dev` > `[build] default-profile` > global **`dev`**; the implementation is
`resolve_profile_name(..., fallback="dev")` [src/build/prepare.cppm:1014,1096-1099], and the only caller passing `"release"` is
`mcpp pack` (`--profile` > `[build] default-profile` > `release`). `build` / `test` / `run` / `emit build-database` all land on dev.
WARNING: the `--release` / `--dev` shorthands are declared on **`build`, `run`, `pack` and `emit build-database`**, and **not on
`test`** [src/cli.cppm:381,453,629,690, re-read at 2026.9.21.3]. `mcpp test --release` is `error: unknown option: --release`, **exit 2**;
in a gate leg that reads as a broken gate, not as a wrong flag. `test` takes `--profile release` and nothing else.
*changed in 2026.9.16.1*: `pack` gained the two shorthands (before that, `mcpp pack --release` was the same exit-2 refusal), and
`build`, `run`, `test` and `pack` now share one profile decision in which **`--profile` wins over a shorthand**. On `run` it used to be
the reverse, so `mcpp run --release --profile dev` changed meaning.
=> **Write `--profile release` explicitly wherever the profile matters**, or pin `[build] default-profile = "release"` in the manifest
(mcpp does exactly that, noting that otherwise the released binary would be -O0 [mcpp.toml:10-14]). Performance, size and timing numbers
are only comparable when the profile is stated.
WARNING (stale-claim retired): older write-ups say `mcpp build --help` prints "release (default)" and is lying. The help text was wrong
from before this skill's first baseline and has since been corrected; today it reads `dev (default) | release | dist | <[profile.*] name>`
on `build`, `test` and `emit build-database` [verified on mcpp 2026.9.15.2]. **Do not repeat the "the help text is wrong" correction.**
`dist` is a built-in profile (`opt 3` + `strip`) alongside `dev` and `release`.

### 1.2 `MCPP_INDEX_MIRROR` does not exist in mcpp
Zero hits across the repo, and not in the getenv set. Setting it is a **no-op** (it is passed through to child processes and may be read
by xlings, but mcpp definitively does not read it). Only three real approximations exist: `mcpp self config --mirror CN|GLOBAL` (**only
effective when seeding `.xlings.json` the first time** [src/config.cppm:271-277]), `MCPP_INDEX_FLOOR=ignore`, and the
compile-time-constant artifact base [src/config.cppm:59].

### 1.3 `mcpp.lock` records a resolution; `--locked` is what makes it bite
The lock's own header still says "**It does not yet pin future builds: index dependencies are re-resolved from their constraints each
time.**" [src/pm/lock_io.cppm:145-151], and the `hash` field is **not a content checksum** - it is `fnv1a:` plus FNV-1a over
`"{ns}:{name}@{version}"` (`mcpp::pm::index_package_digest` in `src/pm/lock_io.cppm`). The file format is unchanged (`version = 2`,
dev-dependencies excluded).
*changed in 2026.9.20.1* (mcpp#675/#676): before it, the digest was `std::hash<std::string>`, which is FNV-1a only under MSVC and
MurmurHash under libstdc++/libc++, so the same dependency hashed differently on Windows and Linux while the `fnv1a:` label claimed
otherwise. => **After upgrading, the first build on a Linux or macOS host rewrites every `hash` line of `mcpp.lock`** - expect one
diff and commit it; `--locked` compares versions only [src/build/prepare.cppm:14648-14679, re-read], so it does not fail on that diff.
The git cache directory key under `$MCPP_HOME/git/` moved to the same hash, so each `git` dependency is cloned once more.
What changed is that the lock became an **assertion**: the global `--locked` (aliases `--frozen`, `MCPP_LOCKED=1`) fails the command when
the resolution that just happened differs from the recorded one, naming the package and both versions [src/cli.cppm:97,184;
src/build/prepare.cppm:13205]. It deliberately **refuses the fast path** [src/build/execute.cppm:1379,1503] - before that gate, a
deliberately corrupted lock passed `mcpp build --locked` and printed `Finished`.
=> **Put `--locked` on gate legs** and nothing else: every run pays a full resolution. It does not enter the fingerprint, so it opens no
new `target/<triple>/<fp>/` directory. It covers index and git edges only; `path` edges are not in the lock, so in a multi-member
workspace the assertion says nothing about sibling members - read `mcpp why deps` for those.

### 1.4 `mcpp why` is not read-only, and still exits 0 when it refuses
The static side-effect table lists the fullest set for `why toolchain`: `init-mcpp-home, read-project, network, write-global-cache,
exec-build-script` [src/cli.cppm:1068-1070] - its answer comes from `prepare_build`, so it resolves the dependency graph, may download
packages, installs toolchains, and **runs dependencies' build.mcpp**. And `status: "refused"` still **exits 0**
[docs/50-machine-output.md:322]. => CI must branch on `data.status`, never on `$?`; treat it as having side effects when gating. Note:
`--format json` is valid only for `why toolchain`; the other topics refuse explicitly and exit 2 [src/cli/cmd_self.cppm:88-102].
Topics are `toolchain | runtime | deps | runners` (default all). `mcpp why deps` prints the resolved dependency graph recorded in
`resolution.json` - who requested each package, under which key and from which table, and each library's link form with its reason.
**`mcpp emit build-database` declares the same effects as `build --configure-only` minus `write-project` - which makes its entry
byte-identical to `why toolchain`'s** [src/cli.cppm:1075-1077; the source's own comparison is at :1071-1074]: it is the read-only way to
get a compile database, but it still runs build programs and may reach the network.
WARNING: it also widened the **exit-code** space. With no loadable `mcpp.toml` it exits **1** (an enveloped failure with no `data`), where
`build` / `test --list` / `why deps` / `clean` / `emit sbom` / `emit xpkg` all exit **2** for the same condition. Only an invalid `--spec`
or `--format` exits 2 there. A gate reading that `1` off the SPEC-003 table sees "a build failure worth retrying" when the real condition
is "this directory is not an mcpp package" [verified on 2026.9.15.2].

### 1.5 `[xlings.workspace]` provisions tools into `$MCPP_HOME` - gated, but on by default
A declared tool is **provisioned on the build that needs it**, landing in `$MCPP_HOME/registry/data/xpkgs/<ns>-x-<name>/<ver>/`, and
provisioning now spans the **whole dependency graph**, not just the root project. The escape hatches exist:
`--offline` / `MCPP_OFFLINE=1` / `MCPP_NO_AUTO_INSTALL=1` all refuse the install and name what it would have installed
[src/build/prepare.cppm:1541-1571] - **unless** the project carries a pre-2026.9.1.1 provisioning stamp for the same dependency list, in
which case the build proceeds with only a verbose note and no refusal [src/build/prepare.cppm:1558-1575]. So a gate leg that leans on the
refusal firing can pass silently on such a project. Nothing is installed silently any more, but nothing asks either.
=> **Still use a project-owned `MCPP_HOME` prefix** (`$MCPP_HOME` has the highest priority [src/home.cppm:78]), e.g.
`MCPP_HOME="$PWD/.mcpp"` - the reason is now disk ownership, not the absence of a switch.
- **Network work is bounded and reported (2026.9.16.1)**: one index refresh may take `[index] refresh_timeout` seconds of the home's
  `config.toml` (default **120**); past it the refresh is stopped, a warning names the setting and the build continues on the local
  index. An install through xlings is killed after **300 s with no output at all** (heartbeats count as output;
  `kInterfaceIdleTimeout`, src/xlings/xlings.cppm:530), and xlings children run
  in mcpp's process group, so killing mcpp kills them. An offline run that needs a download fails with the diagnostic
  `MCPP_OFFLINE_DOWNLOAD_REQUIRED` / refusal `offline-download-required`, naming the first toolchain, package, git revision or index it
  would have fetched - "one run without `--offline` fixes it", not a project defect.
- *changed in 2026.9.16.1*: `[index] auto_refresh = false` governs **every** implicit refresh - on a dependency miss, before installing
  a package the local index lacks, before a retry, and the first sync of a project's custom index (that build now stops and names
  `mcpp index update`). Before, the pre-install, pre-retry and first-sync refreshes ignored the setting.
- `[xlings.workspace]` is **the one table**. `[xlings] deps` still works but warns (an error under `--strict`), and **`[xlings.envs]` is a
  hard error** - a manifest that still carries it fails to load [modules/manifest/src/toml.cppm:2153-2156].
- `when = "build" | "run" | "dev"` scopes an entry: omitted and `build` are installed by every verb that builds; `run` only by
  `mcpp run` / `mcpp test`; `dev` only when the declaring package is the root, and it does not propagate. A scoped entry must still spell
  `version` (`version = ""` means "present, any version").
  => On a throttled machine, moving run-only tools to `when = "run"` is the cheapest way to shrink a build-only gate leg.
- `[feature-xlings.<f>]` gates a tool on a feature; `[target.<sel>.xlings.workspace]` resolves against the **target** rather than the
  host. Tools that execute on the build machine belong on the host axis; payloads the produced code compiles or links against belong on
  the target axis. On a native build the two name the same platform, so a project that states target facts on the host axis is right by
  accident and stops being right the first time it cross-compiles.
WARNING: do not confuse provisioning with **SubOS** ("reading an environment, never creating one"): a named SubOS that does not exist is
still a hard error, and mcpp does not create it.

### 1.6 The fast path replays a previous build, so every axis it cannot see is a false green
`target/.build_cache` is an 8-entry LRU record; the fast path replays the last build whose **named set** matches: target triple, profile,
cache mode, **feature set**, and **toolchain request** (`--toolchain` / `MCPP_TOOLCHAIN` / the machine default)
[src/build/execute.cppm:100-127,353-369]. `--offline`, `--locked` and `--jobs` deliberately do not participate.
WARNING: that named set governs **which recorded entry may be replayed**, not whether the fast path is attempted at all. Passing any of
those axes **on the command line** (`--profile`, `--features`, `--target`, `--cache`, …) makes the guard in §4 bypass the fast path
outright, so `mcpp build --profile release` never replays a recorded release build - it re-plans every time.
Everything on that list was at some point *not* on it, and each omission produced the same symptom - `Finished dev in 0.00s` handing back
an artifact built on a different axis. The generalised rule is worth more than the individual fixes:
=> **Any axis that enters the fingerprint must also be visible to the fast path, or it is a silent wrong answer.** When a gate result
surprises you, the first question is which axis changed and whether the record could see it.
Two consequences that still hold today: `mcpp test`'s build **writes no record** (so its fingerprint directories look unrecorded to
`mcpp clean --stale`), and entries written by an older engine are rejected once and rewritten - a single extra full build after an upgrade
is expected, not a regression.

### 1.7 Staleness is pure mtime, so `tar` / `cp -p` rollbacks give false green
All three layers are mtime-based with no content hash: mcpp's own fast path [src/build/execute.cppm:1059,1142], ninja's incrementality,
and `ArtifactStamp{exists,size,mtime}` [src/build/runtime_validation.cppm:33-38]. A tar rollback preserves both size and mtime, so **all
three layers are fooled**. => Roll back only with something that updates mtime (`sed -i`, an editor, `git checkout --`); after any
tar-like restore, **`touch` first, then build**. The criterion is **whether the output contains `Compiling`**; `Finished dev in 0.00s` is
the signature of a fast-path hit. [field-tested 2026-08-30]
Two exceptions, both real content hashes: inputs, env and globs declared by `build.mcpp` [src/build/build_program.cppm], and the host-tool
store, which keys a `git` tool by its resolved commit and a `path` tool by a stat imprint of its tree. WARNING: that imprint **includes
mtime**, so the tar/cp trap applies to host tools too - a restored older tree can re-hit the old cache entry.

### 1.8 MCPP_HOME is inferred from the binary's own location, and the home cannot be relocated
Resolution chain: `$MCPP_HOME` > **`<binary-dir>/..`** (self-contained layout; `target/` and `data/xpkgs/` ancestors are disqualified) >
`$HOME/.mcpp` [src/home.cppm:67-105]. => A binary copied elsewhere is, to several tests, **a different binary**. Relocating the home is a
problem because installed artifacts embed four kinds of absolute path (clang `bin/*.cfg`, the payload ELF's PT_INTERP/RUNPATH,
`.mcpp-fixup.json`, the std module cache identity) [src/toolchain/post_install.cppm; src/toolchain/stdmod.cppm].
**Correction**: mcpp does have an unnamed self-healing path - the fixup stamp compares content fingerprints and
`ensure_post_install_fixup` [src/toolchain/post_install.cppm:549] is called at every build seam that resolves a payload
[src/build/prepare.cppm:3361,3584,4155,4377], so the next build re-patches automatically. What actually blocks relocation is three other
things: (1) the **patchelf bootstrap cycle** - the fix needs the patchelf inside the payload, and if its own PT_INTERP is broken it takes
the `hasInterp=false` branch and **silently does not patch** [src/toolchain/post_install.cppm:109,132]; (2) the std BMI and every
dependency BMI are **fully rebuilt**; (3) **a payload inherited through a symlink is never fixed** (`escapes_containment`
[src/toolchain/post_install.cppm:52] skips it silently). (A bare `[:N]` is only safe when the immediately preceding citation in the same
sentence names the intended file; here the preceding one is `prepare.cppm`, so both are spelled out.)
=> Operational conclusion unchanged: **install fresh in place, never `mv`**. [field-tested: `ls` shows the binary, `exec` reports it does
not exist]
Upstream's own position is that the home is a rebuildable cache: when a home really must move, the sanctioned recovery is to drop the
registry and let the next build re-fetch the toolchain in the new location, not to patch in place.

## 2. Mental model

```
$MCPP_HOME/                      <- decided by $MCPP_HOME > <binary-dir>/.. > $HOME/.mcpp
|-- registry/                    <- this IS XLINGS_HOME (set per run by mcpp, never persisted)
|   |-- data/xpkgs/<ns>-x-<name>/<ver>/   <- toolchain payloads and provisioned tools land here
|   |-- subos/default/                    <- default SubOS (machine-wide, shared)
|   `-- .mcpp-index-overrides.json        <- what [index.repos.<name>] replaced, so removing it restores
|-- build-cache/v1/{pkg,std}/    <- cross-project dependency cache; v1 is the layout version
|-- cache/build-database/<key>/  <- where `mcpp emit build-database` plans; pure cache, safe to delete
|-- cache/tool/.build/<hash>/    <- scratch for host-tool sub-builds
|-- bmi/                         <- pre-v1 legacy (mcpp cache clean --legacy)
`-- config.toml

<project>/
|-- mcpp.toml, mcpp.lock
|-- .mcpp/.xlings.json                             <- project-side runtime declaration
|-- .mcpp/.xlings/subos/<name>/                    <- named SubOS (project-private, shares nothing)
`-- target/<triple>/<16-hex fingerprint>/          <- this project's build dir; inputs in §8
    `-- ../.build_cache                            <- 8-entry LRU fast-path record (§1.6)
```
WARNING: neither `cache/build-database/` nor `cache/tool/` is managed by `mcpp clean --stale` (which only touches
`target/<triple>/<fp>/`) or by `mcpp cache gc` (which owns `build-cache/v1`). Account for them separately when sizing a project-local home.

- **For a workspace member to be importable you must write it in two places**: `[workspace] members` (so `-p` and `mcpp test` can address
  it) **and** `[dependencies.<ns>] x = { path = "..." }` (so it can be imported). "Either one alone looks sufficient" is a pitfall mcpp
  calls out in its own manifest [mcpp.toml:80-82]. Make the key spell the identity the member's own `[package]` declares: a `path` or
  `git` dependency takes the identity from **its own manifest**, and a key that normalises to a different one warns once per declaring
  edge (and, when the member declares no namespace, two differently-namespaced keys over one directory are refused before scanning).
- **SubOS is the single answer to "what is this project built against"** - not a compiler path, not `XLINGS_ACTIVE_SUBOS`, not the shell
  [docs/23-the-project-environment.md]. Three isolation levels: declare nothing -> shared `subos/default`; `subos = "default"` -> the same
  directory, named explicitly; `subos = "<name>"` -> a project-private directory. **Read, never create**: a named SubOS that does not
  exist is a hard error. A dependency's own `[xlings] subos` is **never consulted and never propagates**; in a workspace build **the root
  owns the choice**.
- **Why an `env -u XLINGS_HOME -u XLINGS_BIN` prefix**: mcpp sets `XLINGS_HOME` itself on every run, pointing at `<MCPP_HOME>/registry`,
  and declares `XLINGS_SUBOS_LD_PATHS=0` for **every** child process to refuse the xlings linker wrapper's injection of
  `-rpath "$XLINGS_SUBOS_LIB"` - that variable refers to the **active shell's** SubOS, and inheriting it puts a second libc on the
  artifact's search path [src/cli.cppm; docs/91-toolchain-internals.md]. But a login shell's `XLINGS_BIN` still makes `xlings`/tools on
  PATH resolve to the global copy. **Honest annotation**: no explicit read of `XLINGS_BIN` was found on the mcpp side (not in the getenv
  set), so that half of the prefix is **defensive discipline**, not an mcpp requirement.
  A third variable of the same family, `XLINGS_ACTIVE_SUBOS`, is now stripped by the engine itself on every xlings invocation - a shell
  that ran `xlings subos use <name>` used to redirect mcpp's registry into a same-named other SubOS, leaving bootstrap tools and payloads
  in the wrong place and an empty pkg-config view. Keep the `env -u` prefix anyway; it guards the other two.
- **Which xlings binary a home gets** [src/fallback/xlings_binary.cppm]: `MCPP_VENDORED_XLINGS` > the xlings released beside this
  mcpp (`<prefix>/registry/bin/xlings` of the running binary's release layout) > `which xlings` on PATH. *changed in 2026.9.17.2*: the
  middle rung is new; before it, an mcpp installed as an xlings package (home `~/.mcpp`) fell through to whatever xlings was on PATH,
  kept it even when it was older than the pin, and only printed a note. The pin itself is `kXlingsVersion` =
  **`2026.9.16.1`** at this baseline [src/xlings/xlings.cppm:99] - newer xlings releases exist and are not what mcpp runs.
- **Building an external project under a shared `MCPP_HOME` has side effects**: if that project pins no toolchain, mcpp installs gcc into
  the shared home and makes it the default. A project pinning its own toolchain ignores that default, but watch for it. [field-tested
  2026-08-29]

## 3. Everyday commands

Full flag surface is in `references/commands.md`. This table covers semantics and traps only.

| Command | What you must know |
|---|---|
| `build` | Default profile is **dev** (1.1). `--configure-only` **is not read-only**: it may update build.mcpp, install dependencies/toolchains, write the lock and build-dir metadata; run it only in trusted workspaces. For a compile database without writing into the project, prefer `emit build-database` |
| `run [bin]` | The positional argument is a **binary name, not a triple**; triples go to `--target`. It now carries the same axes as `build` (`--features`/`--profile`/`--release`/`--dev`/`--toolchain`/`--accel`), plus `--runner <NAME>` / `--list-runners`, `--no-runner`, and `--format <name>` (run what a `pack --format` would produce; refused together with `--no-runner`). **Its exit code is the program's own**: 0-124 passed through verbatim, 125-127 = the spawn was attempted and refused (127 not found / 126 not executable / 125 other), 2 = mcpp refused before attempting anything [docs/50-machine-output.md:199-201] |
| `test [pattern]` | See §4; the most traps. Exit 2 now also means "built, never ran"; `--no-run` asks for "build only" and exits 0 |
| `clean` | Deletes the whole `target/`. **`--stale` is the one you want**: it removes only the `target/<triple>/<fingerprint>/` directories no recorded build considers current, reporting each one's size. `--dry-run` and `--older-than <DUR>` each imply `--stale`, so `mcpp clean --older-than 3d` cannot fall through to the full wipe. `--bmi-cache` additionally deletes all of `$MCPP_HOME/build-cache/v1` and is **mutually exclusive** with the stale mode |
| `add <pkg>` | A bare name **can only mean the `mcpplibs` namespace**; `gtest` must be written `compat.gtest`. WARNING: the transitional `(mcpplibs, x)` -> `(compat, x)` fallback is documented as "removal in `2026.9`" but is **still present** on 2026.9.24.1 [docs/specs/package-identity.md:184; src/pm/package_fetcher.cppm:726,764 @ b4824697] - treat it as deprecated, not gone |
| `remove` / `update [pkg]` | `update` only deletes the entry and tells you to run a build; **it does not write the lock itself** |
| `pack [target]` | **Two different "targets"**: the positional argument is a `[targets.*]` target name, `--target` is a triple (repeatable). Output is decided by the target's `kind`, not by a flag. Profile falls back to **release**, landing in a **different** `target/<triple>/<fp>/` than a bare build. Also takes `--toolchain`, `--features` (applies to **every** build pass of the pack), `--release`/`--dev` and `--message-format json` (one `mcpp.pack` envelope; human lines go to stderr) since 2026.9.16.1. It now **strips shared libraries the graph built** and the Android program; store, host and prebuilt libraries are never stripped |
| `why [topic]` | See 1.4. Topics: `toolchain \| runtime \| deps \| runners`. Takes `--features` (root features and `<dep>/<feature>`) since 2026.9.16.1 |
| `emit <doc>` | `xpkg` (descriptor) / `sbom` (CycloneDX 1.5 read straight out of `mcpp.lock` - no re-resolution, no network, no build) / `build-database` (the build plan as an S1 document or `compile_commands.json` entries, **without writing into the project**) |
| `index update [name]` | WARNING: the `[name]` filter **applies only to project-level custom indices**; global repos are always synced in full because `xlings update` has no per-index mode. The help text now says so - this is a documented limitation, not a bug to report |
| `publish` | **Purely local**: no credentials, no upload, no network writes; the last step prints **manual** PR instructions |

**Internal commands** (ninja invokes them): `dyndep stage bmi-equal coff-def bmi-compile bmi-supervise bmi-await`, plus the hidden
`mcpp __action-stamp <stamp>... -- <cmd>...` (a portable wrapper for `role="check"` actions that writes the stamp only when the command
exits 0). WARNING: **`mcpp stage` is no longer purely internal** - its argument shape is a contract, because a build program's action can
name the engine itself through `${mcpp.self}`: `${mcpp.self} stage --verify content --output <dst> <src>` is the portable way to copy a
file from an action (an action's command is argv with no shell, so `cp`/`copy` were never portable). `--verify` defaults to `content`.

### Machine-readable output (for CI)

**Detection rule**: **parse stdout as JSON and require both `schemaVersion` and `kind` to be present. Never rely on the exit code, and
never rely on "the command did not fail"** [docs/50-machine-output.md]. Reason: on older mcpp, `--protocol-version` is itself an unknown
option, and unknown options used to print human text to **stdout**, exit 1, leave stderr empty. SPEC-003 makes this a rule rather than
advice: a client **must not** use exit codes for capability detection [docs/specs/exit-codes.md §3.3].

- Three non-equivalent switches: `--format json` (enveloped, **6 commands**: `self env` / `xpkg parse` / `cache list` / `toolchain list` /
  `why toolchain` / `emit build-database`); `--json` (legacy bare payload, **2 commands**, **permanently retained, not deprecated, no
  warning**); `--message-format json` on the two commands whose `--format` already names their **product**: `mcpp test` (NDJSON,
  **hand-assembled, no envelope, no schemaVersion**) and, since 2026.9.16.1, `mcpp pack` (**one** `mcpp.pack` envelope printed after the
  command finishes, every human line on stderr, failure code `MCPP_PACK_FAILED`).
- The seven `kind`s are `mcpp.env`, `mcpp.xpkg`, `mcpp.cache`, `mcpp.toolchain.list`, `mcpp.why.toolchain`, `mcpp.build-database` and
  **`mcpp.pack`** (new in 2026.9.16.1) [src/wire.cppm:72-93, re-read at 2026.9.21.3; the six older ones were also verified with
  `mcpp --protocol-version` on 2026.9.15.2]. `mcpp.graph` is a **document kind** (the file `mcpp::graph_file()` names, §6), not an
  envelope, and is not in that table.
- *changed in 2026.9.16.1*: an envelope's `effects` report what the run **did**; `network` is listed whenever the run started an index
  refresh, an install or a git remote operation (including one that failed or hit its bound) and never under `--offline`. The static
  `--protocol-version` table remains what a command **may** do.
- WARNING: **`data` is omitted when the command failed** - a failure is one envelope carrying diagnostics and no `data`, exit 1. A script
  doing `jq .data.x` gets `null`, not `{}`. Test for the presence of `data` first.
- WARNING: `mcpp pack --format` is the **distributable format**, unrelated to machine output - and it is no longer the closed set
  `tar|dir`: those two are engine-owned, and any other name is looked up among the packages in the resolved graph (so an unknown value is
  refused **after** resolution, naming the formats actually available in this build).
- Exit codes are a contract now [docs/specs/exit-codes.md §2]: **0** success / **1** ran and failed / **2** usage error (no side effects
  allowed before it) / **4** environment not ready (`$MCPP_HOME` unwritable, `config.toml` corrupt, xlings bootstrap failed) / **70**
  internal error (`EX_SOFTWARE`, worth an issue) / **127** unknown subcommand. `1` can arrive **together with** an envelope on stdout, and
  every non-zero exit must leave a reason on stderr.
  => In a gate, `4` means "this machine's mcpp home is broken", not "this build failed" - do not retry it as a build failure.
  WARNING: SPEC-003 v1.0 predates **three** commands that widened the space. `mcpp run` passes the program's own 0-124 through; `mcpp test`
  uses **2** for "built but not run"; and `mcpp emit build-database` exits **1**, not 2, when there is no loadable manifest (§1.4).
  **Read exit codes per command, not off the SPEC-003 table alone.**

Field tables, the full `reason` token set and the NDJSON event table are in `references/commands.md`.

## 4. Test system and gating

- **Exit codes: `0` all ran and passed / `1` a test ran and failed / `2` a test was built and never ran** ("not run", because this host has
  no runner that reaches the artifact) [src/build/execute.cppm:2898 at 2026.9.15.2]. `2` is also the usage-error code, so a script cannot
  tell them apart by number - read stderr, or read the JSON. **A gate must require `rc == 0`**: neither "not 1" nor "`failed == 0`" is
  green any more.
- **`--no-run` (2026.9.21.3) is the answer when you only want the build for a target this host cannot execute.** Every selected test
  is compiled and linked for the target, none is executed, and the result says `test result ok. 0 passed; 0 failed; 2 built, not run`,
  exit **0**. A test that does not compile is still a failure. The NDJSON status is `built` (summary field `built`, workspace field
  `tests_built`), deliberately counted apart from `not_run`: `not_run` = "tried and could not, question open, exit 2"; `built` = "told not
  to, build was the whole question, exit 0" - **never sum the two**. `--no-run` with `--no-runner` is refused, exit 2 (one character
  apart, opposite meanings) [src/cli/cmd_build.cppm:542-551].
  WARNING: before this flag the tempting substitute was `mcpp build --target <t>`, and it is **not** equivalent: `build` compiles the
  **package**, so for a member whose only sources are under `tests/` it compiles the dependencies, compiles none of the member's own
  code, and exits 0. Upstream measured exactly that false "builds on macOS" reading.
- **Where tests come from is configurable**: `[test] discover` replaces the default `["tests/**/*.cpp"]` and takes the `[build] sources`
  vocabulary, `!` exclusions included [src/build/test_targets.cppm:22,46-50]. `discover = []` finds nothing. Duplicate test names are
  refused, naming both files. => Fixtures living under `tests/` no longer have to be moved out of the way; exclude them.
- **`-p <NAME>` takes the member directory basename or the member's relative path, unrelated to `package.name`**, and the comparison is
  **exact equality**. A full relative path such as `-p libs/core` is also accepted.
- **The filter is bare substring containment** (`std::string::find`), case sensitive, not glob, not regex, not prefix, and there is **no
  `--exact`**. A test name is the path under the matching discover glob's fixed prefix with the extension stripped, forward-slash form
  (`tests/unit/test_parser.cpp` -> `unit/test_parser`).
- WARNING: **the filter saves nothing**: the plan always contains every test; filtering only selects during build/run - this keeps
  `build.ninja` and `compile_commands.json` complete (clangd depends on the latter). => **The only way to shorten a gate is `-p`;
  filtering does not help.**
- WARNING: **but `-p` turns the fast path off** - and it is not alone. The guard requires **every** resolution-affecting override to be
  absent: `ov.target_triple` / `ov.profile` / `ov.features` / `ov.capabilities` / `ov.package_filter` / `ov.cache_mode` / `ov.accel` all
  empty and `!ov.strict` / `!ov.force_static` [src/cli/cmd_build.cppm:194-208], so any of `--target / --profile / --features / --cap / -p /
  --cache / --accel / --no-accel / --strict / --static` bypasses it (see commands.md §3 for the full list, which also carries `--locked`
  and an active `[hooks]`). => `-p` and the fast path are a trade-off, not additive - and a `--profile release` gate leg never gets a
  fast-path hit, however many times it has run before.
- **`mcpp test` has no fast path at all**: `run_tests` calls `prepare_build` unconditionally, and its build **writes no `.build_cache`
  record** - which is also why `mcpp clean --stale` sees test-only fingerprint directories as unrecorded (§8).
- **`--workspace` runs a full `prepare_build` per member with zero reuse between members**. Fan-out is **serial**, so one unbounded member
  stalls every member after it. The three deadlines do **not** behave alike: `--timeout` (default 300) **kills** the test still running and
  `--build-timeout` (0 = unlimited, **POSIX only**) **kills** the compile/link drive still running - in both cases the run continues to a
  reported result; only `--workspace-timeout` (0) merely **stops the fan-out and reports what did run**. WARNING: a hung link is
  `--build-timeout`'s business; **`--timeout` will not catch it**.
- **`mcpp test --list [--message-format json]` is zero-cost enumeration**: early-exit path, **resolves no toolchain and builds nothing**,
  works even for tests that do not currently compile. First choice for CI sharding.
- WARNING: **`mcpp test -p <member>` exits 0 for a member with no tests** - "no tests" and "tests passed" look identical in CI output.
- **`--toolchain <SPEC>` is now a declared option on `test`** (and on `run` and `pack`), so a gate leg can pin the toolchain on the command
  itself instead of exporting `MCPP_TOOLCHAIN`. The value always reached these commands; only the spelling was refused.
- **`--no-runner` is the escape hatch for a host that runs the artifact natively.** `[target.<triple>].runner` is honoured on hosted
  cross targets, so if any manifest declares a runner for the triple you are testing and that program is missing, `mcpp test` now **fails
  with a message** instead of executing the artifact bare. Each runner also receives `MCPP_RUNTIME_FILES` (deployed files and linked
  shared libraries, TAB-separated). `mcpp run --list-runners` and `mcpp why runners` are the two diagnostic entry points when a test comes
  back `NOT RUN`.
- Cross-package substring collisions really require **`--workspace`** (fan-out applies **the same** filter to every member); without
  `--workspace` and without `-p`, a rooted workspace only looks at the root package. Same-package collisions still happen (`test_parser`
  also matches `test_parser2`).

### Gate cost on a large workspace

For a workspace with a large dependency closure, a full `mcpp test` can cost far more than its compile work. Two distinct causes were
found and fixed; if you still see a long silent stretch, it is a third one.

- **Cause 1, fixed in 2026.8.30.2**: two post-link ELF passes re-read every image in full, and the memo never hit across processes because
  `resolution.json` was rewritten as a fresh object each time. Records moved to `.mcpp-runtime-verdicts.json`. (The symptom was ~15.6 s of
  silent CPU per member between "dependencies resolved" and "compiling tests", scaling with the **total module interface count of the
  dependency closure** - the attribution "re-planning the dependency closure" was wrong, the independent variable was right.)
- **Cause 2, fixed in 2026.9.11.3**: the dlopen-surface scan ran a full ELF inspection of **every linked artifact** before it discovered
  the surface was empty, and `mcpp test` pays it once per target. Upstream measured that phase at 170 ms on a `build` and a flat 17948 ms
  on a `test` with 108 binaries; after the cheap check moved ahead of the expensive work, 4 ms.
  => Any "`mcpp test` is an order of magnitude slower than `build`, that is normal" note predates this and should be re-measured.
- WARNING: the three structural costs are **unchanged**: test has no fast path, `-p` disables the fast path, `--workspace` reuses nothing
  between members. Gate discipline stays as it was.
- Concurrency is now bounded by config as well: `[build] default_jobs` in `$MCPP_HOME/config.toml` **also caps `mcpp test`'s test-process
  concurrency**, whose fallback was otherwise the whole machine (§8).

## 5. Configuration reference index

The easiest `mcpp.toml` traps are in `references/config-index.md`; field-by-field tables are in `references/mcpp-toml.md`.

## 6. hooks and build.mcpp / mcpp::action

### `[hooks]`

These are **build sound effects and desktop notifications**, not build hooks. Three scope rules:

1. **Only the root project's hooks run.** Every manifest mcpp parses carries the field, including dependencies', but a dependency's
   `[hooks]` is **permanently inert**. This is the only reason `mcpp add`-ing a third-party package does not become "next build runs their
   shell commands" [src/hooks.cppm; modules/manifest/src/types.cppm].
2. **Only `mcpp build` runs hooks.** `mcpp run` / `mcpp test` / `mcpp build --configure-only` also build, and **deliberately do not run
   them**. A virtual workspace root builds nothing, so `[hooks]` there never fires.
3. **If preparation fails, none fire** (invalid manifest / unresolvable dependencies / no usable toolchain), because "the hook program may
   be exactly what preparation failed to install".

- **`side_effect = true` is hard-rejected by the parser** => **a hook cannot decide build success or failure**; all four failure modes
  (cannot start / non-zero exit / timeout / loop keepalive failure) are **warnings only**.
- **A hook gets no `MCPP_*` context** - the PR says verbatim: "Hook context (MCPP_PROFILE, MCPP_TARGET, ...) is deferred".
- WARNING: **declaring an active hook makes the project leave the no-op fast path** => installing a hook permanently forfeits sub-second
  builds.
- WARNING: **a hook is code and `mcpp.toml` is part of the repository**: building a freshly cloned project runs whatever its `[hooks]`
  say, with the caller's privileges.
- A hook's process tree is killed with the build: every child goes into its own process group (a job object on Windows) and mcpp sends
  `SIGKILL` to the group on `SIGINT`/`SIGTERM`/`SIGHUP`. => A `timeout`-wrapped mcpp no longer leaks a spinning ninja per timeout.

### `build.mcpp` + `mcpp::action` (the real build-time external command mechanism)

- Four `role` values: `source` (joins the compile set) / `check` (writes a stamp, runs in parallel with compilation, waits only when
  `blocking=true`) / `object` (joins the link set) / `artifact` (input is the link output, runs **after** linking)
  [docs/30-build-mcpp.md].
- **Runtime environment**: `MCPP_TARGET` / `_OS` / `_ARCH` / `_ENV` / `MCPP_HOST` / `MCPP_PROFILE` / `MCPP_OUT_DIR` / `MCPP_MANIFEST_DIR`
  / `MCPP_FEATURE_<NAME>` / `MCPP_FEATURES` / `MCPP_DEP_<NAME>_DIR`, all **unconditionally part of the re-run key**. => The only
  build-time extension point that can see target/profile/out_dir. The contract has grown a lot since - package identity
  (`MCPP_PKG_NAME`/`_NAMESPACE`/`_VERSION`/…), `MCPP_CXX_STDLIB`, `MCPP_TOOLCHAIN_SYSROOT`/`_BINUTILS_DIR`, `MCPP_ACCEL`,
  `MCPP_DEVICE_SOURCES` (newline-separated), `MCPP_PACK_FORMAT`/`_STAGE_DIR`, `MCPP_DEP_<NAME>_LINKAGE`. The full list is in
  `references/env-vars.md` §3; do not derive the package name from the last segment of `MCPP_MANIFEST_DIR` (that is a directory name and
  they differ whenever packages sit under a common directory).
  New in 2026.9.16.1: **`MCPP_GRAPH_FILE` / `mcpp::graph_file()`** - the resolved graph as a JSON document (`kind = "mcpp.graph"`,
  packages in dependency order, each with `manifest_dir`, `features`, `targets`, link form and its `[package.metadata]` verbatim). Only
  the **root** package's program receives it (a dependency's reads `""`), and its content joins the re-run key, so editing a
  dependency's metadata re-runs the root program while editing its sources does not. **`MCPP_PACK_STRIP`** (`1`/`0`) and
  **`MCPP_PACK_DEBUG_SYMBOLS_DIR`** tell a packaging member that stages its own libraries what `--no-strip` / `--debug-symbols`
  decided. `dep_dir` / `dep_linkage` / `dep_bin` now share one naming derivation, so a package with `namespace = "ns"` and
  `name = "x"` is also reachable as `MCPP_DEP_NS_X_*` (its tool used to be published under the bare name only).
- **Hard constraint: output file names must be known at prepare time.** "mcpp fixes the source set during prepare, so an output whose NAME
  is unknown cannot be built" [modules/buildmcpp/src/directives.cppm; docs/30-build-mcpp.md]. => **Content-hashed bundler outputs
  (`index-a1b2c3.js` from vite/webpack) cannot be declared.** Secondary constraints: the command is **argv, not a shell string** (`npm run
  build && cp ...` is not expressible); the default timeout is 600s. The interpolation set has grown past the original four
  (`${mcpp.out_dir}` / `${mcpp.bin_dir}` / `${mcpp.compile_db}` / `${mcpp.target_file:<name>}`) with `${mcpp.self}` (the engine's own
  absolute path - use it with `stage` to copy files portably) and `${mcpp.stage_dir}` (the bundle tree `mcpp pack` computes; usable only
  in the `artifact` role under a packing build, and a **refusal** rather than an empty expansion anywhere else). The fixed argv buffer cap
  is gone: an action's lists grow on demand.
- **Declare a `depfile` for a command whose real inputs it discovers by reading source.** Without it, changing a file the command merely
  *read* triggers no rebuild and `mcpp build` stays green on a stale artifact. WARNING: do not also declare the depfile as an `output()` -
  ninja's `deps = gcc` consumes and deletes it, so an edge promising that output is dirty for ever.
- => If you decide to keep a hashed-output frontend build out of the mcpp graph, state the reason correctly: not "mcpp has no hook
  mechanism" (factually wrong), but "`[hooks]` cannot decide success and gets no context, and `action` requires output names known at
  prepare time".
- **The build-program directive protocol is a hard floor.** It has stepped 6 -> 7 -> 8 -> 9 -> 10 -> 11 in this window; the engine refuses
  a program declaring a version it does not know, and calling a function the bundled `mcpp` module lacks fails at `build.mcpp` **compile**
  time rather than as a protocol error. => A package whose build program uses a recent API must state its engine floor; the upgrade is not
  reversible for consumers. The protocol is **still 11** at 2026.9.24.1 [modules/buildmcpp/src/program_protocol.cppm:84 @ b4824697]: `graph_file()`,
  `pack_strip()` and `pack_debug_symbols_dir()` (2026.9.16.1) arrived without a bump, so for them the `build.mcpp` compile error is the
  only signal an older engine gives.
- WARNING: **`[generated_files]` is a literal "path -> file content string" write; it cannot execute any command** - not the same thing as
  `build.mcpp`'s `mcpp:generated=`.
- **Extending mcpp no longer means changing mcpp.** A rule package declares which device source extensions it compiles and which module
  supplies the rules (`[features.<f>] device_extensions` + `rule_module`, which must appear together), and the engine holds no package
  name, feature spelling or module name of its own. A project that declares `[rules]` does not have to write a `build.mcpp` at all - mcpp
  synthesises one into the build directory, and stops as soon as you copy it to the project root and take over.

## 7. Cross-compilation and targets

Target selection, toolchains and sysroots are in `references/cross-compilation.md`.

## 8. Cache discipline

What the caches key on and how to clean them safely is in `references/cache-discipline.md`.

## 9. Ecosystem cross-references (pointers only, no duplicated content)

- **Device code, custom languages, non-desktop targets, bare metal** -> `references/heterogeneous-and-baremetal.md`. Route there for any
  of: the accelerator axis (`[build] accel`, `--accel` / `--no-accel`, `cfg(accelerator = ...)`, constrained `{ glob, accel }` sources,
  `[package] accelerators`, `[[runtime.artifacts]] accel` and consumer matching); **writing or reading a build plugin / rule package**
  (`mcpp::action` roles, depfiles, `device_extensions` + `rule_module`, `tools = [...]` host tools, `dist-*` members); the refusal *"mcpp
  has no role for the extension '.x'"*; the **wasm / Android / iOS** rows (capability pins, `min_api_level`, `[target.<sel>.abi]`
  `threads`/`exceptions`, `run --format apk|app`); and **freestanding targets** (the thirteen `*-none-elf` / `thumb*` rows,
  `sysroot = ""`, `std-freestanding`, board-support packages, runners, openkal / openarch). It walks `examples/09-heterogeneous`,
  `examples/12-a-new-device-language` and `examples/13-platform-targets` file by file, and carries the `#403` history.
- **Packaging and publishing to mcpp-index** -> `references/packaging.md` (full descriptor field table, the seven feature sub-keys,
  GLOBAL+CN mirrors, the nine lint rules, the validate/publish CI chain, the isolated-home verification recipe, four pitfalls and three
  always-green traps, worked example PR #299, namespace conventions).
  WARNING: the upstream `add-mcpp-index-package` skill shipped in the mcpp-index repo is **outdated**: step 8's README classification
  table **no longer exists**; "features can only gate sources" is **now wrong** (seven sub-keys); "four package shapes" is **now nine**;
  "xpm must cover three platforms" holds for only 115/175. [field-tested 2026-08-31]
  WARNING: that file's own mcpp-side citations were re-pointed for the `docs/` renumbering but its index-side facts (descriptor fields,
  lint rules, CI chain, pinned `MCPP_VERSION`) were **not re-verified against the mcpp-index repository** at this baseline. Treat them as
  dated 2026-08-31 and check before relying on a number.
- **The bundled xlings** is pinned at `2026.9.16.1` for mcpp 2026.9.24.1 [src/xlings/xlings.cppm:99 @ b4824697]. Its region-chain and bounded
  refresh behaviour (index artifact `{GLOBAL, CN}` tried in order before git; `XLINGS_UPDATE_TIMEOUT` and friends) is what an mcpp
  index refresh inherits - see the `xlings` skill, `references/version-notes.md`. The default `mcpplibs` index entry
  mcpp writes now carries `artifact = { GLOBAL = <github>, CN = <gitcode> }` and an existing home's `.xlings.json` is upgraded in place.
- **Filing issues / PRs / releases against mcpp itself** -> `references/contributing.md`. WARNING: the upstream `mcpp-contributing` /
  `mcpp-release` / `pr-workflow` skills are **outdated**: `src/platform/` and `src/manifest/` have moved into `modules/`, the
  `src/xlings.cppm` path is wrong, and "merge commits by default" is the opposite of reality (zero merge commits in the last 120).
  [field-tested 2026-08-31]
- **Coding style (modules / naming / `.cppm` organisation)** -> the `mcpp-style-ref` skill.
- **xlings itself (install/use/subos lifecycle, building your own index)** -> the `xlings` skill; upstream also ships `xlings-usage` / `xlings-quickstart` / `xlings-build`
  skills.

## 10. references/

- `whats-new.md` (§0.1), `config-index.md` (§5), `cross-compilation.md` (§7), `cache-discipline.md` (§8) - the long sections of this
  file, moved out so it loads fast.
- `commands.md` - full flag tables for all 28 top-level commands, exit codes, the machine-output envelope and the data fields of its six
  kinds, the NDJSON event table, the full `reason` token set.
- `mcpp-toml.md` - mcpp.toml section by section and field by field (types/defaults/allowlists/validation), workspace inheritance, the full
  `cfg()` predicate set, dependency selector syntax, and (§17) the target-side declarations added in 2026.9.16-2026.9.21: `[c-abi]`,
  `[c-abi-absent]`, `[kernel-abi]` interfaces, `c-environment`, `platform-sdk`, `[package.metadata]`.
- `env-vars.md` - the three environment-variable tables, the `MCPP_HOME` resolution chain, flag/env equivalences.
- `troubleshooting.md` - symptom-indexed failure manual (build reports success but compiled nothing / headers not found / artifact will
  not start / ...); §K collects what the 2026.9.16.1-2026.9.21.3 releases newly produce (cold cache, lock diff, host-header isolation,
  flag-word warnings, runtime-split refusals, offline codes, macro renames) and the defects still open; §L the messages new in
  2026.9.24.1 (toolchain namespace, frozen gcc headers, MSVC toolset selection).
- `version-notes.md` - **the per-version change history**: the `docs/` renumbering map, then one section per release from `2026.9.1.1` to
  `2026.9.24.1` listing its user-visible changes with the spelling to type. **This is the entry point for "that is new, how do I use it".**
  Also older version markers, CHANGELOG blind spots and upgrade notes.
- `contributing.md` - contributing to mcpp itself: which upstream skills/docs are outdated, the three sources of version truth, how to
  write an issue (#529 as the worked example), a full sample of commit-message style, self-hosted build and e2e, the CI surface and its
  four gate scripts, CHANGELOG conventions, the release flow, **external communication rules**.
- `heterogeneous-and-baremetal.md` - the four surfaces that are not an ordinary host build, each at hands-on depth (complete manifests,
  commands, artifact paths, prerequisites, refusal texts): the **accelerator axis** and a file-by-file walk of all seven
  `examples/09-heterogeneous` sub-examples; the **build-plugin framework** (`mcpp::action`, the four roles, depfiles,
  `device_extensions` / `rule_module`, `tools = [...]`, `dist-*` members) with `examples/12-a-new-device-language` walked end to end and a
  checklist for adding your own device language; the **wasm / Android / iOS** rows (tiers, capability pins, `min_api_level`,
  `[target.<sel>.abi]`, the wasm artifact contract, `pack` / `run --format`); and **bare metal** (the thirteen freestanding rows, the
  freestanding link model, `std-freestanding` and its allocator features, the zero-libc tier, runners, board-support packages, openkal /
  openarch). Plus the `#403` history and what `openhal` actually is, and (§6.10) the openkal chain's current version pairs, the
  openkal 0.14 `KAL_TERM_PASS_CONTROL` terminal position, and openkal-musl 0.16+'s real `tcsetattr` / `sigaction` behaviour.
- `packaging.md` - submitting a package to mcpp-index: Form A/B and the nine package shapes, the full descriptor field reference (and how
  it differs from mcpp.toml), the seven `features` sub-keys and their negative list, `generated_files`, GLOBAL+CN mirrors and `gtc`, the
  nine lint rules and local reproduction, the validate/site-check/publish-artifact chain, a full sample of member conventions, the
  isolated-home verification recipe, four pitfalls and three traps, PR #299, namespace conventions.
