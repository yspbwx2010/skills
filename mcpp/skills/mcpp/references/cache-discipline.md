# Cache discipline

Moved out of `SKILL.md` to keep it short; section numbers there still point here.

- **Two caches**: the cross-project dependency cache `$MCPP_HOME/build-cache/v1/{pkg,std}` (a multi-axis key including the **full
  triple** and the **C library header set**), and the project-local `target/<triple>/<16-hex fingerprint>/`. On a clang
  `*-windows-msvc` row the header set also carries the chosen MSVC toolset directory and Windows SDK version, so two toolsets are two
  keys [src/build/cache_key.cppm:502-509 @ b4824697]. Neither cache key contains the engine version; only the project fingerprint does
  (next bullet).
- WARNING: **`MCPP_VERSION` is input 7 of the 11 that make up the whole-project fingerprint** (indices here are the source's own
  **0-based** `parts[N]`, so the eleven inputs are `parts[0]`..`parts[10]`)
  [modules/toolchain-model/src/fingerprint.cppm:125] => **upgrading mcpp means a brand-new empty directory and a full rebuild of the
  project**. Gate-timing comparisons must fix the mcpp version, or the numbers are not comparable. The dependency cache **layout version
  is still `v1`**, but its epoch is **3** since 2026.9.18.1 [src/build/cache_key.cppm:95]: the key used to miss the realised `[c-abi]`
  environment (it read a package's declared `cflags`, not the engine's broadcast), a corrected key cannot vouch for entries written
  under the wrong one, so **every existing entry was orphaned and the first build after upgrading past 2026.9.18.1 recompiles every
  dependency** - by design, not a regression. The key now folds in the broadcast `cflags`/`cxxflags`/`asmflags`. (An earlier label
  rename in the 2026.9.1x window, `macos_deployment_target` -> `min_platform_version`, had the same miss-everything effect on a smaller
  scale.) Old entries are not deleted, merely never hit again: **run `mcpp cache gc` after such an upgrade**, or the home quietly holds
  two generations.
  WARNING: the **install-hook store** (`data/xpkgs`) is still keyed by package and version only; a hook that compiles target-side C
  code cannot know the realised environment (it runs before the toolchain resolves), so nothing checks that its objects match. Upstream
  documents this as an open gap in docs/22.
- **`--cache` has three levels**: `global` (default, reads and writes the global cache) / `local` (**never touches the global cache**;
  every dependency is compiled from source inside this project; **does not clear the directory**) / `off` (same as local, **plus it first
  clears this run's own `target/<triple>/<fp>/`**). Measured, `--cache local` is **3x slower** than the default.
  WARNING: `--help` says `--no-cache` is a "Deprecated alias for --cache=off (**also** clears the build dir)", which reads as if `--cache off`
  alone did not. It does: `run_build_plan` computes `coldBuild = no_cache || cacheMode == CacheMode::Off` and wipes `outputDir` on either
  [src/build/execute.cppm:828-835]. The two spellings are genuinely equivalent [src/cli/cmd_build.cppm:129-133]; the help text's "also" is
  the wrong word. One more instance of §2's rule: **read the implementation, not `--help`**.
- WARNING: **there is no `--force` / `--rebuild`**, and no switch for "force a rebuild but keep the directory". The **only two correct
  ways to force a rebuild**: `mcpp clean` then rebuild; or `mcpp build --cache off` (add `mcpp cache clean --all` to also exclude the
  global cache).
- **Reclaiming `target/` without forcing a recompile**: `mcpp clean --stale`, from the member directory, using that member's
  `target/.build_cache` as the record of what is current. Always `--dry-run` first. Three things to know:
  1. With **no build record at all** it refuses rather than guessing - a tree where only `mcpp test` has ever run has no record, because
     the test build writes none. Run a `build` once first.
  2. Unrecorded directories written within `--older-than` (default `1d`) are **kept**. That window is the only thing protecting a
     directory `mcpp test` just produced, so `--older-than 0` on a freshly tested tree deletes work you still want.
  3. It is **per member**: the record is that directory's. A multi-member workspace needs one run per member. `dist/` and anything else
     outside the record is never touched.
  WARNING: bare `mcpp clean` is still the full wipe. Never reach for it as the disk-space command.
- **Two common cache-hygiene disciplines, and their current status**:
  - **"Clear the cache before switching targets" can be retired**: host/musl cache-axis pollution is fixed at three layers - the full
    triple (including the env segment) enters the dependency cache key, the C library header set enters the key, and the build directory
    and fast path are slotted per target. There is a targeted e2e (`283_run_target_flag_owns_its_cache_slot.sh`, which uses musl).
  - **"Clear the cache first" after changing the dependency graph is still warranted**: over-capture of a dependency unit's header set is
    only half fixed. `[build] private_include_dirs` is **opt-in**; without it the whole set is still published, and **`includeDirsAfter`
    has no corresponding private axis**, so it retains the same shape as the line that was fixed.
  - Residual boundary: **two same-named subos under two different homes are still one key**, distinguished only by the **last** of the
    eleven whole-project fingerprint inputs - `parts[10]`, the runtime binding
    [modules/toolchain-model/src/fingerprint.cppm:128-129].
- **Not cached across projects**: `path` and `git` dependencies at any depth, **and workspace members** - their sources can change while
  `name@version` stays the same [docs/05-dependencies.md]. Host **tools** built from such dependencies are cached, but their key now
  carries the source (a `git` tool by resolved commit, a `path` tool by a stat imprint of the tree), so editing one without bumping a
  version reaches consumers instead of serving a stale binary.
- **Concurrency has four rungs**: `MCPP_JOBS` (where `--jobs` lands) > `[build] jobs` (per package, in `mcpp.toml`) >
  `[build] default_jobs` (per machine, in `$MCPP_HOME/config.toml`) > 0 (say nothing, let the backend decide)
  [src/build/schedule/policy.cppm:128-131,288]. `default_jobs` **also bounds `mcpp test`'s test-process concurrency**, whose fallback is
  otherwise the whole machine - which is usually the real reason a test leg saturates a box that a build leg does not. `[workspace.build]`
  correctly refuses `jobs`, so a machine fact has exactly one place to live.
  => On a throttled machine, write `default_jobs` once in the home's `config.toml` as a floor, and keep `MCPP_JOBS` on the command line as
  the explicit cap; the two do not conflict.
  WARNING (stale-claim retired): `[build] default_backend` has been **deleted** - it promised a choice `src/build/` never implemented.
  Delete it from any `config.toml` that still carries it.
