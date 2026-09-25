---
name: miuix
description: Build apps with Miuix (top.yukonga.miuix.kmp), the Xiaomi HyperOS-style Compose Multiplatform UI library — scaffold a compiling project in an empty directory, source-extracted signatures for every component, HyperOS visual specs, and the traps that make Miuix code fail to compile or look wrong. Use when creating a new app with Miuix, adding Miuix to an Android or Kotlin Multiplatform project, writing, fixing or reviewing any Miuix component (Scaffold, TopAppBar, SwitchPreference, ArrowPreference, OverlayDialog / WindowDialog, BottomSheet, NavigationBar, TabRow, HorizontalPager, miuix-nav, squircle, blur …), or porting a Material3 screen to Miuix. Triggers on "miuix", "HyperOS 风格", "小米风格", "MIUI 风格", "MiuixTheme", "miuix-ui", "miuix-preference", "miuix-nav", "用 miuix 写", "用 miuix 做".
license: MIT
compatibility: The scaffold script needs Python 3.9+. Generated projects need JDK 21; Android targets need Android SDK Platform 37.
metadata:
  miuix-version: "0.9.4"
---

# Miuix

Miuix is a Compose Multiplatform UI library (Android / desktop / web / iOS) that recreates Xiaomi's
HyperOS visual language. It is **not** a Material3 reskin — press feedback, corners, overscroll and
the overlay mechanism are all a different system. This skill targets **miuix 0.9.4**.

## Read your situation first

| Situation | What to do |
| --- | --- |
| Empty directory / new app | Use `scripts/new_app.py` to generate a project that compiles, then only edit the UI code (see "From scratch") |
| Existing Android or KMP project | Add the dependencies per "Integrate into an existing project", and **check compileSdk 37 first** |
| The project depends on a miuix that isn't 0.9.4 | Tell the user this skill is written for 0.9.4 and signatures may differ; treat the source for that version as authoritative: `https://github.com/compose-miuix-ui/miuix/tree/v<version>` |
| You can read the miuix source (submodule or local checkout) | Take signatures from the source; use `references/` for traps, specs and choices |

## From scratch

`<skill>` is this skill's directory (next to `SKILL.md`). Run in the target directory:

```bash
python3 <skill>/scripts/new_app.py . --name "My App" --package com.example.myapp                    # Android + desktop + web
python3 <skill>/scripts/new_app.py . --name "My App" --package com.example.myapp --targets android,desktop
python3 <skill>/scripts/new_app.py . --name "My App" --package com.example.myapp --layout android   # plain Android, no KMP
```

- `kmp` layout (default): `composeApp` (the KMP shared module, all UI code) + `androidApp` (produces
  the APK only). `android` layout: a single `app` module, an ordinary `com.android.application` project.
- The output bundles a Gradle wrapper, so no Gradle install is needed. It needs **JDK 21**; when
  Android is included it needs **Android SDK Platform 37** (`ANDROID_HOME`, or `sdk.dir` in
  `local.properties`).
- The UI code is a single `App.kt` that already demonstrates theming, a collapsing top bar,
  preferences wrapped in a Card, two-page miuix-nav routing and a confirm dialog. **Edit on top of
  it**, don't start over. If a single-page app needs no routing, you can drop the `miuix-nav`
  dependency and the serialization plugin (remove both together), then remove the `NavDisplay` from
  `App.kt`.
- For common combinations (bottom bar + swipeable pages, Chinese text on the web, etc.) read
  `references/recipes.md` first — the code there is compile-verified.

| Platform | Build / run |
| --- | --- |
| Android | `./gradlew :androidApp:assembleDebug` (the `android` layout uses `:app:assembleDebug`) |
| Desktop | `./gradlew :composeApp:run` |
| Web | `./gradlew :composeApp:wasmJsBrowserDevelopmentRun` |

⚠️ **The web target has no built-in CJK font**, so Chinese renders as tofu boxes (Android and
desktop use the system font, so Chinese just works). To show Chinese on the web, wire up a font per
the "Chinese text on the web (wasmJs)" recipe in `references/recipes.md`: Miuix has no global font
entry point, so you must push a `fontFamily` into all 14 styles of `defaultTextStyles(...)` and pass
that to `MiuixTheme`.

