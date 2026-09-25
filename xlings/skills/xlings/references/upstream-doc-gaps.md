# Reference: where upstream docs and the bundled skill are wrong

> Baseline xlings source `main @ 4ea4eac` / `2026.9.14.1`, dated 2026-09-16. Spot-checked 2026-09-23 at `main @ 84572b0`
> (`2026.9.20.1`): row 2 of §2 (the capability list missing `list_index_versions`) still holds; `docs/spec/interface-ndjson-v1.md`
> gained §3.3.1 (parameter validation) and extraction error codes, and `docs/spec/xlings-json-schema.md` /
> `docs/quick-start/custom-index.md` now document the region chain and the network-bound variables - those passages
> match the source. The other rows were not re-checked.
> Two uses: (1) know which upstream passages must not be trusted; (2) source material if these are ever reported upstream.
> WARNING: get the user's approval before any upstream communication, and never put your project's internal package names, paths, or test names into an upstream report.
> **The "recent behaviour changes" table that used to live in §4 has moved to `version-notes.md`** and is now
> maintained per release; §4 here only records where upstream's own change record lives.

---

## 1. Why xlings docs are not a source of truth

Version stamps on the five `docs/quick-start/` files: `project-env.md` and `custom-index.md` say **0.4.36**,
`multi-version.md` and `self-management.md` say **2026.7.29.0**, `subos-and-agent.md` carries a 2026-08-03 date.
Current is **2026.9.14.1** — the two 0.4.36 stamps are now **more than a dozen releases behind**. The docs-example
check (`tests/scripts/test_docs_examples.py:15-21`) covers **only 6 files** (two READMEs + `multi-version` +
`subos-and-agent` + `subos-isolation` + `interface-protocol`) — `custom-index.md`, all of `spec/`, and `index-*.md`
are **outside its scope**, which is exactly why #1 and #5 below survive.
Note in fairness: `self-management.md` and `multi-version.md` gained substantial new prose in 2026.9.5.1 and
2026.9.12.1 (the sysroot check, `--show-ok`, `--subos`, lossy repairs, relocated homes, the local overlay,
cross-subos removal) **without their header stamps being touched** — so a stale stamp no longer implies stale
content in those two files, only that the stamp itself is unmaintained.

**Source-of-truth priority when writing a skill:**
1. **Command surface** -> `src/cli/spec.cpp:22-75` (the only true command tree)
2. **Behaviour / exit codes** -> the corresponding `.cpp` implementation
3. **Design intent / postmortems** -> the long inline comments in `.cpp`/`.cppm` (comment quality here is very high; many carry real measurements)
4. `.cppm` header comments -> **clues only** (measured to contradict the implementation; see `use` in §2)
5. `docs/` -> **clues only**

## 2. Divergences between docs and code (ordered by certainty)

All re-verified at `4ea4eac`; the ones that moved got new coordinates, and four were added.

