# Reference: xlings command surface

> Source of truth: `root()` in `src/cli/spec.cpp` (**the only command-tree source of truth**),
> baseline source `main @ 4ea4eac` / `2026.9.14.1`, dated 2026-09-16. Line numbers come from actual
> `grep -n` / `sed -n` output, and every option list below was cross-checked against
> `xlings <command> --help` on the released 2026.9.14.1 binary. Behavioural assertions are always
> taken from the corresponding `.cpp` implementation, never from `docs/` (rationale in SKILL §0).
> Refresh 2026-09-23: `src/cli/spec.cpp` and `src/cli.cpp` are **unchanged** between `4ea4eac` and `84572b0`
> (2026.9.20.1), so every flag table below still holds; only the `self update` and `index list` notes changed
> behaviour, and they are marked with their version.
> Flags that arrived after the previous baseline are marked **(new in `<ver>`)**; the reasons are in
> `version-notes.md`.

## 0. Two-layer parse architecture (know this before scripting)

xlings handles argv along **two separate paths**:

| Path | Commands covered | Implementation |
|---|---|---|
| **Hand-written positional dispatch** | `agent` / `index` / `subos` / `self` / `profile` / `script` | `src/cli.cpp:1457` (agent), `:1531` (index), `:1562-1572` (subos/self/profile validate against the spec first), `:1589-1591` (dispatch) |
| **`cmdline::App` builder** | `install remove update search list info why use config interface` | `src/cli.cpp:1629-1880` |

**The declarative spec is the shared source of truth for both** (`src/cli/spec.cpp:8-79`): `--help`
is rendered from it (`src/cli.cpp:1444-1447`); `docs/generated/command-reference.md` is generated
from it (hidden flag `--command-reference-json`, `src/cli.cpp:1190`); the hand-written
dispatch path validates argv against it first (`spec::validate_manual_argv`,
`src/cli/spec.cpp:241-246`, called at `src/cli.cpp:1536,1567`).
Everything is wrapped by `run()`, which does nothing but `try`/`catch` around `dispatch_()`
(`:1188`) — the split exists because `subos` / `self` / `profile` used to be dispatched **above** the
top-level handler, so a throw there killed the process with `SIGABRT` after printing a full report
(fixed in 2026.9.4.1).

**Bidirectional parity test** (`tests/scripts/test_cli_spec_parity.py:1-23`) keeps the spec from
drifting away from the real parser: forward = every (command path, option) the spec publishes is
fed to the real process and must not produce a parse-level diagnostic; reverse = every option
literal compared inside the hand-written argv loops must exist in the spec.
WARNING: reverse only checks option literals, not positional shorthands — that is how
`xlings agent <name>` escapes it.

After `app.run` succeeds, the action's rc is returned (`src/cli.cpp:1629-1635,1886-1900`):
`cmdline::App` drops the action's int return value into a `std::function<void(...)>` and swallows
it, so a shared `action_rc` fishes it back out; otherwise a failing `xlings install` would be
squashed to 0 in CI.

## 1. Global options (`spec.cpp:13-19`)

Those marked `global=true` are legal on **every** command, and are **ignored** where they do not
apply (not exit 2):

| Option | Meaning | global |
|---|---|---|
| `-y, --yes` | skip confirmation prompts | yes |
| `--agent` | stable plain-text output (ANSI off, does **not** set tui_mode) | yes |
| `-v, --verbose` | verbose output | yes |
| `-q, --quiet` | suppress non-essential output | yes |
| `--ui-mode <MODE>` | frontend for this run (`cli`/`tui`/`auto`) | yes |
| `-h, --help` | show help for the selected command | no — **it is itself a command** |
| `--version` | show version | no — same |

