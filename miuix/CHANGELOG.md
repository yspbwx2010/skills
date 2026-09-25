# Changelog

## Unreleased

- **Moved** into the [yspbwx2010/skills](https://github.com/yspbwx2010/skills) collection (the repository
  was renamed from `miuix-agent-skill`). New install commands: `npx skills add yspbwx2010/skills --skill miuix`,
  or `/plugin marketplace add yspbwx2010/skills` then `/plugin install miuix@yspbwx2010-skills`. The Claude
  Code plugin is now `miuix` (was `miuix-skill`) and the marketplace `yspbwx2010-skills` (was `miuix-skill`),
  so reinstall it under the new names.
- **Fix**: the `joinToPath` trap showed the Kotlin literal for one backslash as `"\\\\"`; it is `"\\"`.
  The YAML parser now decodes `\\` the same way whether or not PyYAML is installed.

## 1.0.0 — for Miuix 0.9.4

First public release.

- **Scaffold**: `skills/miuix/scripts/new_app.py` generates a compiling project from an empty directory —
  Kotlin Multiplatform (Android / desktop / web, any subset) or plain Android. Versions: Gradle 9.7.1,
  AGP 9.4.1, Kotlin 2.4.20, Compose Multiplatform 1.12.0, compileSdk 37. Every layout is built in CI.
- **References** synced to the Miuix 0.9.4 release (tag `v0.9.4`) and split into 17 topic files plus an
  index; every source location links to GitHub. Signatures now keep `suspend` / `inline` and type
  parameters; every public type lists its import path; icons explain their two-part import.
- **Hand-written layer** re-verified against 0.9.4: `NavigationRail`'s split into two overloads, the new
  `Modifier.pagerGestureOverride` family (new `pager.yaml`), `LocalNavTransitionScope`, `NavKey` /
  `NavEntryBuilder` routing, SavedState support in nav entries, and the Overscroll fixes.
- **Extraction fixes**: top-level `val`s whose initializer starts on the next line (`LocalNavTransitionScope`
  was missing), and enum entries preceded by KDoc (ten enums had no entries at all).
- **Corrections from empty-directory trials**: compileSdk 37 is required; plain Android projects use the
  root Maven coordinates (no `-android` suffix needed); prefer `Window*` popups when unsure (an `Overlay*`
  outside a `Scaffold` silently renders nothing); miuix-nav needs the serialization compiler plugin; the web
  target has no CJK font.
- **Recipes**: `references/recipes.md` — hand-written, compile-verified combinations (bottom bar + pager +
  collapsing top bar, Chinese text on the web, icons for common meanings), rendered from `data/recipes/`.
- **Gates**: `validate_skill.py` (Agent Skills spec + links stay inside the skill), `check_evidence.py`
  (every `file:line` exists; `--rebase` shifts line numbers across an upgrade), `render.py --check`.
