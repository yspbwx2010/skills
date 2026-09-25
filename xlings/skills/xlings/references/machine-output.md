# Reference: xlings machine-readable output (four layers)

> Baseline xlings source `main @ 4ea4eac` / `2026.9.14.1`, dated 2026-09-16.
> WARNING: the only thing executed in this pass was `--help` / `--version` / `--command-reference-json`. The NDJSON
> tables below come from source-code evidence and are otherwise **unverified**. Run `--list` once to self-verify
> before wiring it up.
> **One breaking change and one gap since the previous baseline**: the `list_subos` field rename (§3) and the
> missing parity for the 2026.9.12.1 CLI verbs (§3). Both are in `version-notes.md`.
> **Refresh 2026-09-23 (source `main @ 84572b0`, 2026.9.20.1, not executed)**: parameter validation before dispatch
> (§3.1), typed extraction errors (§3.1), `artifact_bases` in `index list --json` and `list_repos` (§2, §3). Protocol
> version and capability count unchanged (still `1.0`, still 20). Line numbers in the tables below are from `4ea4eac`
> and have moved in `src/interface.cpp` and `src/capabilities.cpp`.

## 0. The four layers

| Layer | Trigger | Output form | Evidence |
|---|---|---|---|
| **Global plain text** | any command + `--agent` | ANSI off, TUI layout off; error/warn to stderr, everything else to stdout | `src/cli.cpp` |
| **Single-command JSON** | `xlings index list --json` | JSON array, indent 2 | `src/cli.cpp:1549`; `src/core/xim/index_cmd.cpp:89-103` |
| **NDJSON protocol** | `xlings interface [capability]` | one JSON object per line | `src/interface.cpp` |
| **Command-tree JSON** | `xlings --command-reference-json` (**hidden**, must be the only argument) | `spec::reference_json().dump()` | `src/cli.cpp:1190` |

**`--agent` vs `interface`**: `--agent` does **not** set `tui_mode(true)`; logs
still go to the terminal, it only strips the ANSI decoration. **`interface` is the fully programmatic channel.**

## 1. `--agent`: what it does and does not do

- Does: stable plain text, no ANSI, stream separation (error/warn to stderr).
- Does **not**: make `remove` safe. The `Refuse` policy for non-interactive confirmation (remove's default
  direction) raises `Diagnostic{Error}` and **exits 2**; historically `xlings remove foo --agent` **printed
  `cancelled`, exited 0, and left the package installed**.
  Therefore: **always pass `--yes` explicitly for install/remove/update.**
- The built-in skill's RULES say the same (`src/agent/skills/usage.cppm:25-40`): (1) always add `--yes` to
  install/remove/update, otherwise it **hangs** non-interactively; (2) always add `--agent`; (3) never guess a
  package name, run `xlings search` first; (4) before installing anything, check for a `.xlings.json`; if present,
  run `xlings install --yes --agent` with no package arguments.

## 2. `xlings index list --json`