| # | Severity | Problem | Evidence |
|---|---|---|---|
| 1 | **Certain, wrong content** | `quick-start/custom-index.md:133-141` writes the index-repo layout as `packages/<pkg>/xpkg.lua`, but the code **only accepts `pkgs/`** | Code: `xim/index.cpp:190`, `repo.cpp:25,231`, `catalog.cpp:370,385,399`; **the same file contradicts itself** — `custom-index.md:91` says the tarball root contains `pkgs/` |
| 2 | **Certain, missing item** | `spec/interface-ndjson-v1.md:197-215` lists only **19** capabilities; the code has **20**, missing `list_index_versions` | `src/capabilities.cpp:257` (`destructive=false`, `dataKind: index_versions`). It is the programmatic counterpart of `xlings index list` |
| 3 | **Certain, wrong number** | `spec/xlings-json-schema.md:175` attributes "a sub-index listed first gains the whole official index out of nowhere" to **#576**. The version 2026.8.30.1 is right, the PR number is not: 2026.8.30.1 = **#575** (`335c4c6`); #576 (`f5a0775`) is the payload-ownership change | Confirmed against `git log`; the sentence moved from `:157-159` as the file grew |
| 4 | **Certain, dead reference** | `design/package-index-ecosystem.md:138` cites "config.cppm L443-459" and pastes **single-argument** pseudocode; the real logic is `src/core/config.cpp:564-575` and the signature is **two-argument** | `config.cpp:81`; `config.cppm:164` |
| 5 | **Certain, stale metadata** | **15** doc files still carry a localized version-stamp line reading `0.4.36` / `0.4.51` / `0.4.53` / `0.4.63`; current is `2026.9.14.1` (was 13 files at the previous baseline) | `grep -rlE '0\.4\.(36\|51\|53\|63)' docs/` -> 15. Ironically `tests/scripts/test_docs_examples.py` lists `版本: 0.4.36` as a literal staleness marker, but applies it to **only 6 files** |
| 6 | **Certain, thin coverage** | The docs-example check covers 6 files | `test_docs_examples.py:15-21`. Directly explains #1 and #5 |
| 7 | **Certain, doc blank** | `xlings why`, `xlings profile *`, `xlings script`, `self doctor --deep/--scope` **exist only in the generated reference**, with zero prose documentation | `quick-start/self-management.md` never mentions `--deep`/`--scope` even after its 2026.9.5.1 / 2026.9.12.1 expansion; `xlings profile` is an entire feature surface with no docs |
| 8 | Medium | `design/index-distribution.md` carries two generations of the pointer format side by side: `:44-45` describes per-index `xim-index[-<sub>]-latest.json` (release assets), and only `:106` says 0.4.54 moved to a merged single file `xim-index-pointers.json` (a repo file). The earlier section is not marked as superseded | Code uses the latter: `xim/indexfetch.cpp:469` |
| 9 | Minor | `custom-index.md:149` says `xlings update` is "git fetch + reset", but since 0.4.52+ it defaults to artifact download, with git only as fallback. **Now doubly wrong**: since 2026.9.12.1 `update` also **deletes** local overlay recipes that match the synced index | `xim/repo.cpp:554-562`; `xim/commands.cpp:2477-2490` |
| 10 | Minor | `spec/diagnostics.md:116` says `--ui-mode` "has only two values" and lists `cli`/`tui`, but `:145` in the same file and the generated reference both say `cli/tui/auto` | Readable as "two render modes plus one auto selector", but literally contradictory |
| **11** | **New, certain, incomplete list** | `spec/diagnostics.md:169-180` calls itself the **stable code table** and instructs "add your code here when you add a diagnostic", but names **15** codes while the source defines **25 dotted ones plus a 10-strong hyphenated `xvm-*` family**. Everything from 2026.9.12.1 on is absent: `xim.uninstall_hook_failed`, `xim.uninstall_recipe_unavailable`, `xim.overlay_identical`, `xim.namespace_priority`, `xim.subos_unreadable`, `self.upgraded` — and so are the older `xim.ambiguous_target`, `cli.bad_theme`, `xself.kept_existing`, `xself.needs_confirmation`, and the whole `xvm-*` family | `grep -rhoP '\.code\s*=\s*"\K[a-z_.]+' src/ \| sort -u` prints **26** lines: the 25 dotted codes plus a bare `xvm`, which is the regex truncating `xvm-sysroot-drift` & co at the hyphen. Hyphen-aware: `grep -rhoP '\.code\s*=\s*"\K[a-z_.-]+' src/ \| sort -u` -> 35 (25 + 10) |
| **12** | **New, certain, wrong attribution** | `spec/xlings-json-schema.md:31` describes the global `version` key as "written after a successful `self doctor --fix`, used to decide whether package records are still an old client's format". That is **`verifiedBy`'s** job since 2026.9.12.1; `version` moves on every `self install`/upgrade regardless | `src/core/config.cpp:1370` (version stamp) vs `:1398` (verifiedBy, stamped only when `outstanding == 0`); `config.cppm:607-613` |
| **13** | **New, certain, missing items** | The global field table (`spec/xlings-json-schema.md:21-33`) omits `verifiedBy`, `knownProjects`, `subos`, `repo`, `need_update`, `mirror_fallback`, and every `xim.*` key; the project table (`:240-251`) still omits `versions` and `xim.index-base` | Parser: `src/core/config.cpp` |
| **14** | **New, minor, upstream's own note** | The `ForeignPayload` remedy still prints `xlings subos use X && xlings self doctor --fix` although `--fix --subos X` exists since 2026.9.12.1 | `src/core/xself/doctor.cpp:1365`. Upstream recorded this on its own follow-up list — **not a finding to report as new** |