## Integrate into an existing project

The compile-verified version set (the template uses exactly this set):

| Item | Version | Notes |
| --- | --- | --- |
| miuix | 0.9.4 | Maven Central release |
| Kotlin | 2.4.20 | The host should be on the 2.4 line |
| Compose Multiplatform | 1.12.0 | Matches miuix 0.9.4; 1.12.1 warns about a runtime version mismatch on wasm |
| AGP | 9.4.1 | |
| Gradle | 9.7.1 | |
| compileSdk | **37** | Required. Below 37, `checkDebugAarMetadata` fails: the miuix and androidx.compose 1.12 AARs require ≥ 37 |
| minSdk / JDK | 24 / 21 | |

```kotlin
// KMP: commonMain. Plain Android: the app module's dependencies. Both use the root coordinates with
// no platform suffix; Gradle metadata selects the -android / -desktop / -wasm-js variant (verified for plain Android).
implementation("top.yukonga.miuix.kmp:miuix-ui:0.9.4")          // required
implementation("top.yukonga.miuix.kmp:miuix-preference:0.9.4")  // preferences
implementation("top.yukonga.miuix.kmp:miuix-icons:0.9.4")       // extended icons (936)
implementation("top.yukonga.miuix.kmp:miuix-nav:0.9.4")         // in-app navigation
implementation("top.yukonga.miuix.kmp:miuix-blur:0.9.4")        // optional
implementation("top.yukonga.miuix.kmp:miuix-squircle:0.9.4")    // optional
```

- **Using miuix-nav's `rememberNavBackStack` requires the kotlinx-serialization compiler plugin**
  `org.jetbrains.kotlin.plugin.serialization`. Route keys must be `@Serializable`; without the
  plugin it still compiles but throws `SerializationException` on first composition at runtime. You
  don't add the runtime library yourself — miuix-nav brings it transitively. See `NavKey` in
  `references/nav.md`.
- **KMP project under AGP 9**: the shared module uses the `com.android.kotlin.multiplatform.library`
  plugin, configured in `kotlin { android { namespace = …; compileSdk = 37; minSdk = 24 } }`; the APK
  comes from a separate `com.android.application` module. AGP 9 has built-in Kotlin support — don't
  add `org.jetbrains.kotlin.android` to the Android module, only `org.jetbrains.kotlin.plugin.compose`.
- `repositories { }` goes inside `dependencyResolutionManagement { }` in `settings.gradle.kts`
  (`google()` + `mavenCentral()`), not at the settings top level.
- If you must write platform-suffixed coordinates, the web suffix is `-wasm-js`, not `-wasmjs` (the
  official getting-started doc has this wrong; the latter 404s).

Minimal theme skeleton:

```kotlin
import top.yukonga.miuix.kmp.theme.ColorSchemeMode
import top.yukonga.miuix.kmp.theme.MiuixTheme
import top.yukonga.miuix.kmp.theme.ThemeController

// Use the controller overload, not MiuixTheme(colors = ...) — see hard rule 6
MiuixTheme(controller = remember { ThemeController(ColorSchemeMode.System) }) {  // follow the system light/dark
    // every Miuix component goes inside this
}
```

Custom colors: `ThemeController(lightColors = lightColorScheme(primary = ...), darkColors = darkColorScheme(...))`.
System dynamic color (Material You): `ThemeController(ColorSchemeMode.MonetSystem, keyColor = ...)`.

## Versions

This skill's data matches **the miuix 0.9.4 release on Maven Central** (git tag `v0.9.4`, 2026-09-20).
Every patch release in the 0.9.x line carries source-level breaking changes — don't assume
signatures are stable across versions:

- **0.9.4-rc01 → 0.9.4**: `NavigationRail` split from "one function + a nullable `state`" into two
  overloads — `NavigationRail(expanded = …)` (stateless) and `NavigationRail(state = …)` (`state`
  required, non-null). 0.9.4 added the `Modifier.pagerGestureOverride` family and
  `LocalNavTransitionScope`.
