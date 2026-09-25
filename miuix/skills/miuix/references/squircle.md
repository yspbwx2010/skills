# Smooth corners

miuix-squircle: the squircle shape and clipping. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## Modifier.absoluteSquircleBackground  ·  smooth corners

absoluteSquircleBackground / absoluteSquircleClip / absoluteSquircleSurface -- parameters are named by physical corner (topLeft/topRight/bottomRight/bottomLeft) and explicitly do not flip with LayoutDirection.

> Absolute-positioning variant of [squircleBackground]. Corner parameters are physical
> (clockwise from top-left) and are NOT flipped by `LocalLayoutDirection` — mirrors
> `AbsoluteRoundedCornerShape`. Reach for this when corners are anchored to physical sides
> regardless of layout direction (e.g. transition reveals tied to a swipe edge).

```kotlin
import top.yukonga.miuix.kmp.squircle.absoluteSquircleBackground

@Composable
fun Modifier.absoluteSquircleBackground(
    color: Color,  // required
    topLeft: Dp,  // required
    topRight: Dp,  // required
    bottomRight: Dp,  // required
    bottomLeft: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `color` — The fill [Color] of the squircle background.
- `topLeft` — The physical top-left corner radius, never flipped by `LocalLayoutDirection`.
- `topRight` — The physical top-right corner radius, never flipped by `LocalLayoutDirection`.
- `bottomRight` — The physical bottom-right corner radius, never flipped by `LocalLayoutDirection`.
- `bottomLeft` — The physical bottom-left corner radius, never flipped by `LocalLayoutDirection`.
- `extension` — The corner-tile size as a multiple of each corner radius, clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Traps**

- 🟡 On the shader path, the absolute variant and the relative variant produce identical output (the relative variant does not flip to begin with). The only real difference is in the API<33 fallback branch: absolute uses AbsoluteRoundedCornerShape, relative uses RoundedCornerShape (which flips). In other words, the value of the absolute variant is that its fallback path also does not flip, not that it does anything more than the relative variant.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:193`)
- ⚪ The parameter order is clockwise from top-left: topLeft, topRight, bottomRight, bottomLeft. It maps one-to-one with the relative variant's topStart, topEnd, bottomEnd, bottomStart positions, so under LTR you can just swap names without changing order.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:169`)

**Spec** 

**State** Stateless, identical to the corresponding relative variant.

**vs Material3** Corresponds to AbsoluteRoundedCornerShape with background/clip.

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:182`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L182)</sub>

## Modifier.absoluteSquircleClip  ·  smooth corners

absoluteSquircleBackground / absoluteSquircleClip / absoluteSquircleSurface -- parameters are named by physical corner (topLeft/topRight/bottomRight/bottomLeft) and explicitly do not flip with LayoutDirection.

> Absolute-positioning variant of [squircleClip]. See [absoluteSquircleBackground] for semantics.

```kotlin
import top.yukonga.miuix.kmp.squircle.absoluteSquircleClip

@Composable
fun Modifier.absoluteSquircleClip(
    topLeft: Dp,  // required
    topRight: Dp,  // required
    bottomRight: Dp,  // required
    bottomLeft: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `topLeft` — The physical top-left corner radius, never flipped by `LocalLayoutDirection`.
- `topRight` — The physical top-right corner radius, never flipped by `LocalLayoutDirection`.
- `bottomRight` — The physical bottom-right corner radius, never flipped by `LocalLayoutDirection`.
- `bottomLeft` — The physical bottom-left corner radius, never flipped by `LocalLayoutDirection`.
- `extension` — The corner-tile size as a multiple of each corner radius, clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Traps**

- 🟡 On the shader path, the absolute variant and the relative variant produce identical output (the relative variant does not flip to begin with). The only real difference is in the API<33 fallback branch: absolute uses AbsoluteRoundedCornerShape, relative uses RoundedCornerShape (which flips). In other words, the value of the absolute variant is that its fallback path also does not flip, not that it does anything more than the relative variant.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:193`)
- ⚪ The parameter order is clockwise from top-left: topLeft, topRight, bottomRight, bottomLeft. It maps one-to-one with the relative variant's topStart, topEnd, bottomEnd, bottomStart positions, so under LTR you can just swap names without changing order.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:169`)