### Three more (flagged in place in this skill's body as "do not copy")

- **`use <name>` without a version**: `docs/quick-start/multi-version.md:52-56` and the header comment in
  `src/core/xvm/commands.cppm` both say "1 candidate, switch to it directly (exit 0)", but the
  implementation is `// NO single-candidate auto-switch.` (`commands.cpp:1079`). The revert landed in #558 /
  `e3a8ab4` (2026.8.22.3). Upstream therefore carries three mutually contradictory statements, two of them stale.
  **Still true at 2026.9.14.1.**
- **lowercase `mirror` example**: the worked example at `spec/xlings-json-schema.md:518` writes
  `"mirror": "cn"`. It is internally consistent (it also lowercases the `XLINGS_RES` key at `:533`), but
  matching at runtime is exact and **case-sensitive**: writing only `"mirror": "cn"` without a custom
  `XLINGS_RES` misses the built-in CN table and **silently falls back to GLOBAL**.
- **schema field-table omissions**: see #13 above — the omissions grew rather than shrank.

### Encoding and formatting

`docs/architecture/overview.md` still has **7 encoding corruptions** (replacement characters;
`grep -c $'\xef\xbf\xbd' docs/architecture/overview.md` -> 7). The structure section of `AGENTS.md` is stale: the
`src/platform.cppm` and `src/libs/` it lists **do not exist** (moved to `modules/platform/`, `modules/json/` +
`modules/tinyhttps/`; the move is recorded in the top comment of `mcpp.toml`). `AGENTS.md` also writes
"SubOS lifecycle (create/use/**fork**/remove/stop)" — fork is an internal concept, not a CLI verb.

## 3. The bundled upstream skill (`xlings agent skills usage`) as the baseline

The content lives in `src/agent/skills/usage.cppm` (**still 114 lines**); `usage.cpp:24-26` substitutes the
placeholder `@@COMMAND_REFERENCE@@` (at `usage.cppm:45`) with `cli::spec::agent_reference()` at runtime — **the
command reference is rendered live from the spec and can never go stale**. That is its strongest property, and
this skill cannot reproduce it (it relies on version stamps plus re-verification instead).
=> It also means the bundled skill **already knows about `remove --all-subos` and `doctor --show-ok`** in its
command-reference section while its hand-written prose sections do not. Those are the parts to distrust.

Structure (`usage.cppm` line numbers):
- `:25-40` **RULES** (4 hard rules): (1) always pass `--yes` to install/remove/update (otherwise it **hangs**
  non-interactively); (2) always pass `--agent`; (3) never guess a package name, run `xlings search` first;
  (4) before installing anything, check for a `.xlings.json` and if present run bare `xlings install --yes --agent`.
- `:42-45` COMMAND REFERENCE (placeholder injection)
- `:48-67` **DECISION TREES** (three: installing a tool, diagnosing a build failure, project has `.xlings.json`)
- `:70-88` **SubOS** section, including the security statement: Linux sandbox mode isolates the filesystem,
  while **macOS and Windows only redirect HOME/USERPROFILE**, so use an OS sandbox or a VM for untrusted code;
  each SubOS has its own tool-version mapping, binaries are shared globally, creation is
  instantaneous, and `default` cannot be removed (`:88`).
- `:91-98` FLAGS REFERENCE; `:100-109` CONFIG & SELF-MANAGEMENT

The rendering logic of `agent_reference()` is at `src/cli/spec.cpp:272`: **global options get their own
section first** — the comment explains that a per-command listing that skips the root node would drop them
entirely, and an agent reading only that section would never learn the two flags the rules above tell it to
always pass (`:273-278`).

