# Core utilities

miuix-core: platform detection and other low-level helpers. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## getCornerRadiusBottom  ·  interaction utility

```kotlin
import top.yukonga.miuix.kmp.utils.getCornerRadiusBottom

fun getCornerRadiusBottom(
    context: Context,  // required
): Int
```

<sub>Source [`miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt#L51)</sub>

## getRoundedCorner  ·  interaction utility

Reads the device screen's physical corner radius. Used to align edge-hugging cards/navigation containers with the screen's corners.

> Returns the rounded corner of the current device.

```kotlin
import top.yukonga.miuix.kmp.utils.getRoundedCorner

@Composable
expect fun getRoundedCorner(): Dp
```

Platform impls: androidMain, commonMain, skikoMain

**Traps**

- 🔴 On all non-Android platforms it always returns 0.dp (the skiko actual is one line). Any layout that relies on it for visual alignment degrades to square corners on Desktop / iOS / Web, with no error. Provide a fallback value before using it.  (`miuix-core/src/skikoMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.skiko.kt:16`)
- 🟡 On Android it can also be 0: API 31+ goes through WindowInsets.getRoundedCorner(POSITION_BOTTOM_LEFT), and only when that returns nothing does it fall back to reading the system-private dimen rounded_corner_radius_bottom (a MIUI convention), returning 0 when that resource does not exist. In other words, on non-Xiaomi Android 11-and-below devices it is essentially always 0.  (`miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt:51`)
- ⚪ It reads only the bottom-left position, assuming all four corners have the same radius. On irregular screens (different top and bottom corners) it reads the wrong value.  (`miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt:39`)

**Spec** non_android always 0.dp

**State** @Composable read-only. On Android it is remember keyed on (context, rootWindowInsets), and insets changes (rotation, multi-window) recompute it.

**vs Material3** No equivalent. M3 does not expose the screen corner radius.

<sub>Source [`miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt:31`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt#L31)</sub>

## platform  ·  interaction utility

> Returns the current platform name.

```kotlin
import top.yukonga.miuix.kmp.utils.platform

expect fun platform(): Platform
```

Platform impls: androidMain, commonMain, desktopMain, iosMain, jsMain, macosMain, wasmJsMain

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:195`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L195) · [`example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt:329`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt#L329)

<sub>Source [`miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt:25`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt#L25)</sub>

## platformDialogProperties  ·  interaction utility

The platform default DialogProperties for Miuix's own dialogs. Together with RemovePlatformDialogDefaultEffects, the goal is to fully turn off the platform's default window animation and scrim so Miuix can draw its own.

> Returns platform-specific DialogProperties.

```kotlin
import top.yukonga.miuix.kmp.utils.platformDialogProperties

@Composable
expect fun platformDialogProperties(): DialogProperties
```

Platform impls: androidMain, commonMain, skikoMain

**Traps**

- 🔴 Both platforms set dismissOnBackPress to false. Using it to open a plain Dialog gives you a dialog the back key cannot close -- you must wire the close logic yourself (Miuix's dialog components go through the PredictiveBackHandler chain).  (`miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt:58`)
- 🟡 The DialogProperties fields returned by the two platforms are not the same: Android is (dismissOnBackPress=false, usePlatformDefaultWidth=false, decorFitsSystemWindows=false), skiko is (dismissOnBackPress=false, usePlatformDefaultWidth=false, usePlatformInsets=false, scrimColor=Transparent, animateTransition=false). The skiko version also carries @OptIn(ExperimentalComposeUiApi). Do not assume the two behave identically.  (`miuix-core/src/skikoMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.skiko.kt:25`)
- 🟡 Turning off the platform window animation and dim is not done in this function -- that is RemovePlatformDialogDefaultEffects() (on Android it changes the window's windowAnimations / dimAmount / FLAG_DIM_BEHIND, on skiko it is a no-op). Using platformDialogProperties without calling it means on Android you still see the system's window animation and scrim layered over Miuix's own animation.  (`miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt:64`)

**Spec** 

**State** A @Composable pure factory, stateless.

**vs Material3** Corresponds to constructing androidx.compose.ui.window.DialogProperties() directly. The difference is that these defaults are tuned for Miuix's self-drawn dialogs, not general defaults.

<sub>Source [`miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt:37`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt#L37)</sub>

## RemovePlatformDialogDefaultEffects  ·  interaction utility

> Removes platform default dialog effects such as window animations and dimming.
> 
> Platform implementations should clear default window animations and dim amount to ensure
> Miuix custom dialog animations and dim layer behave consistently across devices.

```kotlin
import top.yukonga.miuix.kmp.utils.RemovePlatformDialogDefaultEffects

@Composable
expect fun RemovePlatformDialogDefaultEffects()
```

Platform impls: androidMain, commonMain, skikoMain

<sub>Source [`miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.kt#L46)</sub>

## Top-level properties & CompositionLocals (1)

- `hasFocusReassignBug: Boolean`  <sub>[`miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt:24`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt#L24)</sub>

## Public types in this topic (8)

- `MiuixIcons` **object** · `import top.yukonga.miuix.kmp.icon.MiuixIcons`
- `MiuixIcons.Basic` **object** · `import top.yukonga.miuix.kmp.icon.MiuixIcons`
- `MiuixIcons.Demibold` **object** · `import top.yukonga.miuix.kmp.icon.MiuixIcons`
- `MiuixIcons.Light` **object** · `import top.yukonga.miuix.kmp.icon.MiuixIcons`
- `MiuixIcons.Medium` **object** · `import top.yukonga.miuix.kmp.icon.MiuixIcons`
- `MiuixIcons.Normal` **object** · `import top.yukonga.miuix.kmp.icon.MiuixIcons`
- `MiuixIcons.Regular` **object** · `import top.yukonga.miuix.kmp.icon.MiuixIcons`
- `Platform` **enum** — Android, IOS, Desktop, WasmJs, MacOS, Js · `import top.yukonga.miuix.kmp.utils.Platform`

## Notes on types & namespaces

### MiuixIcons

An icon namespace: a carrier with just six empty nested objects (Basic / Light / Normal / Regular / Medium / Demibold), with the actual icons attached as extension properties by two different modules.

**Traps**

- 🔴 MiuixIcons.Save does not exist. docs/components/icon.md:145 and the Chinese mirror both use it, but the Kotlin source across the repo has zero hits. The closest are MiuixIcons.Download / FileDownloads / TopDownloads.  (`miuix-core/src/commonMain/kotlin/top/yukonga/miuix/kmp/icon/MiuixIcons.kt:6`)
- 🔴 MiuixIcons.Basic.Audio does not exist. docs/components/sliderpreference.md:114 and rangesliderpreference.md:113 (4 places across the two language versions) use it, but the Basic group has only 7 in total: ArrowRight / ArrowUpDown / Check / Close / Search / SearchCleanup / Sidebar.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/icon/basic/Close.kt:14`)
- 🔴 The Basic group and the extended group belong to different modules: the MiuixIcons.Basic.* extension properties are in miuix-ui (package top.yukonga.miuix.kmp.icon.basic), and the rest are all in miuix-icons (package top.yukonga.miuix.kmp.icon.extended). Depending on miuix-ui only, writing MiuixIcons.Ok does not compile; depending on miuix-icons only, writing MiuixIcons.Basic.Search does not compile.  (`miuix-icons/src/commonMain/kotlin/top/yukonga/miuix/kmp/icon/extended/Close.kt:15`)
- 🔴 Close / Search / Sidebar exist in both groups and are two completely different graphics (Basic.Close is a 24x24 viewport, 2.2f round-cap stroked cross; extended's Close is a 1003.2 viewport filled path). The receivers differ (MiuixIcons.Basic.Close vs MiuixIcons.Close), and when both dependencies are present writing the wrong receiver silently compiles and draws the other icon -- harder to spot than a compile error. The Basic Icons table in docs/guide/icons.md only gives bare icon names and never states the receiver is MiuixIcons.Basic, which is the root cause of the two doc bugs above.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/icon/basic/Search.kt:14`)
- 🟡 Writing MiuixIcons.X bare gets an alias for the Regular weight (get() = MiuixIcons.Regular.X), not some neutral version. The five weights Light/Normal/Regular/Medium/Demibold are each a separate ImageVector, each with a file-level private var cache. The Basic group has no weight axis.  (`miuix-icons/src/commonMain/kotlin/top/yukonga/miuix/kmp/icon/extended/Home.kt:15`)
- ⚪ The extended group is one icon per file (156 files, about 780 ImageVectors across five weights), and the physical layout serves DCE/R8 tree-shaking -- only the icon extension properties actually referenced are retained, and adding the dependency does not mean all of them enter the package.  (`miuix-icons/src/commonMain/kotlin/top/yukonga/miuix/kmp/icon/extended/Add.kt:15`)

**Spec** weights Five weights Light / Normal / Regular / Medium / Demibold; bare MiuixIcons.X == MiuixIcons.Regular.X · basic_set The Basic group has 7 in total: ArrowRight, ArrowUpDown, Check, Close, Search, SearchCleanup, Sidebar (living in miuix-ui)

**State** They are all lazy val extension properties, built on first read and stored in a file-level private var (not thread-safe, worst case building once redundantly, with no correctness impact).

**vs Material3** Corresponds to androidx.compose.material.icons.Icons (five styles Filled/Outlined/Rounded/Sharp/TwoTone). Difference: M3's axis is style, Miuix's axis is stroke weight; and Miuix puts the Basic group in the UI module and the extended group in a separate module, requiring separate dependencies.