**Spec** 

**State** Stateless, identical to the corresponding relative variant.

**vs Material3** Corresponds to AbsoluteRoundedCornerShape with background/clip.

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:209`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L209)</sub>

## Modifier.absoluteSquircleSurface  ·  smooth corners

absoluteSquircleBackground / absoluteSquircleClip / absoluteSquircleSurface -- parameters are named by physical corner (topLeft/topRight/bottomRight/bottomLeft) and explicitly do not flip with LayoutDirection.

> Absolute-positioning variant of [squircleSurface]. See [absoluteSquircleBackground] for semantics.

```kotlin
import top.yukonga.miuix.kmp.squircle.absoluteSquircleSurface

@Composable
fun Modifier.absoluteSquircleSurface(
    color: Color,  // required
    topLeft: Dp,  // required
    topRight: Dp,  // required
    bottomRight: Dp,  // required
    bottomLeft: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `color` — The fill [Color] drawn behind the clipped content.
- `topLeft` — The physical top-left corner radius, never flipped by `LocalLayoutDirection`.
- `topRight` — The physical top-right corner radius, never flipped by `LocalLayoutDirection`.
- `bottomRight` — The physical bottom-right corner radius, never flipped by `LocalLayoutDirection`.
- `bottomLeft` — The physical bottom-left corner radius, never flipped by `LocalLayoutDirection`.
- `extension` — The corner-tile size as a multiple of each corner radius, clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Traps**

- 🟡 On the shader path, the absolute variant and the relative variant produce identical output (the relative variant does not flip to begin with). The only real difference is in the API<33 fallback branch: absolute uses AbsoluteRoundedCornerShape, relative uses RoundedCornerShape (which flips). In other words, the value of the absolute variant is that its fallback path also does not flip, not that it does anything more than the relative variant.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:193`)
- ⚪ The parameter order is clockwise from top-left: topLeft, topRight, bottomRight, bottomLeft. It maps one-to-one with the relative variant's topStart, topEnd, bottomEnd, bottomStart positions, so under LTR you can just swap names without changing order.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:169`)

**Spec** 

**State** Stateless, identical to the corresponding relative variant.

**vs Material3** Corresponds to AbsoluteRoundedCornerShape with background/clip.

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:233`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L233)</sub>

## Path.addSquircleRect  ·  smooth corners

Appends a squircle outline to a Path. The only public API in the module that needs no shader, intended for per-frame path scenarios such as clipPath reveal animations.

> Appends a squircle-shaped rounded rectangle path. Use this for path-based effects that can't
> ride the shader pipeline (e.g. `clipPath` reveals rebuilt per frame); for static fills/clips
> prefer the modifier APIs.
> 
> Pass `squircleEnabled = false` (typically forwarded from [isSquircleEnabled]) to append a
> plain rounded rectangle of the same dimensions instead — useful when the surrounding visuals
> use the shader-backed modifiers' fallback path.

```kotlin
import top.yukonga.miuix.kmp.squircle.addSquircleRect