**What this skill adds on top**: the danger-corrections section, the distinction between the two kinds of
mirror, the partial exemption of `projectScope`, `XLINGS_HOME` write-back and the self-contained
reassessment, attribution of the module move, mcpp integration and where `[xlings] deps` land, the boundary
criteria between the two indexes, and a project-local isolation recipe.
**What it has and this skill does not**: the live command reference (replaced here by a version stamp plus
the `references/commands.md` snapshot).

## 4. Where upstream's change record actually lives — there is no CHANGELOG

The repo has **no top-level CHANGELOG file** (the only `changelog.md` in the tree is an archived copy under an
old agent-docs directory). Three places carry the story, none of them complete on its own:

| Source | What it has | Catch |
|---|---|---|
| **GitHub Releases** | tags | **Every release body in the 2026.9.x window is empty.** "Read the release notes" is not actionable advice |
| **The merging pull request** | the full narrative, including real-machine measurements | This is the one to link to. #577 / #580 / #581 / #585 / #588 / #591 / #596 |
| `.agents/docs/*-release-<ver>-notes.md` **inside the repo** | the same narrative plus post-release verification | **Not published** — only visible if you have the source. Readable with `git show HEAD:.agents/docs/...` even when a sandbox masks `.agents/` from the filesystem |

Commit messages are unusually good here: each release commit's subject is a one-line statement of the behaviour
change (`git log --oneline <old>..<new>` is a serviceable changelog).

**The per-release list of user-visible changes now lives in `version-notes.md`**, which also carries the
"still open, do not document as fixed" table. Keep it there rather than duplicating it here: this file is about
upstream *documentation* being wrong, which is a different question from upstream *behaviour* having changed.

For the mechanism, user-visible impact, and escape hatches of #575 and #576, see SKILL §5.3,
`config-layout.md §4-5`, and `troubleshooting.md B1/B5`.

## 5. Item-by-item staleness of the two bundled skills

### 5.0 Where they live (important)

`xlings-usage` and `xlings-quickstart` ship **inside the xlings repository's own `.agents/skills/`**, so the
skill distributed with upstream source carries exactly the stale content below. This means (a) fixing it has
upstream value, and (b) anyone who takes the skill from upstream inherits the same errors.
**Re-verified at 2026.9.14.1: every item in 5.1 and 5.2 below still reproduces** — `xlings-usage/SKILL.md:60`
still teaches `--pick` (`-i`) and `:137-138` still prints the `{"protocol":...}` shape. Nothing was fixed in the
seven releases, and the surface the skill does not cover has grown by another release's worth of verbs.

**Overall assessment:**
- **`xlings-usage`: moderately trustworthy, roughly 80% accurate.** The skeleton (subos lifecycle, sandbox
  semantics, `XLINGS_RES`, the multi-version model) matches the source, but **two of three rows in its `use`
  behaviour table are wrong**, and it documents a `--pick` argument that has been removed — precisely the two
  spots an agent is most likely to copy straight into a script.
- **`xlings-quickstart`: essentially unusable, rewrite it wholesale.** Written before 0.4.8, its backbone is
  the `xim`/`xvm` short-alias command family; those aliases were removed in 0.4.8 and now **actively error out
  with exit 2**. Its very first verification command, `xlings help`, is itself an unknown command. Its
  `references/commands.md` is more harmful still as a "cheat sheet" — **6 of its 9 commands are not executable**.

### 5.1 `xlings-usage/SKILL.md`