Design rationale (`spec.cppm:16-24`): global options are accepted by every command rather than
only by the one that lists them, because `xlings --help` advertises them unconditionally, and an
agent told to "always pass `--yes`" will add it to commands that have nothing to confirm;
rejecting those spellings (exit 2) would turn a documented spelling into a trap.
WARNING: **that trap is live today, for `-y/--yes` only, and only before the subcommand.** The spec
declares it global, but the implementation's strip loop [src/cli.cpp:1400-1402] filters
`--verbose/-v`, `--quiet/-q`, `--agent` and `--ui-mode` — **not `-y`/`--yes`**. So `-y` survives into
the filtered argv that the positional handlers read, and `xlings -y subos list` /
`xlings --yes profile list` / `xlings -y index list` / `xlings -y self <sub>` each exit **2** with
``unknown subcommand for `xlings <group>`: <group>``, while the same commands without `-y`, or with it
trailing (`xlings subos list -y`), exit 0. **`script` and `agent` are on the same positional path and are
equally broken, with worse symptoms**: neither reaches `spec::validate_manual_argv` (`agent` dispatches
at `:1457`, before the validate blocks at `:1531`/`:1562`), so instead of the clean "unknown subcommand"
they exit **1** naming the wrong thing — `xlings -y script` takes `fargv[2]` as the filename [`:1598`] ->
`[error] failed to load script: package file not found: script`, and `xlings -y agent` takes `argv[2]` as
the subcommand [`src/agent/agent.cpp:63`] -> `Unknown: xlings agent agent` [both measured, 2026.9.14.1].
The other four globals are fine in that slot
(`xlings -v|--agent|--ui-mode cli subos list` -> 0). Worth an upstream issue.
But `-h`/`--version` are **not** global: accepting them mid-command would make
`xlings subos new foo --version` **silently create a subos**.

## 2. The 16 top-level commands (`spec.cpp:22-75`)

| Command | Arguments | Own options | spec line |
|---|---|---|---|
| `install` | `[packages]...` (variadic) | `-g, --global`; `-u, --use` | `:22-23` |
| `remove` | `<package> [version]` | `-g, --global`; `--force`; **(new in 2026.9.12.1)** `--all`; `--all-subos`; `--subos <NAME>` | `:24-29` |
| `update` | `[package] [version]` | — | `:30` |
| `search` | `<keyword>` | — | `:31` |
| `list` | `[filter]` | `-a, --all` | `:32-33` |
| `info` | `<package> [version]` | `--all-versions` | `:34-35` |
| `why` | `<package> [dep]` | — | `:36-37` |
| `use` | `<target> [version]` | `-a, --all`; `--strict` | `:38-39` |
| `config` | — | `--lang <LANG>`; `--mirror <MIRROR>`; `--ui-mode <MODE>`; `--theme <THEME>`; `--interactive <BOOL>`; `--add-xpkg <FILE>`; **(new in 2026.9.12.1)** `--list-xpkg`; `--remove-xpkg <NAME>`; `--clear-xpkg <all\|stale>`; `--index-repo <NS:URL>` | `:40-41` |
| `subos` | — | §3 | `:42-50` |
| `self` | — | §4 | `:51-60` |
| `script` | `<script-file> [args]...` | — | `:61` |
| `interface` | `[capability]` | `--args <JSON>`; `--args-file <PATH>`; `--list`; `--version` | `:62` |
| `index` | — | §5 | `:63-67` |
| `agent` | — | §6 | `:68-70` |
| `profile` | — | §7 | `:71-75` |

### Behavioural points (evidence from the implementation)

- **`install` with no package name = project mode** (`src/cli.cpp:1684` ->
  `install_from_project_config_`, defined at `:536`): walks **upward level by level** from cwd
  looking for `.xlings.json`, reads `workspace` -> `Config::workspace_install_targets` -> installs
  with `yes=true, useAfterInstall=true`. The upward walk **skips the XLINGS_HOME directory
  itself**, but has **no `subos/` boundary detection** and **never checks `projectScope`**.
  Fallback: if a legacy `config.xlings` (Lua) is found, it **auto-generates `.xlings.json`** and
  then installs. If nothing is found, it prints a hint and **exits 0**.
- **`install` multi-package semantics + heuristic warning**: each positional is an independent
  package; if there are exactly two arguments and the first contains no `@` while the second looks
  like a version number or is `latest`, it warns "did you mean `a@b`".