fun Path.addSquircleRect(
    width: Float,  // required
    height: Float,  // required
    cornerRadius: Float,  // required
    extension: Float = SquircleDefaults.Extension,
    squircleEnabled: Boolean = true,
)
```

- `width` — The width of the rectangle in pixels; nothing is appended when not positive.
- `height` — The height of the rectangle in pixels; nothing is appended when not positive.
- `cornerRadius` — The corner radius in pixels, clamped to half the smaller side.
- `extension` — The corner-tile size as a multiple of [cornerRadius], clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].
- `squircleEnabled` — When `false`, appends a plain rounded rectangle instead of the squircle   silhouette; typically forwarded from [isSquircleEnabled].

**Traps**

- 🔴 All size parameters are pixels, not Dp (width/height/cornerRadius: Float). Passing the value 16f from 16.dp directly gives you a 16px corner. Inside DrawScope/CacheDrawScope use cornerRadius.toPx().  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquirclePath.kt:49`)
- 🔴 squircleEnabled defaults to true and does not read the CompositionLocal. It is a plain extension function and cannot read LocalSquircleEnabled, so when the user turns off the global switch or runs on Android<33, this path still draws a squircle while the surrounding modifiers have already fallen back to rounded corners -- you must call isSquircleEnabled() in the composable and pass it in explicitly.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquirclePath.kt:54`)
- ⚪ The squircleEnabled=false fallback branch uses cornerRadius without multiplying by extension, while the squircle branch uses cornerRadius×extension. Toggling the switch makes every corner's visual size jump by 10%.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquirclePath.kt:58`)
- 🟡 The outline it draws has none of the shader path's circle blending, so at capsule/pill sizes where r approaches halfMin it does not line up with an adjacent squircleSurface/squircleClip (ListPopup's clipPath reveal hits exactly this).  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquirclePath.kt:30`)
- ⚪ The path is clockwise, starts at (tile, 0) and close()s, with the coordinate origin fixed at (0,0). To draw elsewhere you must translate yourself; the function accepts no offset. When width/height<=0 it silently appends nothing.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquirclePath.kt:56`)

**Spec** tile tile = cornerRadius × extension, then clamped to min(w,h)/2; when tile<=0 it degrades to a plain rectangle · handle handle = tile × (1 - 0.643) = 0.357 × tile

**State** Stateless, pure Path construction.

**vs Material3** Corresponds to Path.addRoundRect(RoundRect(...)).

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquirclePath.kt:49`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquirclePath.kt#L49)</sub>

## isSquircleEnabled  ·  smooth corners

A @Composable @ReadOnlyComposable switch query: LocalSquircleEnabled.current && isRuntimeShaderSupported(). Only useful when you need to pass this boolean to the non-Composable Path.addSquircleRect.

> Whether shader-backed squircle silhouettes are active in the current composition — combines
> [LocalSquircleEnabled] with the platform's [isRuntimeShaderSupported] check. Forward the result
> to [Path.addSquircleRect] when mixing the path builder with the modifier APIs.

```kotlin
import top.yukonga.miuix.kmp.squircle.isSquircleEnabled

@Composable
fun isSquircleEnabled(): Boolean
```

**Traps**

- 🟡 It does not just read the user switch, it also ANDs in the platform capability. On Android<33 it is always false, even when LocalSquircleEnabled is true. To check user intent alone, read LocalSquircleEnabled.current directly.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/LocalSquircleEnabled.kt:27`)
- ⚪ LocalSquircleEnabled is a staticCompositionLocalOf, not a compositionLocalOf -- when its value changes, the entire subtree that reads it recomposes, with no fine-grained invalidation. That is correct for a global switch, but do not use it as per-frame changing state.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/LocalSquircleEnabled.kt:18`)

**Spec** 

**State** Read-only, stateless. Default value true.

**vs Material3** No equivalent.

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/LocalSquircleEnabled.kt:27`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/LocalSquircleEnabled.kt#L27)</sub>

## Modifier.squircleBackground  ·  smooth corners

A smooth rounded-corner background that only fills, never clips. To also clip child content at the corners you must use squircleSurface or squircleClip; with this modifier the area outside the corners still paints child content.

> Squircle solid background — fill-only, descendants are NOT clipped.
> 
> Falls back to `Modifier.background(color, RoundedCornerShape(cornerRadius))`
> when runtime shaders are unavailable (Android < API 33).

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleBackground

@Composable
fun Modifier.squircleBackground(
    color: Color,  // required
    cornerRadius: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `color` — The fill [Color] of the squircle background.
- `cornerRadius` — The radius applied uniformly to all four corners.
- `extension` — The corner-tile size as a multiple of [cornerRadius]: 1.0 matches a circular   arc, 1.1 is the default continuous-corner look. Clamped to [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Traps**

- 🔴 Using it as a clip. The first sentence of the KDoc states fill-only, descendants are NOT clipped -- child content (images, ripples, child backgrounds) still paints outside the corners, making it look like the rounding did not take effect. To clip child content too, use squircleSurface (fill + clip) or squircleClip (clip only).  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:40`)
- 🔴 Assuming topStart/topEnd flip under RTL. The KDoc for all four parameters says flipped by LocalLayoutDirection, but the entire miuix-squircle module never reads LocalLayoutDirection (grep only hits the KDoc string). The shader path maps by fixed physical position (index 0 is always top-left), while the API<33 fallback path uses a real RoundedCornerShape, which does flip -- so the same component looks different under RTL before and after Android 33. For deterministic behavior, use absoluteSquircleBackground directly.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:61`)
- 🟡 Assuming extension=1.0 gives a standard circular arc. The KDoc says 1.0 matches a circular arc, but extension only enlarges the corner tile size and never changes the control-handle ratio of that cubic Bézier, SQUIRCLE_CONTROL=0.643 (a circular arc needs 0.5523). At e=1.0 the 45° direction is still about 11.6% shallower than a circular arc, and the endpoint curvature is 0.576/r instead of 1/r.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:47`)
- 🟡 Assuming a larger extension gets closer to a superellipse. The direction is exactly the opposite: the circle-blend threshold is cornerSize > (π/4)·halfMin, and cornerSize = r×extension, so a larger extension blends toward a pure circle sooner. The default Button (r=16dp, height 40dp) at e=1.1 has blendWeight≈0.44 -- 44% is already pure circle; pushing e to 2.0 saturates the weight straight to 1.0 and the squircle component drops to zero.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:406`)
- ⚪ Using it on every item in a long list. The SquircleShaderBrush constructor calls RuntimeShader(SQUIRCLE_SHADER), and on Android that constructor compiles AGSL on the spot, with no process-level cache at this layer (Skiko has a RuntimeEffect cache, Android does not). The brush is remember(color, tiles) per call site, so 50 Cards = 50 AGSL compilations; a theme-color change rebuilds them all.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:392`)

**Spec** extension Default 1.1 (SquircleDefaults.Extension), clamped to 1.0..2.0 · control SQUIRCLE_CONTROL = 0.643f, manually kept in lockstep with the build-time baked SDF's control.set(0.643f), with no test guarding it · blend_threshold BLEND_THRESHOLD_RATIO = 0.7853982f (π/4); once cornerSize/halfMin exceeds it, blending toward a pure circle begins, reaching a pure circle at 1.0

**State** Stateless. A @Composable modifier; internally rememberSquircleBrush memoizes on (color, four-corner Dp, extension, density); when unsupported it returns null and falls back to Modifier.background(color, RoundedCornerShape(cornerRadius)). Note the fallback uses r without multiplying by extension, so its corners are 10% smaller than the main path, and toggling LocalSquircleEnabled makes the corners visibly jump.

**vs Material3** Corresponds to Modifier.background(color, RoundedCornerShape(r)). Difference: M3 goes through Shape/Outline and can be passed to any API that takes a Shape; miuix-squircle exports no Shape implementation, only a Modifier, so it cannot be fed to parameters like Surface(shape=) or drawBackdrop(shape=).

**Compilable examples** [`example/shared/src/commonMain/kotlin/ColorPage.kt:271`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L271) · [`example/shared/src/commonMain/kotlin/utils/FPSMonitor.kt:93`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/FPSMonitor.kt#L93)

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L51)</sub>

## Modifier.squircleBackground  ·  smooth corners

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Per-corner variant of [squircleBackground]. Ordering matches [RoundedCornerShape].

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleBackground

@Composable
fun Modifier.squircleBackground(
    color: Color,  // required
    topStart: Dp,  // required
    topEnd: Dp,  // required
    bottomEnd: Dp,  // required
    bottomStart: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `color` — The fill [Color] of the squircle background.
- `topStart` — The corner radius of the top-start corner (flipped by `LocalLayoutDirection`).
- `topEnd` — The corner radius of the top-end corner (flipped by `LocalLayoutDirection`).
- `bottomEnd` — The corner radius of the bottom-end corner (flipped by `LocalLayoutDirection`).
- `bottomStart` — The corner radius of the bottom-start corner (flipped by `LocalLayoutDirection`).
- `extension` — The corner-tile size as a multiple of each corner radius, clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Compilable examples** [`example/shared/src/commonMain/kotlin/ColorPage.kt:271`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L271) · [`example/shared/src/commonMain/kotlin/utils/FPSMonitor.kt:93`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/FPSMonitor.kt#L93)

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:69`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L69)</sub>