| # | SKILL claim | Reality | Impact |
|---|---|---|---|
| **A1** | [:54-58] `use <name>` no-version behaviour table: `1 -> switches to it`; `>1 -> exit **2**` | **Both rows wrong.** `commands.cpp:1079` has `// NO single-candidate auto-switch.` (reverted by #558/`e3a8ab4`, 2026.8.22.3); `cmd_use_by_name` unconditionally does `return cmd_list_versions(...)` (`:1140`), which always `return 0` (`:1072`). The `>1` exit code is **0**, not 2 (exit 2 was a short-lived 2026.7.31.2 behaviour; the `commands.cppm` header comment records why it was reverted). The third row, `0 -> exit 1`, is correct | **High** |
| **A2** | [:60-62] `--pick` (`-i`) arrow selector, opt-in, fails loudly with no terminal | **All three wrong.** The argument does not exist (`spec.cpp:38-39` has only `-a/--all` and `--strict`). The picker returned in another form: `commands.cpp:1112` `if (!all && stream.interactive())` emits a `PromptEvent` **automatically**, and the switch is the persistent config `xlings config --interactive true`. It does **not** fail loudly — the opposite: the `NobodyToAsk` branch at `:1135` is **empty** and silently falls back to a listing | **High** |
| **A3** | [:135-139] bare `xlings interface` -> `{"protocol":"1.0","capabilities":[...]}` | A bare call returns `{"kind":"result","exitCode":1,"error":"capability name required. Use --list…"}` and **exits 1** (`interface.cpp:91`). Getting the capability table requires `--list`; and the key is **`protocol_version`**, not `protocol` (`:84`) | **Medium-high** |
| **A4** | [:106] "project subos activates automatically only when the project has a `.xlings.json` **with a workspace declaration**" | The trigger is **the existence of a project `.xlings.json` itself**, unrelated to `workspace`. `config.cpp:667` sets `projectSubosName_`, and `:351-352` / `:468-473` do the routing: a subos name means Named, **otherwise always Anonymous** (`<project>/.xlings/subos/_`). `workspace` is an independent, parallel field. Writing the condition too narrowly suggests "no workspace means no isolation" | **Medium** |
| **A5** | [:153-160] `index_repos` example (xim listed first) | The literal JSON still parses, but the old mental model it carries was overturned by **#575**: **array position no longer confers any privilege**, and each entry gets only the index under its own name. Entries also support three keys the SKILL never mentions: `artifact`/`source`/`version`. A custom index configured from that minimal example **gets no artifact acceleration and goes through git only** | **Medium** |
| **A6** | New command surface missing entirely | `why`/`info`/`index list\|use`/`profile *`/`agent skills`/`script`/`subos runtime`/`subos new --runtime`/`subos use --gpu`/`self doctor --deep\|--scope\|--fix\|--reset-metadata`/`--ui-mode`/`config --theme\|--interactive\|--index-repo`/`install -u\|--use`/`remove --force` — plus, since 2026.9.12.1, `remove --all\|--all-subos\|--subos`, `config --list-xpkg\|--remove-xpkg\|--clear-xpkg`, `self doctor --subos\|--show-ok` | **Low** (incomplete, not misleading). Note the injected command reference does list these; only the prose lags |

### 5.2 `xlings-quickstart/SKILL.md` + `references/commands.md`

| # | SKILL claim | Reality | Impact |
|---|---|---|---|
| **B1** | [:12,37,53-59,65,78-88] [commands.md:8,21-29] the whole `xim` command family: `xim -h` / `xim -s gcc` / `xim -l` / `xim --update index` / `xim --add-xpkg` / `xim --add-indexrepo` | The five aliases `xim`/`xvm`/`xself`/`xsubos`/`xinstall` were **removed wholesale in 0.4.8** (`compact/xself.cppm:85`). Invoked as argv[0], they print `[error] xim was removed in 0.4.8…` and **exit 2**. Leftover symlinks are actively cleaned by `self init` / `self doctor --fix`. Locked down by the e2e test `cli_short_alias_removal_test.sh` | **High** (about 1/3 of the SKILL plus a whole block of commands.md) |
| **B2** | [:36] [commands.md:7] `xlings help` as the first post-install verification command | `spec::root()` has **no `help`** among its children; the unknown-command detection at `cli.cpp:1584` fires with `[error] unknown command: help` and **exit 1**. Working forms: `xlings --help`, `-h`, or bare `xlings` | **High** (the quickstart fails at step one and reads as "the install is broken") |
| **B3** | [:40] `If xlings/xim is not found, reload shell profile` | `xim` **will never exist** (B1), and `self init` actively deletes it. This troubleshooting advice points at a check that can never be satisfied | **Medium** |
| **B4** | [:92,95-97] `Use xvm through xlings for version switching` | The command form `xlings use <tool> [version]` is still valid (the one-shot `@` form `xlings use gcc@16.1.0` also works), but the name `xvm` is gone; and listing "without version" and "with version" side by side suggests they differ only in a default version (see A1 for what actually happens) | **Medium-high** |
| **B5** | [:109] `managed per subos via xvm metadata` | The mechanism is directionally right; "xvm metadata" is a retired external name. Stale wording, not a factual error | **Low** |

### 5.3 Addendum

- **#576 produces no staleness entry** — neither SKILL makes a falsifiable claim about installed-payload
  ownership; the facts that need **adding** are in `config-layout.md §5`.
- **Neither SKILL hard-codes a version**, so there is no direct "version behind" assertion. But quickstart's
  overall shape corresponds to **<=0.4.7**, and usage's `use` behaviour table corresponds to **2026.7.31.2**,
  behind #558 (2026.8.22.3) and #575/#576 (2026.8.30.x).

### 5.4 Parts of the two skills that are still correct and can be reused as-is

**`xlings-usage`**: the install scripts `tools/other/quick_install.sh` / `.ps1` exist; `xlings --version`; the five base command names and argument shapes `install`/`remove`/`search`/`update`/`list`, variadic multi-package arguments, `-y`/`-g`; the description of coexisting multiple versions + version-view + refcounted shared payload; `--strict` semantics and "programs that did not follow are named" (`commands.cpp:681-706`); `--all` widening candidates to all subos; **the full SubOS lifecycle command set** (`new`/`use`/`list`(ls)/`remove`(rm)/`info`(i)/`stop`/`runtime`), **and it correctly uses `new --from` rather than the fictional `fork`**; `--storage shared|tmpfs|image` (default shared, default image-size 50G); `subos use` with `--sandbox`/`--cmd`/`--keep`/`--no-keep`/`--ttl`; **the sandbox security warning is accurate** (only Linux is real isolation; macOS redirects HOME and Windows redirects USERPROFILE, isolating dotfiles only — `sandbox.cpp:985-1047`); the `--from subos:<name>@<ver>` pkg-spec form; **the entire `XLINGS_RES` mirror configuration section is exactly right** (key names and default values match verbatim) — with two things it does not say: values may also be arrays, and **the CN mirror of the default index repo uses gitee, not gitcode** (res mirrors and index mirrors are two separate host sets); `~/.xlings/.xlings.json` as the global config path.

**`xlings-quickstart`**: the install script URLs; the four package-name forms `<name>` / `<name>@<ver>` / `<ns>:<name>` / `<ns>:<name>@<ver>`; `install`/`remove`/`search`/`update <name>`; `subos list` / `new <name>` / `use <name>`; the model of "package storage can be shared globally while the active version mapping is per-subos"; the repository address in `references/links.md` matches `Info::REPO`.

### 5.5 Disposition

| Target | Recommendation |
|---|---|
| `xlings-usage` | Keep it; spot-fix A1-A5, then fill in the new command surface per A6 |
| `xlings-quickstart` + `references/commands.md` | **Rewrite wholesale** — its organising skeleton is the `xim` command family, so patching item by item costs more than a rewrite |
| Every copy in circulation | All need the same fix, **including the one inside the xlings repository itself**. Filing an upstream issue is worth considering, **but wait for the user's approval first** |

This skill supersedes both: it takes over usage's subos / multi-version / `XLINGS_RES` skeleton and
quickstart's install, package-name-form, and custom-index flow.

## 6. The former `xpkg-creater` skill copy

The unaudited `xpkg-creater` skill copy this skill once pointed to has since been audited against the
xlings and xim-pkgindex sources and absorbed into `references/xim-packaging.md` (claims that could not
be verified are marked "unverified" there). The copy itself was retired on 2026-08-31. The audit
confirmed the two lines previously cited (new packages write `spec = "2"`; `res = true` is legacy) and
corrected the rest where stale; use `xim-packaging.md`, not any surviving copy of the original.
