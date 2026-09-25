# Reference: the environment variables xlings actually reads

> Baseline xlings source `main @ 4ea4eac` / `2026.9.14.1`, dated 2026-09-16.
> "Read site" = a place in the source that really calls `getenv` / `get_env_or_default`;
> variables that are only **written** are listed separately.
> **Exactly one variable was added since the previous baseline**: `XLINGS_DOCTOR_CHILD_TIMEOUT`
> (2026.9.12.1) — a whole-tree diff of environment-variable names turned up nothing else.
> **Refresh 2026-09-23 (`main @ 84572b0`, 2026.9.20.1)**: 2026.9.16.1 added three network-bound variables -
> `XLINGS_UPDATE_TIMEOUT`, `XLINGS_INDEX_HTTP_TIMEOUT`, `XLINGS_GIT_NETWORK_TIMEOUT` - and xlings now **sets**
> `GIT_TERMINAL_PROMPT=0`, `GIT_HTTP_LOW_SPEED_LIMIT` and `GIT_HTTP_LOW_SPEED_TIME` for git when the operator has not
> (rows at the end of §3). 2026.9.20.1 added none. Line numbers in the older rows are from `4ea4eac`.

## 0. The three most important conclusions

1. **`XLINGS_BIN` is never read.** Zero `getenv("XLINGS_BIN")` in the whole codebase. It is a
   **pure output variable**: xlings writes it for the shell / child processes, and the shell
   profile **re-derives** it from `XLINGS_HOME` + `XLINGS_ACTIVE_SUBOS`.
   => `env -u XLINGS_BIN` has zero effect on the behavior of xlings **or of mcpp**.
2. **`XLINGS_HOME` is the only variable that really decides the path root**, with a four-level
   fallback; once stripped it lands on `$HOME/.xlings` **or on the self-contained probe result**.
3. **`src/main.cpp:65` writes `XLINGS_HOME` back unconditionally.** After main, any
   `getenv("XLINGS_HOME")` reads **the value xlings computed itself**, not what the caller
   passed. The source added an `ambient_home_env()` snapshot for exactly this
   (`config.cpp:17-23`).

## 1. `XLINGS_HOME` in depth

**Read sites**:

| file:line | how | purpose |
|---|---|---|
| `src/core/config.cpp:21` | `std::getenv` | `capture_ambient_home_env()` — snapshot of "the value the caller passed", first-call-wins |
| `src/core/config.cpp:491` | `utils::get_env_or_default` | **the `Config` constructor**, main path resolution |
| `src/core/xvm/shim.cpp:149` | `env_or_empty` | **hop 2** of shim owner-anchoring (deprecated fallback; it warns, `:174-179`) |
| `src/core/xself/install.cpp:204` | `utils::get_env_or_default` | `detect_existing_home()` |
| `src/core/xself/install.cpp:472-478` | **`xlings::ambient_home_env()` (not getenv)** | `explicit_home_()` — self install conflict guard, must see "what the user passed" |
| `src/core/xvm/db.cpp:680` | dynamic `getenv(name)` | evaluates any `${XLINGS_*}` inside alias text |

**Downstream paths**: `dataDir = homeDir/"data"`; `subosDir = resolve_subos_scope_()`;
`binDir = subosDir/"bin"`; `libDir = subosDir/"lib"`.
`resolve_subos_scope_()` priority (`config.cpp:458-477`): `activeSubosOverride_` (explicit
in-process override) > project Named/Anonymous (unless `-g`) > env `XLINGS_ACTIVE_SUBOS` >
`globalActiveSubos_`; the root is always `homeDir/"subos"/<name>`.
Two things now set the override: `subos new --runtime` as before, and **`self doctor --subos <NAME>`
(2026.9.12.1), which sets both the override and `XLINGS_ACTIVE_SUBOS`** so that every subcommand the
run spawns agrees with it (`src/core/xself/doctor.cpp:5047-5074`).
> Source note: there used to be **two mutually contradictory implementations** here, diverging
> on exactly one case, `xlings install -g` (run inside a project), which installed into one
> subos and cleaned up another.

**Written / passed to child processes**:

| file:line | how | to whom |
|---|---|---|
| `src/main.cpp:65` | `set_env_variable` | **unconditional, every run**. Every later child process (hook, `os.execute`, shim exec, shell) inherits the resolved value |
| `src/core/subos/sandbox.cpp:927` | `set_env_variable` | the shell inside the bwrap/proot sandbox (the comment requires the spelling to match the outside exactly, otherwise the shim warns about conflicting with itself) |
| `src/core/xself/install.cpp:893` | `set_env_variable` | the patchelf child process run after Linux `self install` |
| `src/core/xself/install.cpp:373` | PowerShell `[Environment]::SetEnvironmentVariable(...,'User')` | **persisted into the Windows user environment** |
| `src/core/xself/profile_resources.cppm:79,148,203` | shell profile `export` | bash/zsh, fish, pwsh |

**What happens once it is stripped**: fallback 3 -> 4 takes over; **if the binary sits under
some self-contained layout, home silently becomes that root**; `explicit_home_()` of
`self install` returns empty (`install.cpp:474`) and the conflict guard does not fire — which is
precisely why it uses `ambient_home_env()` rather than `getenv` (the comment records the
original bug: a caller doing `env -u XLINGS_HOME` was hit by the value xlings itself had
written). The shim call path is unaffected: hop 1 is the owner home (`shim.cpp:157-166`).

`get_home_dir()` reads the environment too: Linux/macOS read `HOME`
(`modules/platform/src/platform/linux.cpp:155`, `macos.cpp:133`), Windows reads `USERPROFILE`
(`windows.cpp:145`); both return `"."` on failure.
WARNING: **when `HOME` and `XLINGS_HOME` are stripped at the same time, home on Linux becomes
`./.xlings` (relative to cwd).**

## 2. `XLINGS_BIN` in depth

- **Read sites: none.**
- **Derivation formula (shell side, not C++)**: bash/zsh `profile_resources.cppm:87` --
  `XLINGS_BIN="$XLINGS_HOME/subos/${XLINGS_ACTIVE_SUBOS:-current}/bin"`; fish `:152,155`;
  pwsh `:207`.
- **C++-side write formula**: `bin_dir = p.homeDir/"subos"/name/"bin"`, **derived entirely from
  `homeDir` + the subos name, carrying no independent information**.
- **Write sites**: `subos.cpp:1348` (the child shell spawned by `subos use`; the comment at
  `:1344-1347` calls it "**mostly defensive**", only there to cover `--norc` not sourcing the
  profile); `:1226/1249/1275` (eval output for `--shell fish/pwsh/POSIX`); profile
  `:88,152,155,207`.
- **The only consumers are on the shell side**: the profile uses it for the PATH dedup test
  (`profile_resources.cppm:97-98,159-160`). The code explicitly **refuses** to derive the
  lib directory as `XLINGS_BIN + "/../lib"`, declaring `XLINGS_SUBOS_LIB` separately
  (`:69`, `subos.cpp:1359`: "true by layout, not by promise").
- **Once stripped**: nothing happens inside the xlings process. The one observable side effect:
  if the profile is re-sourced right afterwards, the PATH dedup test
  `case ":$PATH:" in *":$XLINGS_BIN:"*)` degrades to matching `"::"` because the variable is
  empty, which can prepend PATH **one extra time**.

## 3. Full table of xlings' own variables (`XLINGS_*`)