- **`remove --force` is separate from `-y`** (`:1718-1722` carries the reasoning verbatim). Since
  2026.9.12.1 `--force` also covers "the recipe is gone" and "the uninstall hook throws"; see
  SKILL §1.6 for what it still does not override.
- **`remove` scope flags** (`:1725-1734`): `--subos <NAME>` maps to that name, `--all-subos` maps to
  the wildcard `"*"`, neither means the current subos (`nullopt`); **`--subos` wins if both are
  given**. `--all` is orthogonal and means every installed version.
- **`use <name>` without a version is always a "list"**. It only switches when a version is given,
  or when the user picks from the inline selector opened by `xlings config --interactive true`.
  Giving `a@b` and a separate version at the same time reports ambiguous.
- **`config` enum-typed settings print the candidates instead of erroring when the value is
  omitted** (`:620-631` comment): the value space of `--theme`/`--lang`/`--mirror`/`--ui-mode`/
  `--interactive` is short, so a supplied value is applied and an omitted value makes the list the
  answer (a selector when a human can be asked, print + non-zero exit when not). Implemented with
  the sentinel `kValueOmitted = "\x01omitted"` (`:632`), injected by `inject_omitted_values_`
  (option list at `:1171`, sentinel push at `:1183`).
  WARNING: `--mirror` **and `--lang`** are the two with **no value-validation branch** — a supplied
  value is written verbatim and exits 0 (`--lang` arm `:712-726`, `--mirror` arm `:729-743`, the same
  shape byte for byte; `xlings config --lang bogus` -> `lang = bogus`, **0**). Only
  `--ui-mode`/`--theme`/`--interactive` reject a bad value (`diag::emit` + `return 2` at `:770`,
  `:840`, `:868`). See SKILL §1.4 for the silent-fallback trap this opens on `mirror`; the same trap
  applies to `lang`.
- **`config` overlay verbs** (new in 2026.9.12.1, `spec.cpp:40`; implementation
  `src/core/xim/commands.cpp:2335` list, `:2377` remove, `:2409` clear): `--list-xpkg` prints
  name / version / status / source, where status is `unique|identical|modified|behind|missing`;
  `--clear-xpkg` takes `all` or `stale` and **exits 2** on any other word. These read and write
  `<global data dir>/xim-pkgindex-local`, the directory `--add-xpkg` has always written to.
  See SKILL §5.4 — `xlings update` also deletes from it now.

## 3. `xlings subos` (`spec.cpp:42-50`; implementation `src/core/subos.cpp:1680+`)

| Subcommand | Alias | Arguments | Options |
|---|---|---|---|
| `new` | — | `<name>` | `--storage <MODE>`; `--image-size <SIZE>`; `--from <SOURCE>`; `--runtime <SPEC>` |
| `use` | — | `[name]` (omitted = list candidates) | `--global`; `--shell [KIND]`; `--sandbox [BACKEND]`; `--cmd <COMMAND>`; `--keep`; `--no-keep`; `--ttl <SECONDS>`; `--gpu` |
| `list` | `ls` | — | — |
| `remove` | `rm` | `<name>` | — |
| `info` | `i` | `[name]` | — |
| `stop` | — | `<name>` | — |
| `runtime` | — | `<binding> [name]` | — |

Alias normalisation is at `src/core/subos.cpp:1698-1700`. WARNING:
`docs/generated/command-reference.md` does **not** render aliases.
There is **no `fork` / `exec` / `shell` subcommand.**