## Modifier.squircleBorder  ·  smooth corners

A smooth rounded-corner border. A pure Path implementation that needs no shader, but is still gated by the shader capability to keep its fallback consistent with the fill APIs.

> Squircle stroke around this layout, inset by half the stroke width so it lines up with a
> same-radius [squircleBackground] / [squircleSurface]. Path-based; no shader required, rebuilt
> only when size changes. Falls back to `Modifier.border(...)` with `RoundedCornerShape` whenever
> [isSquircleEnabled] is `false`, keeping borders aligned with the fill APIs' fallback.

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleBorder

@Composable
fun Modifier.squircleBorder(
    width: Dp,  // required
    color: Color,  // required
    cornerRadius: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `width` — The stroke width of the border.
- `color` — The stroke [Color] of the border.
- `cornerRadius` — The radius applied uniformly to all four corners.
- `extension` — The corner-tile size as a multiple of [cornerRadius], clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Traps**

- 🟡 The border and a same-radius squircleSurface do not coincide at common sizes. The fill goes through the shader with circle blending (the default Button at r=16dp/height 40dp is 44% pure circle), while the border goes through addSquircleRect with no blending logic at all, so the two outlines differ by about 0.021×tile in the 45° direction (a visible offset on a 1dp thin border).  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBorder.kt:49`)
- ⚪ The two overloads have different fallback paths. The first (width: Dp, color: Color), when isSquircleEnabled()==false, swaps entirely to Modifier.border(width, color, RoundedCornerShape(cornerRadius)); the second (the lambda version) does not swap the modifier but passes squircleEnabled into addSquircleRect to draw a rounded-rectangle border path. The same parameters give visually inconsistent fallbacks across the two overloads.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBorder.kt:36`)
- ⚪ cornerRadius is the radius of the border's outer edge, not its centerline: internally it draws with cornerRadiusPx - halfStroke and translates the whole thing by translate(halfStroke). To align the border's outer edge with a fill of radius r, pass r directly, do not subtract yourself.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBorder.kt:48`)

**Spec** 

**State** Stateless. The lambda overload (width: () -> Dp, color: () -> Color) reads its values only inside onDrawBehind, so driving the border with animateDpAsState/animateColorAsState does not trigger recomposition -- prefer it for animated scenarios.

**vs Material3** Corresponds to Modifier.border(width, color, RoundedCornerShape(r)).

**Compilable examples** [`example/shared/src/commonMain/kotlin/ColorPage.kt:272`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L272)

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBorder.kt:30`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBorder.kt#L30)</sub>

## Modifier.squircleBorder  ·  smooth corners

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Deferred-read variant of [squircleBorder]. [width] and [color] are sampled inside the draw
> scope, so animating either via `animateDpAsState` / `animateColorAsState` updates the stroke
> without recomposing this composable or its subtree. Falls back to a stroked rounded-rect path
> (rather than [Modifier.border]) when [isSquircleEnabled] is `false`.

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleBorder

@Composable
fun Modifier.squircleBorder(
    width: () -> Dp,  // required
    color: () -> Color,  // required
    cornerRadius: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `width` — Lambda returning the stroke width, read inside the draw scope each frame.
- `color` — Lambda returning the stroke [Color], read inside the draw scope each frame.
- `cornerRadius` — The radius applied uniformly to all four corners.
- `extension` — The corner-tile size as a multiple of [cornerRadius], clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Compilable examples** [`example/shared/src/commonMain/kotlin/ColorPage.kt:272`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L272)

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBorder.kt:80`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBorder.kt#L80)</sub>

## Modifier.squircleClip  ·  smooth corners

Masks child content to a smooth rounded-corner outline. Note it is an alpha mask (BlendMode.DstIn), not a true outline clip.

> Clips the subtree to the squircle silhouette.
> 
> Falls back to `Modifier.clip(RoundedCornerShape(cornerRadius))` when
> runtime shaders are unavailable.

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleClip

@Composable
fun Modifier.squircleClip(
    cornerRadius: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `cornerRadius` — The radius applied uniformly to all four corners.
- `extension` — The corner-tile size as a multiple of [cornerRadius], clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Traps**

- 🟡 Using it as Modifier.clip(shape). The implementation draws the content and then uses BlendMode.DstIn to multiply the corner alpha to 0, not a stencil/outline clip. The pixels outside the corners were actually drawn, just with alpha=0, and any subsequent non-SrcOver blend can still bring them back; when child content carries its own graphicsLayer(alpha=) or a non-SrcOver blendMode, the result differs from a true clip.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:333`)
- ⚪ When either side of the node exceeds 2048px it switches to a band path: the content is first recorded into a GraphicsLayer, then replayed with saveLayer in the top and bottom corner bands, while the straight-edge region in between opens no offscreen layer. The dst of DstIn differs between the two paths (a whole-node offscreen layer vs a band-height temporary layer), so results diverge when child content uses a non-SrcOver blend. Also the banding only cuts along the Y axis, so for a 4000×100 ultra-wide node each band's saveLayer width is still 4000px.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:261`)
- 🔴 RTL parameters do not flip, same as squircleBackground (the KDoc says they flip, the code does not, and the fallback path does flip instead).  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:104`)
- ⚪ Every node wastefully takes a GraphicsLayer. drawWithCache calls obtainGraphicsLayer() unconditionally, but it is only used on the >2048px band path. Button/Card/IconButton all go through the squircleSurface chain, so a single screen has dozens of unrecorded layers.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:269`)

**Spec** max_offscreen MAX_OFFSCREEN_PX = 2048f -- when the node's max(w,h) does not exceed it, the single-offscreen-layer fast path is used; above it, the band path

**State** Stateless. The fallback path is Modifier.clip(RoundedCornerShape(...)), which is a true outline clip and differs semantically from the main path (see above).

**vs Material3** Corresponds to Modifier.clip(RoundedCornerShape(r)). Difference: M3 is an outline clip, this modifier is an alpha mask.