- **Not yet released, on `main`** (for the next version; 0.9.4 users must not copy this):
  `BreadcrumbBar`'s `scrollState: ScrollState?` becomes `listState: LazyListState?`; each
  `pagerGestureOverride` overload gains a required `flingBehavior`,
  `PagerInterceptionMode.CrossAxisInterceptor` is renamed `CrossAxis`, and
  `horizontalPagerSwipeOverride` is removed; `TabRow` only consumes leftover horizontal scroll while
  it can still scroll itself; `NavDisplay` clears focus when the top of the stack changes. If a
  project depends on a snapshot or newer version, treat the source as authoritative.

## Look up a component

The reference is split by topic into a dozen-odd files, each kept under a bit over a thousand lines.
Start at `references/index.md`: the topic table plus which symbols each file contains.
`references/recipes.md` is the hand-written combination recipes; the rest are generated from source.

- **Find a symbol**: grep the section headings across files, then pull that section:

  ```bash
  grep -rn "^## Switch  " <skill>/references/            # -> references/ui-input.md:<line>
  sed -n "<line>,+60p" <skill>/references/ui-input.md
  ```

- **Build a kind of UI**: read the whole topic file. Settings screens → `preference.md`, page
  skeleton → `ui-scaffold.md`, overlays → `ui-overlay.md`, bottom / side / tab bars →
  `ui-navigation.md`, page switching and transitions → `nav.md`.

Each section contains: the real generated signature (required params marked `// required`), the
KDoc, the full factory parameters of `XxxDefaults`, traps (with `file:line` evidence), visual specs,
the state model, differences from Material3, and links to compilable examples. The end of each topic
file lists that topic's public types and their `import` paths.

Source locations and examples link to the corresponding line at `v0.9.4` on GitHub. To read the
source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.
Prefer the miuix repo's `docs/demo/**` and `example/shared/**` for examples (compilable Gradle
subprojects); the examples in the official `docs/*.md` have rotted (28 verified spots fail to compile
if copied), so don't copy them.

## Choosing between options

### Overlay\* or Window\*

Every overlay has two identically-named variants:

| | `Overlay*` | `Window*` |
| --- | --- | --- |
| Rendered where | inside the Compose tree, on the Scaffold's popupHost | a platform Dialog / separate window |
| Must be inside a Scaffold | **yes** — outside a Scaffold it **fails silently and never shows** | no, works anywhere |
| Can extend past the host window bounds | no | yes |
| When to pick it | you're certain you're inside a Scaffold and want it clipped with the page and part of the Scaffold layering | **when unsure, pick this** |

Covers `OverlayDialog` / `OverlayBottomSheet` / `OverlayListPopup` / `OverlayCascadingListPopup` and
their `Window*` counterparts. Dialogs have no confirm / dismiss button slots — arrange the buttons
yourself in the content: a `Row` with two `TextButton`s each `Modifier.weight(1f)`, the confirm
button using `ButtonDefaults.textButtonColorsPrimary()` (this is exactly how the template's `App.kt`
does it).

### Preference components

`miuix-preference` is **not** the counterpart of androidx.preference: **zero persistence, purely
controlled**. You own the state and storage; the components only display and call back.

Pick by the action area: `ArrowPreference` (navigate), `SwitchPreference`, `CheckboxPreference`,
`RadioButtonPreference`, `SliderPreference` / `RangeSliderPreference`, `OverlayDropdownPreference` /
`OverlaySpinnerPreference` (and the `Window*` versions).

Group corners are **not** the component's job — wrap them in a `Card` to clip them together.

### Gesture conflicts inside HorizontalPager

When a page has a vertical list, a horizontal swipe during that list's fling or overscroll won't
change the page. Since 0.9.4, use `Modifier.pagerGestureOverride`
(`import top.yukonga.miuix.kmp.utils.pagerGestureOverride`, see `references/ui-utils.md`). The
default `CrossAxisInterceptor` mode **requires both** disabling the Pager's own gesture and attaching
the dedicated nested-scroll connection — miss either and gestures conflict:

```kotlin
HorizontalPager(
    state = pagerState,
    modifier = Modifier.pagerGestureOverride(pagerState),
    userScrollEnabled = false,
    pageNestedScrollConnection = PagerGestureNestedScrollConnection,
) { page -> /* e.g. a LazyColumn */ }
```

When switching to `PagerInterceptionMode.Native` or `TapToHalt`, restore those two to the Pager
defaults.

