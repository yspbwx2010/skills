# What changed since `2026.9.15.2`

Moved out of `SKILL.md` to keep it short; section numbers there still point here.

Twelve releases, `2026.9.16.1` to `2026.9.21.3`. The CLI word list is still 28 commands and nothing was removed; per-release detail
with the spelling to type is `references/version-notes.md` §2, the upgrade checklist is its §4.

**Can turn a gate red, or change an artifact, on the first run after upgrading:**
- The global dependency cache epoch moved 2 -> 3 (`2026.9.18.1`): **every dependency recompiles once**, old entries are orphaned
  rather than deleted (`mcpp cache gc` reclaims them). §8.
- `mcpp.lock` `hash` values are rewritten once on Linux/macOS (`2026.9.20.1`, host-independent FNV-1a). `--locked` is not tripped
  (it compares versions), but the lock file shows a diff. §1.3.
- Unknown keys in `[package]` are now reported (a warning, an error under `--strict`) (`2026.9.16.1`). §5.
- A `cflags`/`cxxflags`/`asmflags` element is read with one fixed word syntax on every host (`2026.9.17.1`); a `defines` entry is one
  value, so `N="x"` now reaches the compiler with its quotes. A changed reading warns once as `build/flag-words`. §5.
- When the target's C library / C++ runtime comes from the dependency graph (the openkal targets), the compiler's own host header
  search is closed on Clang (`-nostdlibinc` / `-nostdinc++`, `2026.9.17.3`): code that compiled only because a host header filled a
  gap now fails deterministically. GCC keeps its command line and gets a `degraded` warning instead (an error under `--strict`). §7.
- C++ runtime per process, static placement and pack stripping changed (`2026.9.16.1`): new refusals `program-cxx-runtime-split` and
  `static-package-in-two-images`, a `build/static-placement` warning, and `mcpp pack` now strips shared libraries the graph built.
- `mcpp run`: `--profile` now wins over `--release`/`--dev` (it used to be the other way round on `run` only). §1.1.
- `[index] auto_refresh = false` now blocks **every** implicit refresh, including the first sync of a project's custom index. §1.5.
- The glibc a toolchain payload declares is installed by mcpp and matched by exact version (`2026.9.17.2`); a home without it
  downloads it once, and offline that is an error naming `xim:glibc@<version>`.
- Engine-defined macros: `__MCPP_TARGET_<OS>__` on every target-side unit, `__OPENKAL__` when `kernel-abi = openkal`, and
  `__CYGWIN__` is **no longer** defined under a POSIX-presenting Windows C library (`2026.9.21.2`). §7.

**New surface:** `mcpp test --no-run`; `mcpp pack --release`/`--dev`/`--message-format json`; `--features <dep>/<feature>` on the
command line (also on `why deps`); a `git` dependency can select a member package of that repository; `mcpp::graph_file()` with
`[package.metadata.<tool>]`; `[index] refresh_timeout`; the `[c-abi]` / `[c-abi-absent]` / `[kernel-abi]` target-side declarations,
`[package] c-environment`, `provides = ["platform-sdk"]` with `[build] platform-dependencies = "refuse"`; a mirror-partitioned default
index artifact; the bundled xlings is `2026.9.16.1`; `pip install mcpp-bin` as an install channel.

**Traps still open at this baseline:** a fast-path hit never rewrites a deleted `compile_commands.json`; `--no-color` is a no-op on a
TTY; `[modules].exports` is never checked for a namespaced package. All three are in `references/troubleshooting.md` §K8.

**One release on top, `2026.9.24.1`**, is mostly about Windows and macOS: the MSVC toolset became the sysroot of a clang
`*-windows-msvc` row, `msvc@<toolset>` takes an installed toolset before the payload, `macos_deployment_target` is decided by the
target rather than the host, and `mcpp self doctor` reports frozen fixincludes headers in gcc payloads. Two changes can stop
a Linux build: `xim:` is now the only namespace a toolchain spelling accepts (any other `<ns>:` prefix used to be dropped
silently and is now refused, §5), and a `*-windows-msvc` row's `sysroot` no longer takes a C library package or `""` (refused when
the manifest is parsed, on every host). CLI word list and flags are unchanged. Detail with the spelling to type is
`references/version-notes.md` §2 (2026.9.24.1) and §4.0; the new failure messages are `references/troubleshooting.md` §L.