**Compilable examples** [`example/shared/src/commonMain/kotlin/IconPage.kt:246`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L246) · [`example/shared/src/commonMain/kotlin/OverscrollLoadMorePage.kt:164`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/OverscrollLoadMorePage.kt#L164) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:191`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L191)

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:96`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L96)</sub>

## Modifier.squircleClip  ·  smooth corners

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Per-corner variant of [squircleClip].

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleClip

@Composable
fun Modifier.squircleClip(
    topStart: Dp,  // required
    topEnd: Dp,  // required
    bottomEnd: Dp,  // required
    bottomStart: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `topStart` — The corner radius of the top-start corner (flipped by `LocalLayoutDirection`).
- `topEnd` — The corner radius of the top-end corner (flipped by `LocalLayoutDirection`).
- `bottomEnd` — The corner radius of the bottom-end corner (flipped by `LocalLayoutDirection`).
- `bottomStart` — The corner radius of the bottom-start corner (flipped by `LocalLayoutDirection`).
- `extension` — The corner-tile size as a multiple of each corner radius, clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Compilable examples** [`example/shared/src/commonMain/kotlin/IconPage.kt:246`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L246) · [`example/shared/src/commonMain/kotlin/OverscrollLoadMorePage.kt:164`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/OverscrollLoadMorePage.kt#L164) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:191`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L191)

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:112`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L112)</sub>

## Modifier.squircleSurface  ·  smooth corners

The combination of squircleBackground + squircleClip: in a single offscreen layer it both fills the base color and masks the corners. Miuix's Button/Card/IconButton go through it.

> Fill + clip behind a squircle silhouette — drop-in replacement for
> `.clip(RoundedCornerShape(r)).background(color)` with a squircle outline.

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleSurface

@Composable
fun Modifier.squircleSurface(
    color: Color,  // required
    cornerRadius: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `color` — The fill [Color] drawn behind the clipped content.
- `cornerRadius` — The radius applied uniformly to all four corners.
- `extension` — The corner-tile size as a multiple of [cornerRadius], clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

**Traps**

- 🟡 Inherits all of squircleClip's pitfalls (alpha mask rather than outline clip, 2048px banding, RTL does not flip, wasted GraphicsLayer). The fallback path is clip(RoundedCornerShape(...)).background(color), using the radius without multiplying by extension.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:162`)
- 🟡 When you want to background-blur a squircle region, squircleSurface and drawBackdrop cannot connect: miuix-squircle exports no Shape, and drawBackdrop's shape parameter only accepts a Shape. You can only wrap another squircleClip around drawBackdrop -- and then drawBackdrop's internal clipping and edge highlight still follow the RoundedCornerShape outline, which does not line up with the outer squircle.  (`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:152`)

**Spec** 

**State** Stateless.

**vs Material3** Corresponds to Modifier.clip(shape).background(color), or M3's Surface(shape=, color=).

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:134`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L134)</sub>

## Modifier.squircleSurface  ·  smooth corners

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Per-corner variant of [squircleSurface].

```kotlin
import top.yukonga.miuix.kmp.squircle.squircleSurface

@Composable
fun Modifier.squircleSurface(
    color: Color,  // required
    topStart: Dp,  // required
    topEnd: Dp,  // required
    bottomEnd: Dp,  // required
    bottomStart: Dp,  // required
    extension: Float = SquircleDefaults.Extension,
): Modifier
```

- `color` — The fill [Color] drawn behind the clipped content.
- `topStart` — The corner radius of the top-start corner (flipped by `LocalLayoutDirection`).
- `topEnd` — The corner radius of the top-end corner (flipped by `LocalLayoutDirection`).
- `bottomEnd` — The corner radius of the bottom-end corner (flipped by `LocalLayoutDirection`).
- `bottomStart` — The corner radius of the bottom-start corner (flipped by `LocalLayoutDirection`).
- `extension` — The corner-tile size as a multiple of each corner radius, clamped to   [SquircleDefaults.ExtensionMin]..[SquircleDefaults.ExtensionMax].

<sub>Source [`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt:152`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/SquircleBackground.kt#L152)</sub>

## Top-level properties & CompositionLocals (1)

- `LocalSquircleEnabled = staticCompositionLocalOf { … }`  <sub>[`miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/LocalSquircleEnabled.kt:18`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-squircle/src/commonMain/kotlin/top/yukonga/miuix/kmp/squircle/LocalSquircleEnabled.kt#L18)</sub>

## Public types in this topic (1)

- `SquircleDefaults` **object** · `import top.yukonga.miuix.kmp.squircle.SquircleDefaults`