| Variable | Role | Default / unset | Read site |
|---|---|---|---|
| `XLINGS_HOME` | see §1 | 4-level fallback | §1 |
| `XLINGS_BIN` | see §2 | — (**never read**) | **none** |
| `XLINGS_ACTIVE_SUBOS` | selects the current subos (per-shell override) | empty -> `globalActiveSubos_` (`activeSubos` in `.xlings.json`, then default `current`) | `config.cpp:358,475`; also **written** by `self doctor --subos` (`doctor.cpp:5071-5072`, env var + in-process override) |
| `XLINGS_PROJECT_DIR` | last resort for project mode (after the cwd walk-up fails; **it also does the `subos/` boundary check**) | empty -> cwd walk-up only | `config.cpp:785` (written `:651`) |
| `XLINGS_SUBOS_LIB` | subos library farm path (explicit contract: `-rpath-link` for the binutils `ld` wrapper, mcpp pack-time strip). **This is also the variable that is actually exported inside `subos use --sandbox`** — `XLINGS_SUBOS` is not, and a sandbox probe keyed on that name silently never fires | if not declared, consumers silently stop working | written `sandbox.cpp:735`, profile `profile_resources.cppm:93,153,156`; read indirectly via `db.cpp:680` |
| `XLINGS_SUBOS_MODE` | `sandbox` = already inside the sandbox | empty = not sandboxed | `sandbox.cpp:678` (**refuses nested entry**), written `:730`; also drives the prompt-bracket flip in the profiles (`profile_resources.cppm:120,175,226`) |
| `XLINGS_DYNAMIC_SUBOS_DIR` | **placeholder** (`kSubosPlaceholder`, `db.cppm:303-304`), **not a real environment variable** | no subos resolved -> error | `db.cpp:680` |
| `XLINGS_SHIM_ANCHOR` | `0`/`legacy`/`off` -> fall back to the pre-0.4.48 env-first shim dispatch | empty -> owner-anchored | `shim.cpp:142` (inside `resolve_dispatch_home`, `:133-134`) |
| `XLINGS_SHIM_DEPTH` | recursion depth guard, `>=10` errors, `>=8` takes the alias full-path fallback | unset -> 0 | `shim.cpp` (+1 before exec, including before the 2026.9.3.1 **host passthrough** at `:622`) |
| `XLINGS_THEME` | `dark`/`light` forces it; `auto`/unknown -> OSC-11 probe | unset -> probe -> `COLORFGBG` -> `Dark` | `palette.cppm:109` |
| `XLINGS_TERM_WIDTH` | overrides terminal width detection; `0` = no width limit | invalid/unset -> ftxui probe, non-tty -> nullopt | `src/ui/layout.cppm:65` |
| `XLINGS_TERM_QUERY_TIMEOUT_MS` | deadline for the OSC-11 background color query | 500ms, clamped to `[50,5000]` | `modules/platform/src/platform/unix.cpp:90` |
| `XLINGS_SHELL` | forces the shell candidate (**the only candidate**) | unset -> Win: `pwsh/powershell/cmd`; macOS: `$SHELL` or `/bin/zsh`; Linux: `$SHELL` or `/bin/sh` | `modules/platform/src/platform.cpp:207` |
| `XLINGS_NO_LOCK` | `=1` skips the state lock (**diagnostics only**) | unset -> lock | `xvm/lock.cpp:96` |
| `XLINGS_LOCK_TIMEOUT` | lock wait timeout (seconds) for waiting on **another** xlings | see `lock.cpp:85` | `xvm/lock.cpp:85`. WARNING: **temporarily cleared** by `rmw_home_config_locked_` (`config.cpp:1320`) for its own 2-second acquisition and restored right after — otherwise a passive version-stamp write would inherit a ten-minute wait meant for a long install. Upstream openxlings/xlings#594 notes it is restored as **empty rather than unset**; no observable effect today |
| **`XLINGS_DOCTOR_CHILD_TIMEOUT`** | **(new in 2026.9.12.1)** seconds a single `self doctor --fix --subos <name>` child may run before the parent gives up; **`0` disables the bound** (wait forever, the pre-existing behaviour). A non-numeric value falls back to the default | unset -> **1800** (30 min) | `xself/doctor.cpp:3220-3237`. WARNING: the bound is applied **only when `timeout(1)` is found on PATH** — `have_timeout_tool_()` runs `command -v timeout` once per process (`:3249-3255`). It is **not** a POSIX-vs-Windows split: on **stock macOS (ships none)** and **minimal/distroless CI containers** the child runs completely **unbounded** and the parent hangs, which is exactly the failure this variable exists to bound (upstream says so at `:3242-3248`; openxlings/xlings#592 covers the Windows half). => In a slim image, wrap the whole `xlings self doctor --fix` in your own `timeout` |
| `XLINGS_STATE_LOCK_HELD` | reentrancy marker | empty -> not reentrant | `xvm/lock.cpp:107` (written `:166`, restored by the destructor `:224`) |
| `XLINGS_INDEX_SOURCE` | `git`/`artifact`/`auto`; `=git` also opts out of the "refuse to clone over an artifact-managed tree" guard | `auto` | `xim/repo.cpp:229,562` |
| `XLINGS_INDEX_REPO` | index artifact repo name | `"xim-index"` | `xim/indexfetch.cpp:20` |
| `XLINGS_INDEX_TAG` | index artifact tag | `"latest"` | `xim/indexfetch.cpp:25` |
| `XLINGS_INDEX_BASE_URL` | overrides the index base (supports `file://` and bare local paths) | empty -> `Config::index_base()` (`xim.index-base`), then empty | `xim/indexfetch.cpp:83` |
| `XLINGS_INDEX_PIN` | pins the index snapshot; **overrides the per-repo pin** | empty -> use the repo's own pin | `xim/indexfetch.cpp:537` (`xself/update.cpp:33,55` sets `"newest"`, clears it at `:35,57`) |
| `XLINGS_MIRROR_FALLBACK` | `off`/`force`/`auto` proxy fallback mode | unset -> read `mirror_fallback` from `.xlings.json`, then default `Auto` | `mirror/expand.cpp:36` |
| `XLINGS_ADAPTIVE_MIRROR` | `off`/`0` disables latency-probe reordering | unset -> enabled | `mirror/adaptive.cpp:56` |
| `XLINGS_INSTALL_MIRROR` / `XLINGS_MIRROR` / `XLINGS_RELEASE_MIRROR` | mirror region for `self install` (first non-empty wins, in that order) | all empty -> latency probe | `xself/install.cpp:58-59`. WARNING: **not read at runtime; only written into `.xlings.json` at `self install` time** |
| `XLINGS_DOWNLOAD_LOW_SPEED` | `off`/`0` disables the low-speed watchdog; `<bytes>:<secs>` tunes it | unset -> use the caller's limit/window | `modules/tinyhttps/src/tinyhttps.cpp:97` |
| `XLINGS_COMPACT_GIT_BIN` | overrides the git executable | empty -> `"git"` | `core/compact/git.cppm:56` |
| `XLINGS_COMPACT_GIT_BOOTSTRAP` | recursion guard | unset -> bootstrap allowed | `git.cppm:121` (written `:139`, restored `:147`) |
| `XLINGS_COMPACT_INSTALL_TARGET` | the current install target; bootstrap is disabled for `xim:git`/`git` | empty | `git.cppm:116` (written `:140`, restored `:148`) |
| `XLINGS_NO_AUTO_INSTALL_GIT` | `=1` disables automatic git installation | unset -> allowed | `core/compact/git.cpp:34` |
| `XLINGS_BUILDDEP_<UPPER>_PATH` | install directory of each build_dep, injected into install hooks | not set when there is no such dep | **xlings does not read it** (it is for the xpkg-side `pkginfo.build_dep()`); written `installer.cpp:3044-3071`, cleared when the hook ends |
| any `${XLINGS_*}` | the shim checks whether alias/env text would expand to empty | expands to empty -> refuses to execute and errors | `xvm/db.cpp:680` (dynamic `getenv`) |
| **`XLINGS_UPDATE_TIMEOUT`** | **(2026.9.16.1)** total budget of one `xlings update`, seconds; `off`/`0` = unbounded; unparsable -> default. Past it, remaining sources are skipped with a warning and keep their local copy | **300** | `xim/repo.cpp:630-656` at `84572b0` |
| **`XLINGS_INDEX_HTTP_TIMEOUT`** | **(2026.9.16.1)** index HTTP `<connectSec>:<maxSec>`; `off` = the ordinary download defaults | **`10:120`** | `xim/indexfetch.cpp:54-57` |
| **`XLINGS_GIT_NETWORK_TIMEOUT`** | **(2026.9.16.1)** git low-speed window (written into `GIT_HTTP_LOW_SPEED_TIME`, with `GIT_HTTP_LOW_SPEED_LIMIT=1000`); `off`/`0` = do not set | **60** | `core/compact/git.cppm:131-140` |
| `GIT_TERMINAL_PROMPT` / `GIT_HTTP_LOW_SPEED_LIMIT` / `GIT_HTTP_LOW_SPEED_TIME` | **written** by xlings for its git children (2026.9.16.1): prompt `0`, limit `1000`, time from the row above. **An operator-set value is never overwritten** - which also means a stale `GIT_HTTP_LOW_SPEED_TIME` in your shell silently replaces xlings' bound | only set when empty | `core/compact/git.cppm:137-140` |

## 4. mcpp-side variables related to xlings (cross-tool)

| Variable | Who reads it | Evidence | Consequence |
|---|---|---|---|
| `MCPP_VENDORED_XLINGS` | **mcpp, all platforms** | `mcpp/src/fallback/xlings_binary.cppm:107` (first in the acquisition chain), `:219` (candidate version probing); `mcpp/src/config.cppm:127` (used directly on Windows) | if it is left over in the environment, mcpp **copies that binary into the sandbox**, overwriting the vendored xlings |
| `MCPP_HOME` | mcpp | `mcpp/src/home.cppm` (resolution: `root()`/`cache_root()`/`legacy_bmi_root()` — it contains no occurrence of "registry"); `mcpp/src/config.cppm:67` declares `registryDir`, assigned at `:618` | decides `registryDir = mcppHome/"registry"`, i.e. the home mcpp passes to xlings. **Also where the `[xlings] deps` provisioning stamp now lives**: `$MCPP_HOME/provisioned/xlings-deps-<16 hex>` (`mcpp/src/build/prepare.cppm:1469-1484`), moved out of `<project>/.mcpp/` so that wiping the home really does un-provision |
| `XLINGS_HOME` | **mcpp never reads it** | zero hits for `getenv("XLINGS...")` across the tree | mcpp **sets it explicitly** every time |
| `XLINGS_SUBOS_LD_PATHS=0` | mcpp **sets** it for every child process | `mcpp/src/cli.cppm` | refuses the xlings linker wrapper injecting `-rpath "$XLINGS_SUBOS_LIB"` (that points at the **active shell's** SubOS; inheriting it would put a second libc on the artifact search path) |
| `XLINGS_PROJECT_DIR` | mcpp **sets it or `-u`s it depending on the scenario** | `mcpp/src/xlings/xlings.cppm:275-282` | the `[xlings] deps` supply **deliberately does not set it** (goes global, see SKILL §9) |

WARNING: **`MCPP_INDEX_MIRROR` is read by neither side**: zero hits across the mcpp source
tree, and the name does not exist in xlings at all. Setting it is a no-op.

## 5. Proxy / network / color / locale

**Proxy** (`modules/tinyhttps/src/tinyhttps.cpp:52-73`, **each name is tried once in upper and
once in lower case, uppercase first**):

| Variable | Role | Order |
|---|---|---|
| `NO_PROXY` / `no_proxy` | exemption list (supports `*`, a leading `.`, and suffix matching); on a hit it returns an empty proxy immediately | 1 (first, `:62-64`) |
| `HTTPS_PROXY` / `https_proxy` | used when the url starts with `https://` | 2 (`:68`) |
| `HTTP_PROXY` / `http_proxy` | used otherwise | 2 (`:70`) |
| `ALL_PROXY` / `all_proxy` | fallback when neither of the first two is set | 3 (`:72`) |

**Color / TTY**: `NO_COLOR` (**only takes effect when present and non-empty** — `NO_COLOR=`, the
empty string, means "clear the inherited value" and is not an opt-out,
`core/palette.cppm:48-50`); `TERM` (turns color off **only when `== "dumb"`**, `:52`);
`COLORFGBG` (rxvt-style `fg;bg`, a bg of `7` or `9..15` means light, `:119-131`).
`NO_COLOR` deliberately does **not** participate in `cursor_rewrite_allowed` (`:60-72`: it only
requires no color, not the absence of cursor control).
UI mode detection (`core/uimode.cppm:76-85`) **only looks at whether stdout/stdin are TTYs plus
`colorAllowed`, and reads no env at all**.

**locale / i18n** (`modules/platform/src/platform.cpp:117`): POSIX order, first non-empty of
`LC_ALL` -> `LC_MESSAGES` -> `LANG`; unset / `"C"` / `"POSIX"` -> `"en"` (`:121`); otherwise
truncated before `_ - . @` and lowercased (`:124-130`), e.g. `zh_CN.UTF-8` -> `zh`. Windows goes
through `user_ui_language()` (`:113`). The comment at `:89-107` records why `std::locale("")` is
not used: **it always throws under a static musl build**. `Config::lang()` wins; only when it is
empty or `"auto"` does it fall back to system detection (`xself/config.cpp:54-58`).

**System / platform variables** (the important ones): `PATH`; `HOME`/`USERPROFILE`;
`USER`/`USERNAME` (username inside the sandbox, empty -> `"user"`, `sandbox.cpp:696,699`);
`SHELL`; `SUDO_UID`/`SUDO_GID`/`SUDO_USER` (identify the sudo caller so files can be chowned back
to the real user, `platform.cpp:30,31,39`); `TMPDIR`/`TEMP`/`TMP`;
`XDG_*` (**written only, never read**; sandbox redirection `sandbox.cpp:1014-1017,1052-1054`);
`APPDATA`/`LOCALAPPDATA`; `PROOT_NO_SECCOMP` (only written as `="1"`, `sandbox.cpp:950`);
`GIT_SSL_CAINFO` (pins a CA bundle for the static git, **left completely alone if the user or CI
already set it**, `git.cppm:101`, written `:109`).

## 6. Names that explicitly do not exist (avoid false positives)

| Name | Status |
|---|---|
| `XLINGS_RES` | **Not an environment variable.** It is a JSON key in `.xlings.json` (`config.cpp:219`) plus a sentinel string in package recipes |
| `CI` / `GITHUB_ACTIONS` / `TF_BUILD` | **No CI-detection getenv at all.** CI behavior differences all come from `isatty` (`install.cpp:607` comment "no TTY in CI"). `RUNNER_TEMP` is only one of the candidate temp-dir prefixes (`:167`) |
| `XLINGS_PROXY_CN_DIRECT` | Design notes only, not implemented in code |
| `XLINGS_INDEX_ARTIFACT_URL` | Design notes only; the real one is `XLINGS_INDEX_BASE_URL` |
| `XLINGS_GPU_EXTRA_DEVS` | Design notes only, not implemented |
| `XIM_PKGINDEX_DIR` | Read only by test code (`tests/unit/test_core_basics.cpp:85`), no reference in production code |
| `XLINGS_SHIM_HOME` | Explicitly decided against: the shim owner-anchoring design deliberately does not provide it |
| `TERM_PROGRAM` / `COLORTERM` | Not read |
| `MCPP_INDEX_MIRROR` | Read by neither xlings nor mcpp; a no-op (re-verified: zero hits in the mcpp tree) |
| `XLINGS_SUBOS` | **Not exported anywhere**, including inside `subos use --sandbox` — but it **is printed as a display label** (value = the subos dir) by `xlings self config` (`src/core/xself/config.cpp:20`) and by the `system_status` capability (`src/capabilities.cpp:239`), and upstream's own comment there calls those three labels "environment variable names" (`config.cpp:24-26`). **That output is where the false belief comes from**; an agent scraping it will key on a name no `getenv` ever reads. Upstream's own 2026.9.5.1 verification pass wrote a sandbox probe against this name and it silently never fired. The sandbox exports **`XLINGS_SUBOS_LIB`**; the "am I nested" variable xlings reads is `XLINGS_SUBOS_MODE` |

## 7. Used only by the installer scripts (not inside the binary)

`tools/other/quick_install.sh`: `XLINGS_GITHUB_MIRROR` (`:28`), `XLINGS_VERSION` (`:45`),
`XLINGS_BASE_URL` (`:48`), `XLINGS_CURL_CONNECT_TIMEOUT` (`:36`, default 8),
`XLINGS_CURL_MAX_TIME` (`:37`, default 25), `XLINGS_NON_INTERACTIVE` (`:374`).
The PowerShell version uses the same names (`quick_install.ps1:6,25,143`).
`tools/package_xim_index.sh`/`.ps1`: `XLINGS_RELEASE_MIRROR`, `XLINGS_RELEASE_PKGINDEX_REF`,
`XLINGS_RELEASE_PKGINDEX_URL`.

## 8. Isolation recipe cheat sheet

```bash
# Bare xlings call: the five-piece strip plus a clean CWD
env -u XLINGS_HOME -u XLINGS_BIN -u XLINGS_PROJECT_DIR -u XLINGS_ACTIVE_SUBOS \
    -u MCPP_VENDORED_XLINGS XLINGS_HOME=<isolated home> <xlings> ...

# Through mcpp: the only one that actually matters is MCPP_HOME
env -u XLINGS_HOME -u XLINGS_BIN MCPP_HOME="$PWD/.mcpp" .mcpp/bin/mcpp ...
```

WARNING: stripping the environment **does not block** two paths: mcpp's `$HOME` fallback
whole-copy (only changing `HOME` stops it) and the `.xlings.json` cwd walk-up.
See SKILL §1.2.