**`subos new` details** (`:1720-1770`): `--storage` is one of `shared` (default)/`tmpfs`/`image`;
an invalid value reports `unknown storage mode` (`:1741`); `--image-size` defaults to `"50G"`;
a `--from <spec>` containing `:` or `@` is treated as a pkg-spec (the base xpkg is installed
automatically when missing), a bare name is treated as a local subos to fork (`:1749` ->
`new_from` `:937`); `--runtime` (e.g. `glibc@2.39`) is a **creation-time** attribute, because
changing it afterwards would invalidate every installed payload (`:1729`).
**`--opt=value` is NOT uniform across the four options**: only `--runtime` and `--from` have an
`rfind("--x=",0)==0` branch (`:1732`, `:1752`); `--storage` (`:1735`) and `--image-size` (`:1746`) are
**space-form only**, and `--storage=image` is rejected as ``unknown option for `xlings subos new`:
--storage=image``, **exit 1**, with no subos created. On `subos use`, **three** options take the `=`
form — `--shell=` (`:1822`), `--cmd=` (`:1840`) and `--ttl=` (`:1861`); `--global`/`--sandbox`/`--keep`/
`--no-keep`/`--gpu` do not, and `--sandbox=bwrap` / `--gpu=1` are rejected as ``unknown option for
`xlings subos use```, **exit 1** [measured, 2026.9.14.1]. Five `rfind("--x=",0)==0` branches exist in
the file in total (`grep -n 'rfind("--' src/core/subos.cpp`: `:1732`, `:1752`, `:1822`, `:1840`, `:1861`).

**`subos use` details** (`:1788-1875`; the comments there are the spec):
- no flag: spawn a new interactive shell carrying `XLINGS_ACTIVE_SUBOS=<name>` in the environment,
  **per shell**.
- `--global`: persist to `~/.xlings.json` + symlink, affecting every shell (legacy behaviour).
- `--shell <kind>`: emit shell code on stdout for eval/Invoke-Expression; kind is one of
  `{sh,bash,zsh,fish,pwsh}`, default `sh`.
- `--sandbox [bwrap|proot]`: Linux filesystem isolation; `$HOME`, `/tmp`, `/etc/passwd` are
  private to the sandbox, while `~/.xlings`, `/usr`, `/lib*`,
  `/etc/{resolv.conf,ld.so.cache}` are bound from the host. The prompt changes from
  `[xsubos:<name>]` to `<xsubos:<name>>`. The backend accepts only the literals `bwrap`/`proot`
  (`:1826-1836`).
  WARNING: inside the sandbox, the variable that is exported is **`XLINGS_SUBOS_LIB`**, not
  `XLINGS_SUBOS`. A "am I sandboxed" check keyed on `XLINGS_SUBOS` silently never fires; the
  variable xlings itself reads for nested-entry refusal is `XLINGS_SUBOS_MODE=sandbox`.
- `--cmd <string>`: run one command non-interactively and **exit with that command's exit code**;
  routed internally to `sh -c` (POSIX) or `pwsh -Command` / `cmd /c` (Windows).
- keeper: `--no-keep` forces it off; `--keep` never expires; `--ttl <sec>` sets a custom idle TTL.
  The automatic default (storage=image|tmpfs + sandbox + Linux -> on, TTL 5 minutes) is encoded in
  `keeper::should_auto_keeper`.
- `--gpu`: opt-in NVIDIA + DRM device passthrough, **bwrap only**; missing devices are skipped
  silently; ignored under proot (proot already passes `/dev` and `/sys` through wholesale).

**What the shell profile actually does** (`:1272-1290`, POSIX branch):
```sh
export XLINGS_ACTIVE_SUBOS="<name>"; export XLINGS_BIN="<home>/subos/<name>/bin";
export PATH="<new PATH>";   # rebuild_path_for_subos_: strip every <home>/subos/*/bin segment, then prepend the new one
# then the env the subos declares itself (subos_info.envs), op = set | prepend
```
Two UC-1 rules: `prepend` uses `${VAR:+:$VAR}` to avoid a trailing colon (an empty PATH segment
means the current directory); `set` uses `${VAR=v}` rather than `${VAR:=v}`, so **a value the user
explicitly set to the empty string is not overwritten**.

## 4. `xlings self` (`spec.cpp:51-60`; implementation `src/core/xself.cpp:60-180`)