Output is a `dump(2)` array. Each index source carries `snapshots[]`, and each snapshot carries
`artifact{name, sha256, size}` (`src/core/xim/index_cmd.cpp:89-103`). The non-JSON path distinguishes
git-managed sources (`"git-managed — no published snapshots"`) from snapshot sources (`:130`).
Client semantics (`docs/design/index-version-contract.md:132-147`): in human output `*` = **the tree on disk**
(what is actually being read right now), `>` = **what the next update will fetch**; in `--json` these correspond
to `installed` / `current`.
Since 2026.9.16.1 each source also carries **`artifact_bases`**: an array of `{region, url}` in the order the refresh
tries them (the configured `mirror`'s region first, then GLOBAL, then the rest); human output prints the same as
`artifact: <url> [REGION]` followed by `then: <url> [REGION]` lines. An empty array only means no artifact base is
**configured on that entry**; an official entry can still take the official pointer through the declared-source rule
(SKILL §5.3), so do not read it as "git only" without checking.

## 3. NDJSON interface (protocol v1.0)

- Protocol version constant `src/interface.cppm:25` `kProtocolVersion = "1.0"` — **unchanged across all seven
  releases in this window**, even though the CLI surface grew.
- `--version` -> `{"protocol_version":"1.0"}` (`src/interface.cpp:65`).
- `--list` -> `{"protocol_version":"1.0","capabilities":[...]}`; each capability self-describes with `name` /
  `description` / `destructive` / `inputSchema` / `outputSchema` (`:84`).
- **No capability name (bare invocation)** -> `{"kind":"result","exitCode":1,"error":"capability name required.
  Use --list…"}` and **exit 1** (`:91`). To get the capability table you **must** use `--list`, and the key is
  **`protocol_version`**, not `protocol`.
- Input: `--args <JSON>` or `--args-file <PATH>` (the latter sidesteps Windows cmd.exe quoting problems, `:99`).

**Complete set of event `kind` values**: `progress`, `log`, `data`, `prompt`, `error`, `result`, `heartbeat`.

**stdin control channel** — one JSON object per line, key `action`:
`cancel` / `pause` / `resume` / `prompt-reply`; an unknown action is an error.

### 3.1 Parameter validation and error codes (2026.9.20.1)

`docs/spec/interface-ndjson-v1.md` §3.3.1 / §8. Before a capability runs, the server checks:

1. **every capability**: `--args` parses as JSON and is a JSON **object**;
2. **capabilities that declare `inputSchema.required`** (12 of the 20): each required field is present and not `null`.

A failure emits one `error` event (`code: "E_INVALID_INPUT"`, `message: "missing required field(s): <names>"`,
`recoverable: false`, `hint` naming the full required set) and then `{"kind":"result","exitCode":1}`; **the capability
is not executed**. `--args ""` equals no `--args` (`{}`), and unknown extra fields are still accepted - this is the
published `required` plus top-level type, not full JSON Schema validation.

Why a client must care: on 2026.9.16.1 and earlier, a misspelled field was indistinguishable from a legitimate
answer (`plan_install` with a typo'd `targets` returned `{"exitCode":0}` = "nothing to install"; `list_packages`
with a bad `filter` listed everything; `update_packages` updated the whole index), and `create_subos` +
`remove_subos` with `{}` deleted every SubOS in the home (#611). An empty SubOS name is now refused by the operation
itself as well, so `{"name":""}` - a well-formed request - is stopped too.
=> **Against an xlings older than 2026.9.20.1 (mcpp 2026.9.21.3 still bundles 2026.9.16.1), validate params on the
client side** and never send an empty name to a SubOS capability.

**Error codes that changed meaning**: an extraction failure is no longer always `E_INTERNAL` - a corrupt archive or an
unsupported entry is `E_INVALID_INPUT` (the hint says the cache was cleared and a retry downloads again), a write
failure is `E_DISK_FULL` (#376). No new code was introduced. Cancellation stays exit 130, a policy refusal exit 2.

### The 20 capabilities (`src/capabilities.cpp`)

| # | Name | Line | | # | Name | Line |
|---|---|---|---|---|---|---|
| 1 | `search_packages` | `:63` | | 11 | `list_index_versions` | `:257` |
| 2 | `install_packages` | `:79` | | 12 | `list_subos` | `:288` |
| 3 | `plan_install` | `:107` | | 13 | `list_subos_shims` | `:316` |
| 4 | `remove_package` | `:129` | | 14 | `create_subos` | `:344` |
| 5 | `update_packages` | `:147` | | 15 | `switch_subos` | `:364` |
| 6 | `list_packages` | `:163` | | 16 | `remove_subos` | `:379` |
| 7 | `package_info` | `:178` | | 17 | `list_repos` | `:394` |
| 8 | `list_installed_versions` | `:193` | | 18 | `add_repo` | `:422` |
| 9 | `use_version` | `:208` | | 19 | `remove_repo` | `:475` |
| 10 | `system_status` | `:223` | | 20 | `env` | `:537` |

**Still 20** — no capability was added in this window. Verify with
`grep -c '\.name = "' src/capabilities.cpp`.

WARNING: **`docs/spec/interface-ndjson-v1.md:197-215` still lists only 19** — it is missing `list_index_versions`
(`:257`, `destructive=false`, `dataKind: index_versions`), which is exactly the programmatic counterpart of
`xlings index list`. **Do not copy that section of the upstream docs.**

**BREAKING, 2026.9.3.1 — `list_subos` field rename**: entries no longer carry `pkgCount`. They carry
**`commands`** and **`packages`** (`src/capabilities.cpp:303-304`), backed by `SubosInfo::commandCount` /
`packageCount` (`src/core/subos.cppm:60,64`). `commands` = the size of the routing table, i.e. how many command
names the subos publishes; `packages` = releases, de-duplicated through `bindingGroup`, so one llvm is 1 package
and roughly 40 commands (`packageCount == -1` means "not computed"). The agent text changed the same way, from
`(N packages)` to `(N commands, M packages)`. The read side still tolerates an old `pkgCount` on input, but nothing
emits it. Upside: `packages` is finally a real package count and can be asserted on in a gate.

**`list_repos` entries** gained `artifact_bases[]{region,url}` beside `name`, `url` and `scope` (2026.9.16.1).

**WARNING, the 2026.9.12.1 CLI verbs have no counterpart here** (upstream openxlings/xlings#593, **still open on
2026-09-23**): `remove --all` / `--all-subos` / `--subos`, `config --list-xpkg` / `--remove-xpkg` /
`--clear-xpkg`, and `self doctor --subos` / `--show-ok` are reachable **only through argv**. The field rename
above was the only NDJSON change in the whole window. If you are designing an agent integration around
`interface` exclusively, plan to shell out for those.

**CLI and capabilities are not one-to-one**: `plan_install` (dry-run), `list_subos_shims`, `env`, `system_status`,
and `list_repos` / `add_repo` / `remove_repo` have **no equivalent standalone CLI subcommand** (on the CLI side,
repo management is `xlings config --index-repo <NS:URL>`). Conversely, `why` / `profile` / `script` have
no capability — and now so do the verbs listed in the warning above. **`info` does have one** —
`package_info` (#7 in the table above) — but with a stricter input shape (`namespace:name`, e.g. `xim:gcc`)
and no `--all-versions` equivalent.

### Reference clients

`examples/clients/` (`bash_jq.sh` / `python_client.py` / `node_client.mjs`), all three running the same flow:
probe `--version` and assert `1.0` -> `--list` and count capabilities -> call `env` -> call `list_subos` ->
`plan_install xim:bun` (dry-run, proving nothing is actually installed) -> optional
`add_repo` / `list_repos` / `remove_repo` lifecycle. `examples/clients/README.md` also states what is **not
covered**: streaming `install_packages`, the stdin control channel, and `run` / `exec`, which are deferred to v2.

### How mcpp uses it (a shape you can copy directly)

mcpp's `[xlings] deps` provisioning takes exactly this path (in an `<mcpp source checkout>`:
`src/build/prepare.cppm:1641` -> `src/xlings/xlings.cppm:1565`):
```
cd '<home>' && env -u XLINGS_PROJECT_DIR XLINGS_HOME='<home>' '<xlings>' \
    interface install_packages --args '{"targets":[...],"yes":true}' 2>/dev/null </dev/null
```
Three reusable judgments: **stdin is sealed** (`</dev/null`) because the protocol is NDJSON-over-stdout plus
`"yes":true`; use `install_packages` rather than `resolve_xpkg_path` (the latter demands `<name>@<version>` and
rejects a bare `mesa`); **build args with a JSON library, not string concatenation** (deps are manifest input, so
quotes/backslashes produce malformed JSON, and the failure surfaces as an xlings parse error that mentions
neither the manifest nor the key).

## 4. `xlings --command-reference-json` (hidden)

Must be the **only argument**. It is the data source for `docs/generated/command-reference.md` (187 lines); the
generating command is written in that file's header (`:3-7`):
`python3 tests/scripts/test_generated_command_reference.py --xlings <path> --write`.
**CI validates the diff on every run** (`.github/workflows/xlings-ci-linux.yml:362`; without `--write` it is check
mode). It covers the root command plus **5** command groups (`subos` 7 children, `self` 8, `index` 2, `agent` 1,
`profile` 3 — the only spec children carrying `children`, `src/cli/spec.cpp:42-75`), 38 headings total
(1 root + 16 top-level + 21 subcommands), and gives **only a one-line description
plus an option list — no examples, no semantics**. It is therefore **the single authoritative, auto-synced source
for which commands exist**; when the prose docs lag, it wins. It is also the cheapest way to settle "how many
top-level commands are there" — the answer today is **16**.
WARNING: it does **not** render aliases (`subos ls` / `rm` / `i` and `index ls` are not found).

## 5. Recommendations for CI / agent integration

1. **If you need structured results, use `interface`; do not parse `--agent` human text.** `--agent` only
   guarantees "stable plain text" — no schema, no version number.
2. **Probe `interface --version` first and assert `protocol_version == "1.0"`** (all three reference clients open
   this way), then `--list` to confirm the capability you want is present.
3. **Exit codes are not enough**: `interface` failures are expressed as `{"kind":"result","exitCode":…}`; at the
   top level, exit code `2` carries two different semantics on `subos`/`self`/`index`/`profile`,
   where it means either a parse-level rejection or a non-interactive `Refuse`. On
   `install`/`remove`/`update`/`use`/`list`/`info`/`why`/`search`/`interface`, a parse rejection is
   exit **1** [src/cli.cpp:1887], so `2` there is unambiguously the `Refuse` case. **`config` is not in
   that safe list**: it is App-parsed, but its own handler exits **2** for a rejected enum value
   (`--ui-mode`/`--theme`/`--interactive`/`--clear-xpkg` given a bad word [src/cli.cpp:770,840,868]) and
   for an enum value **omitted** in a non-interactive run [`choose_setting_value_` `:697`], so on `config`
   a `2` may be either that or a `Refuse`. Where `2` is ambiguous you
   must read the stderr diagnostic, or switch to `interface` (see `commands.md §8`).
4. **For destructive operations, read the capability's self-described `destructive` field** instead of maintaining
   your own allowlist.
5. **Use `plan_install` for dry-run**; it has no CLI counterpart, and `xlings install` has no `--dry-run` (only
   `self uninstall` / `self clean` / `self doctor` do).
6. **You still have to pass `--yes`** (in `install_packages` args this is `"yes":true`).
7. **Do not assume the NDJSON channel keeps up with the CLI.** Protocol version is still `1.0`, capability count is
   still 20, and a whole release's worth of new verbs landed on argv only (#593). Check `--list` against what you
   intend to call, and be ready to shell out.
8. **Expect `list_subos` consumers to break on upgrade**: `pkgCount` is gone in favour of `commands` + `packages`.
9. **Assert the bootstrap actually installed something.** `quick_install.sh` can **exit 0 having downloaded
   nothing**, and a green bootstrap step that installed nothing fails much later and much more confusingly. Wire it
   as `curl -fsSL --retry 3 -o quick_install.sh <url>; bash quick_install.sh; test -x "$XLINGS_HOME/bin/xlings"` —
   the script's exit code is not proof. (Its own variables are in `env-vars.md §7`.)