⚠️ In 0.9.4 the `CrossAxisInterceptor` grabs the horizontal drag at `PointerEventPass.Initial`
(parent before child): **horizontally swipeable components in the page (a horizontal `LazyRow`,
`Slider`, a carousel) become un-swipeable**. When a page has such components, use `TapToHalt` instead
(it only halts during the child list's fling and is the native Pager gesture the rest of the time),
or move the horizontal component outside the Pager. To change page from a tab tap, use
`pagerState.springAnimateToPage(page)` (suspend; Miuix spring; a silent no-op on an out-of-range
page, no exception). Bind the bottom bar / tab selected state to `pagerState.targetPage` so the
indicator lands on the target on switch; binding `currentPage` walks through each page. Full
skeleton (bottom bar + pager + collapsing top bar) is in `references/recipes.md`. This API changes
signatures in the next version (see "Versions").

### Icons

- `MiuixIcons.Basic.*` has only 7, from **miuix-ui**: `ArrowRight ArrowUpDown Check Close Search SearchCleanup Sidebar`
- The other 936 are in the separate **miuix-icons** module: `MiuixIcons.<IconName>` or
  `MiuixIcons.<Weight>.<IconName>`, weight being `Light` / `Normal` / `Regular` / `Medium` /
  `Demibold` (156 each)
- Icons are extension properties, so import two things: `top.yukonga.miuix.kmp.icon.MiuixIcons`, and
  `top.yukonga.miuix.kmp.icon.extended.<IconName>` (miuix-icons) or
  `top.yukonga.miuix.kmp.icon.basic.<IconName>` (Basic)
- ⚠️ `Close`, `Search`, `Sidebar` exist in **both modules**. A wrong receiver won't error — it
  silently resolves to the other icon
- ⚠️ Before using `MiuixIcons.*`, confirm `miuix-icons` is included — `miuix-ui` does not bring it transitively
- When unsure of an icon name, grep `references/icons.md`; **don't write from memory**. For which
  icon fits a meaning like "home / discover / me / settings", see the mapping table in
  `references/recipes.md` (`MiuixIcons.Save` and `MiuixIcons.Basic.Audio` don't exist, yet both
  appear in the official docs)

## Hard rules

1. **Nullable type ≠ omittable parameter.** `onCheckedChange: ((Boolean) -> Unit)?` has no default
   and must be passed. Look at the `// required` marker, not the trailing `?` on the type.
2. **Don't read colors with `colors.xxxColor`.** The constructor params of `XxxColors` are all
   `private val` and the getters are `internal`. Those names are only usable as **named arguments**
   to `XxxDefaults.xxxColors(...)`.
3. **There is no ripple.** Miuix uses `MiuixIndication` (an alpha overlay) instead, plus
   `SinkFeedback` / `TiltFeedback`. Copying Material3's ripple approach breaks the HyperOS feel.
4. **Corners go through squircle, not Shape.** Use the `Modifier.squircleClip()` family, not
   `RoundedCornerShape`.
5. **The source KDoc itself has known errors.** At least 3 KDoc comments contradict the signature
   right below them (`TextureEffect.kt`'s `contentBlendMode`, `Pressable.kt`'s default indication,
   `ListPopup.kt`'s `Align`). When KDoc and signature conflict, **trust the signature**, and check
   the traps for that topic in `references/` for a recorded note.
6. **The two `MiuixTheme` overloads are not equivalent.** `MiuixTheme(controller = ...)` provides
   `LocalContentColor` and `LocalColorSchemeMode`; `MiuixTheme(colors = ...)` **provides neither**.
   The consequence of the latter: in dark mode, text and icons that read `LocalContentColor` stay
   black; and `MiuixTheme.isDynamicColor` is always false, which is exactly what factories like
   `SwitchDefaults.switchColors()` branch on. **Always use the controller overload.**
7. **Compile after changing.** Don't declare done on signature-matching alone. Fastest check: KMP
   project `./gradlew :composeApp:compileKotlinJvm` (with a desktop target) or
   `:composeApp:compileAndroidMain`; plain Android `./gradlew :app:compileDebugKotlin`; then
   `assembleDebug` when you need an APK.