`action = argv[2]`, defaulting to `"help"`. **`-v/--verbose`, `-q/--quiet`, `--agent` and `--ui-mode`
(plus its space-form value) are stripped before the positional handlers see argv**
[src/cli.cpp:1400-1402]; **`-y/--yes` is not** — the strip loop does not list it.
=> Put `-y` **after** the subcommand: `xlings self doctor --yes`, `xlings subos list -y` are both fine
(the action loops ignore it). `xlings -y subos|self|profile|index …` instead exits **2** with a confusing
``unknown subcommand for `xlings <group>`: <group>`` — the surviving `-y` shifts `fargv`, so `fargv[2]`,
which the manual path reads as the subcommand, is the group name itself.

| Subcommand | Options | Line |
|---|---|---|
| `install` | — (surplus arguments are an error) | `:86` |
| `uninstall` | `-y, --yes`; `--keep-data`; `--dry-run` | `:90` |
| `init` | — | `:106` |
| `update` | — | `:110` |
| `config` | **none** (`reject_surplus`; read-only display) | `:114` |
| `clean` | `--dry-run` | `:118` |
| `migrate` | — | `:126` |
| `doctor` | `--deep`; `--scope <PACKAGE[@VERSION]>`; **(new in 2026.9.12.1)** `--subos <NAME>`; `--fix`; `--dry-run`; **(new in 2026.9.12.1)** `--show-ok`; `--all` (**deprecated alias for `--show-ok`**); `--reset-metadata` | `:130`, parsing `:150-180`, option table `spec.cpp:59` |

- `self update` = `platform::exec("xlings install xlings@latest -y --use")`
  (`src/core/xself/update.cpp:67` at 2026.9.20.1; `--use` added then for #602, it was
  `…@latest -y` at `:46` before) followed by `xlings use xlings latest`; on failure it prints
  `hint: run 'xlings install xlings@latest -y' to see why`. Because it goes through the install path,
  it also rebuilds a shim table an older client emptied (#582).
  WARNING: right after an upstream release, `latest` can lag by minutes because the index snapshot
  a release publishes is cut before the index bump it triggers lands. Settle it with
  `xlings index use xim latest && xlings update` before deciding the release is missing.
- **`--all` now warns on every run**: `--all now means --show-ok; --all is kept as an alias but will
  stop being documented` (`src/core/xself.cpp:157-166`). Scripts still work; switch the spelling to
  stop the extra line.
- **`--subos <NAME>`** sets *both* `XLINGS_ACTIVE_SUBOS` and the in-process active-subos override,
  so every subcommand this run spawns follows; an unknown name **exits 2**
  (`src/core/xself/doctor.cpp:5047-5074`).
- **`--fix` implies `--deep` and spawns one child per other subos that owns a finding**
  (`<client> self doctor --fix --subos <name>`); a child carrying `--subos` does not recurse.
  Child timeout: `XLINGS_DOCTOR_CHILD_TIMEOUT` seconds, default **1800**, `0` = no bound
  (`doctor.cpp:3220-3237`); implemented over `timeout(1)` and **applied only when that binary is on
  PATH** (`have_timeout_tool_()`, `:3249-3255`) — absent it (Windows, stock macOS, minimal containers)
  the child is **unbounded**. A failed child counts as outstanding and makes the parent exit non-zero.
- `self doctor`'s `--deep` / `--scope` still have **zero prose documentation**
  (`quick-start/self-management.md` never mentions them), though that file did gain sections on
  `--show-ok`, `--subos`, the sysroot check, lossy repairs, and relocated homes in 2026.9.5.1 /
  2026.9.12.1.
- WARNING: `xlings self clean` deletes `<home>/.xlings` (i.e. `~/.xlings/.xlings`,
  `xself/clean.cpp:14-27`). Nothing inside `src/` creates that nested path — its purpose is
  **unverified**.

## 5. `xlings index` (`spec.cpp:63-67`; implementation `src/cli.cpp:1531-1559`)

| Subcommand | Alias | Arguments | Options |
|---|---|---|---|
| `list` | `ls` | `[name]` (filter by index source) | `--json` — **machine-readable** |
| `use` | — | `<name> <version>` (version may be `latest`) | — |

- With no subcommand it defaults to `list` (`:1542`).
- `--json` outputs a `dump(2)` array; each index source carries `snapshots[]`, and each snapshot
  carries `artifact{name,sha256,size}` (`src/core/xim/index_cmd.cpp:89-103`).
- The non-JSON path distinguishes git-managed sources ("git-managed — no published snapshots")
  from snapshot sources (`:130`).
- Since 2026.9.16.1 both forms show the **artifact chain in try order**: human output prints
  `artifact: <url>  [CN]` then `    then: <url>  [GLOBAL]`; `--json` adds `artifact_bases[]{region,url}`
  per source (`src/core/xim/index_cmd.cpp:88-90,133-137` at `84572b0`). This is the quickest way to see
  whether a `mirror` change took effect.
- `index use` **bypasses the contract check but not the sha256 verification**; **`self update` is
  not subject to snapshot routing**.
- `xlings index use xim latest && xlings update` is also the documented way to settle the
  **release/index ordering lag**: a release's index snapshot is cut before the index bump it
  triggers lands, so `latest` can lag a fresh release by minutes.

## 6. `xlings agent` (`spec.cpp:68-70`; implementation `src/agent/agent.cpp`)

| Form | Meaning | Line |
|---|---|---|
| `xlings agent skills` | list the built-in skills | `:71` |
| `xlings agent skills <name>` | print that skill in full | `:82` |
| `xlings agent <name>` | **shorthand, not in the spec** | `:86-89` |

`agent` dispatches **before** the generic help interception (`src/cli.cpp:1457`), so that
`xlings agent -h` still prints the plain-text skill overview rather than the boxed help rendered
from the spec. There are only two built-in skills: `usage`
(`src/agent/skills/usage.cpp:15`) and `contributing` (`src/agent/skills/contributing.cpp:14`).

## 7. `xlings profile` (`spec.cpp:71-75`; implementation `src/cli.cpp:1591` -> `run_profile_`, `:1013`)

`list` / `commit [reason]` / `rollback <generation>`.
WARNING: generation / rollback semantics live in `src/core/profile.cpp` and were **not dug into
this round — unverified**. This is an entire feature surface with **zero prose documentation**.

## 8. Exit codes

| Code | Meaning | Evidence |
|---|---|---|
| `0` | success; also used for non-error early exits such as "project mode found no config" | `src/cli.cpp:605-606` |
| `1` | command failed (business failure, uncaught-exception fallback), unknown top-level command, **and every rejection raised by the `cmdline::App` parser itself** on the ten App commands (`install remove update search list info why use config interface`) | `:1584-1585`, `:1901+`; `src/cli.cpp:1887` says it verbatim — "app.run returns its own status (**1 for parse errors**, 0 on successful dispatch)" |
| `2` | parse-level rejection on the hand-written dispatch path (`subos` / `self` / `index` / `profile`), a `Refuse`-policy confirmation in non-interactive mode, **and `config`'s own value-validation branches** (see the carve-out below) | `:1538, 1558, 1569`; `src/core/xself.cpp` `reject_surplus` `:83`; `docs/spec/diagnostics.md:102`; `src/cli.cpp:770,840,868` (bad value) and `:697` (`choose_setting_value_` with nobody to ask) |

WARNING: **exit 2 is not "I mistyped something" at the top level.** The split follows the parser, not the
error: the ten App-parsed commands return **1** for an unknown option, a missing option value or a surplus
positional, and only the positionally dispatched group returns 2. Measured on 2026.9.14.1:
`xlings list --bogus` -> `Error: unknown option: --bogus`, **1**; `xlings interface --args` -> `Error: option
--args requires a value`, **1**; `xlings use a b c d` -> `[error] too many positional arguments`, **1**;
against `xlings self doctor --bogus` -> **2**, `xlings subos new a b c` -> `surplus positional argument`, **2**,
`xlings index list --bogus` -> **2**, `xlings profile bogus` -> **2**.
`agent` is hand-dispatched but is **not** in the exit-2 group: `xlings agent nosuchskill` -> **1**
(`src/agent/agent.cpp:91-96`), as is `xlings nosuchcmd` (`cli.cpp:1584-1585`).
CARVE-OUT: **`config` is an App command that also exits 2 on its own** — the App parser hands it a
syntactically fine value and `config`'s handler rejects it downstream with `diag::emit` + `return 2`.
Measured on 2026.9.14.1: `xlings config --ui-mode bogus` / `--theme bogus` / `--interactive bogus` /
`--clear-xpkg bogus` -> **2**, and any enum setting whose value is **omitted** in a non-interactive run
(`--lang` / `--mirror` / `--theme` / `--ui-mode` / `--interactive`, `… needs a value … nothing was
changed`) -> **2**. The picture is mixed, not binary: `xlings config --index-repo bogus` -> **1** and
`xlings config --add-xpkg` (value missing) -> `Error: option --add-xpkg requires a value`, **1**.
=> A script that reads `$? == 2` as "bad invocation" will read a mistyped `xlings install --bogus` as a
business failure; on the App commands **other than `config`**, `2` can only be the `Refuse` confirmation.
On `config`, `2` means either a `Refuse` or a rejected/omitted enum value — read the diagnostic.

**`self doctor` has its own three-way reading of the same codes**: `0` = converged with nothing
outstanding; `1` = issues, outstanding items, or a regression remain; `2` = bad input (`--subos`
naming a subos that does not exist, `--scope` without `--deep|--fix`; `--clear-xpkg` with an
illegal category is the same shape on `config`).
**`remove` exit codes are worth spelling out**: an uninstall hook that throws returns **1** without
`--force` and **0** with it, and in both cases the state is already rolled back; removing a package
this subos does not have is **0** with a Warn (`xim.remove_absent`).

**Severity is not the exit code** (`docs/spec/diagnostics.md:68-86`): when a project
`.xlings.json` declares a version that is not installed, the shim reports `Warn` but **the exit
code is still 1**. The criterion is **who can resolve it** — `Warn` when xlings knows the exact way
out, `Error` when the user has to resolve it elsewhere.
**Non-interactive confirmation policy** (`:93-112`): `Proceed` (install/update, run as usual) /
`Refuse` (remove, report Error + **exit code 2**, do not fake success). See SKILL §1.6.
Diagnostic format: **one problem carries exactly one marker**, with evidence and the way out as
**continuation lines** (`:7-21`); `Diagnostic` has seven fields, and **`actions` is mandatory for
Warn/Error** (`:32`); **`tui.interactive` defaults to false, interaction is opt-in**, on the
rationale that **a pty is not evidence that someone is at the keyboard**.
WARNING: the "stable code table" (`:169-180`) is **not** a complete list any more — it names 15
codes while the source defines **25 dotted codes plus a 10-strong hyphenated `xvm-*` family**
(`xvm-sysroot-drift`, `xvm-binding-metadata-corrupt`, `xvm-switch-member-missing`, … in
`src/core/xvm/inspect.cpp` and `switch_plan.cpp`). Count them separately, because one regex does not
catch both: `grep -rhoP '\.code\s*=\s*"\K[a-z_.]+' src/ | sort -u` prints **26** lines, of which 25 are
the dotted codes and the 26th is a bare `xvm` — the hyphenated family truncated at the `-`. The
hyphen-aware spelling is `grep -rhoP '\.code\s*=\s*"\K[a-z_.-]+' src/ | sort -u` (35 lines). Everything added since
2026.9.12.1 is missing from it (`xim.uninstall_hook_failed`, `xim.uninstall_recipe_unavailable`,
`xim.overlay_identical`, `xim.namespace_priority`, `xim.subos_unreadable`, `self.upgraded`), as are
`xim.ambiguous_target`, `cli.bad_theme`, `xself.kept_existing`, `xself.needs_confirmation`.
**Derive the set from the source, not from that table.**

## 9. Package coordinate syntax (`src/core/xim/catalog.cpp:53-72`)

```
[<namespace>:]<name>[@<version>]
```
- A leading `::` is normalised to `:` at the very start of parsing (`:54-55`), so `xim::gcc` is the
  same as `xim:gcc`.
- The presence of `:` sets `explicitNamespace = true` (`:66`). The canonical name is reassembled
  by `canonical_package_name` as `<ns>:<name>` (`:17-20`); the **on-disk directory name** comes
  from `package_store_name` as `<ns>-x-<name>` (`:22-25`).
- Ambiguity hints are produced by `format_ambiguous_candidates`, which renders each candidate as a
  directly copy-pasteable `xlings install <ns>:<name>@<ver>` (`:31-49`).
- **Namespace ranking**: in `namespace_rank_`, `local` scores 1 and everything else 0, the comment
  says `lower wins`, and `min` is taken as best (`:197-199`), so **`local:` is demoted relative to
  other namespaces**; demoted entries go into the `demoted` list and are shown without `@`
  (`:216`).
- **The demotion notice is now said once per (id, fingerprint)** rather than on every command:
  id `catalog.demoted`, diagnostic code `xim.namespace_priority`, persisted through `hintsSeen`
  (`:619-628`). It is silent when both sides carry the same version. => Every bare-name shadow you
  leave in the local overlay costs one of these; `config --list-xpkg` then `--clear-xpkg stale` is
  the cleanup (SKILL §5.4).
- Four layers of disambiguation: (1) **a bare name only looks at the primary index**; sub-index
  candidates are merged in only when a namespace is given explicitly (`:296`, `:512`);
  (2) project scope beats global; (3) namespace rank (`:315`, `:809`); (4) if nothing separates
  them, an ambiguous error lists the candidates and their source repos.
- **Version-key spelling is a separate contract** — which index a package came from decides whether
  its version key carries `ns:`, and that is read off the entry's **name**, never its position in
  `index_repos` (`docs/spec/xlings-json-schema.md:70-85`, since 2026.9.2.1). See SKILL §2.

## 10. e2e contract scripts (closer to the truth than docs when a behaviour is in doubt)

`tests/e2e/` holds **142 `.sh` files** (was 124 at the previous baseline); the names are the
contracts. Ones worth remembering:
`install_use_semantics_test.sh`, `install_idempotent_test.sh`, `list_exact_inventory_test.sh`,
`diagnostics_contract_test.sh`, `info_output_contract_test.sh`,
`index_repo_order_test.sh` (the differential test for #575), `legacy_config_test.sh`,
`cli_short_alias_removal_test.sh` (pins the removal of the `xim`/`xvm` aliases),
`xpkg_spec_gate_test.sh` (asserts that one bad recipe does not take down the other packages in the
same batch).
Added with the releases in `version-notes.md`, and the shortest description of each new behaviour:
`shim_table_routing_test.sh`, `shim_project_context_test.sh` (2026.9.3.1 routing + host
passthrough), `doctor_honest_verdict_test.sh` (a lossy `--fix` does not print `OK`),
`doctor_relocated_home_test.sh` (2026.9.5.1), `doctor_cross_subos_fix_test.sh` and
`doctor_cross_subos_child_timeout_test.sh` (the `--fix` walk and its timeout),
`doctor_remedy_mode_parity_test.sh` (default report's remedies match `--deep`'s),
`doctor_removed_not_reinstalled_test.sh`, `current_subos_unreadable_test.sh`,
`remove_force_contract_test.sh` and `remove_multi_version_test.sh` (2026.9.12.1 `remove`),
`local_overlay_test.sh` (the `--*-xpkg` verbs), `doctor_swept_payload_test.sh` (2026.9.14.1).
WARNING: several of these are POSIX-shell only — the new contracts have **no PowerShell port**, and
the doctor child timeout is built on `timeout(1)`, applied only where that binary is on PATH — so it
is absent on Windows **and** on stock macOS / minimal containers (upstream openxlings/xlings#592, open).
