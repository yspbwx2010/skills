# Blur

miuix-blur: background blur, progressive blur, highlight, sensor. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## RuntimeShader.asBrush  ·  blur

> Back-compat re-export.

```kotlin
import top.yukonga.miuix.kmp.blur.asBrush

fun RuntimeShader.asBrush(): ShaderBrush
```

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt#L62) · [`example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt:23`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt#L23)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt:28`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt#L28)</sub>

## RuntimeShader.asComposeShader  ·  blur

> Back-compat re-export.

```kotlin
import top.yukonga.miuix.kmp.blur.asComposeShader

fun RuntimeShader.asComposeShader(): Shader
```

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt:25`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt#L25)</sub>

## BackdropEffectScope.blendColors  ·  blur

Post-blur multi-layer tint. HyperOS frosted glass's coloring relies on it, with 40+ blend modes (including custom modes such as Lab space).

> Chains all blend color layers from [colors] as a single runtime shader pass. Up to
> [MAX_BLEND_LAYERS] entries are honored. Brightness and saturation in [colors] are
> folded into the blend shader's uniforms (separate from any [colorControls] you may
> have already chained).

```kotlin
import top.yukonga.miuix.kmp.blur.blendColors

fun BackdropEffectScope.blendColors(
    colors: BlurColors,  // required
)
```

- `colors` — The [BlurColors] whose blend layers and brightness/saturation drive the shader.   An empty blend-layer list is a no-op.

**Traps**

- 🟡 At most 8 layers (MAX_BLEND_LAYERS = 8), and extra entries are silently dropped -- the KDoc says Extra entries are dropped and the code is minOf(list.size, 8), with no exception and no log.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:26`)
- 🟡 BlurBlendMode.MiLuminance (203) is dead on the public API: the two uniforms it needs, uLuminanceAmount / uLuminanceValues, are hardcoded to 0f and (0,0,0,0), with no public way to set them. Adding a MiLuminance layer does nothing.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:362`)
- 🟡 BlurBlendMode.MiSaturation (201) / MiBrightness (202) reuse the BlurColors.saturation / BlurColors.brightness fields -- and in textureBlurEffect's standard recipe those same two fields have already been consumed once by colorControls before the blur. Adding layers of these two modes applies the same value twice (once before blur, once after).  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:360`)
- ⚪ When the blendColors list is empty the whole call is a no-op. So when BlurColors only set brightness/contrast/saturation but gave no blendColors, calling blendColors(colors) has no effect -- those three values are colorControls's job.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:260`)

**Spec** max_layers MAX_BLEND_LAYERS = 8 · mode_ranges 0-28 standard SkBlendMode (GPU hardware); 100-121 and 200-203 custom modes (go through the runtime shader, need isRuntimeShaderSupported())

**State** Stateless; caches the RenderEffect keyed by the BlurColors value (rebuilding the list every frame still hits the cache).

**vs Material3** No equivalent.

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:259`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt#L259)</sub>

## BackdropEffectScope.blur  ·  blur

A separable Gaussian blur in the effects DSL. Besides chaining a RenderEffect, it also sets downscaleFactor and padding -- the latter two affect other effects in the chain.

> Chains a separable Blur into the scope's [BackdropEffectScope.renderEffect],
> adjusts [BackdropEffectScope.padding] to cover the kernel reach, and updates
> [BackdropEffectScope.downscaleFactor]. Non-positive radii skip that axis.
> 
> Raising [BackdropEffectScope.padding] after [blur] is safe (the effect block re-runs once
> with the final padding), but raising it beforehand avoids the rebuild.
> 
> Typical use:
> ```
> Modifier.drawBackdrop(backdrop, shape = { shape }, effects = {
>     blur(20f * density)
> })
> ```

```kotlin
import top.yukonga.miuix.kmp.blur.blur

fun BackdropEffectScope.blur(
    radiusX: Float,  // required
    radiusY: Float = radiusX,
)
```

- `radiusX` — Horizontal blur radius in pixels.
- `radiusY` — Vertical blur radius in pixels. Defaults to [radiusX] for isotropic blur.

**Traps**

- 🔴 The parameter names are radiusX / radiusY (radiusY defaults to radiusX), there is no radius and no edgeTreatment. The docs docs/guide/blur.md:363 write blur(radius = 60f), and the extension table at :381 writes blur(radius, edgeTreatment) -- both parameter names have zero hits across the repo, and edgeTreatment was mistakenly copied from Compose's official Modifier.blur. The Chinese mirror docs/zh_CN/guide/blur.md:358/376 has the same error.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:46`)
- 🔴 The radius is in pixels, not dp. BackdropEffectScope extends Density, and the KDoc's example is exactly blur(20f * density). Writing blur(20f) directly gives only 6.7dp of blur on a 3x screen -- three times off from Modifier.textureBlur(blurRadius = 20f), which is in dp.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:43`)
- 🔴 It raises downscaleFactor. A runtimeShaderEffect chained after it receives coords in the downsampled layer's pixel space, so all pixel-unit uniforms (size, padding, corner radius, refraction bandwidth...) must be divided by downscaleFactor yourself, otherwise the geometry runs outside the layer and every sample hits transparent black. This is the biggest cognitive-load leak in this API.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt:109`)
- ⚪ Order has performance implications: raising padding after blur is safe but re-runs the entire effects block once; setting padding before blur saves that rebuild.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:33`)
- ⚪ blur(0f) is not zero-cost: when the radius is 0, createBlurEffect returns null and exits early (the `?: return` at :104 in the same file), but padding was already set to 13 beforehand, so the recording surface still gains 13px on each side. During a 0→20 radius animation the first frame wastefully records an extra ring.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:67`)

**Spec** 

**State** Stateless; it writes the scope's three fields renderEffect / padding / downscaleFactor. On Android<33 it simply returns, with no error.

**vs Material3** No equivalent.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt:423`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt#L423)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt#L46)</sub>

## BackdropEffectScope.colorControls  ·  blur

Pre-blur brightness/contrast/saturation adjustment. In the preset recipe it comes before blur and acts on the raw background.

> Applies brightness, contrast, and saturation adjustments to the backdrop.
> 
> Brightness is applied in linear (gamma 2.2) space via a runtime shader to avoid
> the hue shift a linear `ColorMatrix` offset would introduce.

```kotlin
import top.yukonga.miuix.kmp.blur.colorControls

fun BackdropEffectScope.colorControls(
    brightness: Float = 0f,
    contrast: Float = 1f,
    saturation: Float = 1f,
)
```

- `brightness` — Brightness adjustment applied in linear space. 0 (default) leaves brightness unchanged.
- `contrast` — Contrast multiplier. 1 (default) leaves contrast unchanged.
- `saturation` — Saturation multiplier. 1 (default) leaves saturation unchanged.

**Traps**

- ⚪ When all three values are default (brightness=0, contrast=1, saturation=1) the whole call is a no-op and does not even build a RenderEffect. To force this pass you must give a non-default value.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt:68`)
- ⚪ brightness is done in linear (gamma 2.2) space, not a simple linear ColorMatrix offset -- this is to avoid hue shift. So its values cannot be directly compared to M3/ColorMatrix brightness parameters.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt:56`)
- 🟡 The recipe order is intentional: colorControls before blur (acting on the raw background, avoiding blur smoothing over grading errors), blendColors after blur (as a tint over the result). When assembling your own effects block, moving colorControls after blur gives a different result.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:398`)

**Spec** 

**State** Stateless; it caches the RenderEffect on the scope keyed by the (brightness, contrast, saturation) triple.

**vs Material3** Corresponds to part of ColorFilter.colorMatrix, but M3's version is a linear-space matrix and its brightness introduces hue shift.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/liquid/Vibrancy.kt:13`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/Vibrancy.kt#L13)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt:63`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt#L63)</sub>

## Modifier.drawBackdrop  ·  blur

The middle layer of the blur system: a fully controllable background-drawing node where you write the effects block to decide the pipeline. Preset modifiers like textureBlur are thin wrappers over it.

> Applies a backdrop effect to this composable.

```kotlin
import top.yukonga.miuix.kmp.blur.drawBackdrop

fun Modifier.drawBackdrop(
    backdrop: Backdrop,  // required
    shape: () -> Shape,  // required
    effects: BackdropEffectScope.() -> Unit,  // required
    highlight: (BackdropEffectScope.() -> Highlight?)? = null,
    layerBlock: (GraphicsLayerScope.() -> Unit)? = null,
    onDrawBehind: (DrawScope.() -> Unit)? = null,
    onDrawBackdrop: DrawScope.(drawBackdrop: DrawScope.() -> Unit) -> Unit = DefaultOnDrawBackdrop,
    onDrawSurface: (DrawScope.() -> Unit)? = null,
    onDrawFront: (DrawScope.() -> Unit)? = null,
    contentBlendMode: BlendMode = BlendMode.SrcOver,
    progressiveGradient: ProgressiveBlur? = null,
    enabled: Boolean = true,
): Modifier
```

- `backdrop` — The [Backdrop] providing the background content to capture and blur.
- `shape` — The shape provider for the blur region clipping; re-read on each draw so an   animated shape stays current.
- `effects` — The effect pipeline applied to the captured backdrop, configured against a   [BackdropEffectScope] (e.g. [blur], [blendColors], [colorControls]).
- `highlight` — Optional edge highlight resolved against the [BackdropEffectScope] and painted   on top of the content; returning `null` skips drawing.
- `layerBlock` — Optional graphics layer transformation applied to this composable and inverted   on the backdrop sampling so the backdrop stays screen-aligned; safe to animate.
- `onDrawBehind` — Optional draw callback invoked before the blurred backdrop, behind it.
- `onDrawBackdrop` — Wraps the backdrop drawing call, letting callers transform or intercept the   recorded content; defaults to invoking it directly.
- `onDrawSurface` — Optional draw callback invoked after the blurred backdrop and before the   composable's own content.
- `onDrawFront` — Optional draw callback invoked last, on top of the content and highlight.
- `contentBlendMode` — The [BlendMode] used to composite the composable's content over the blur.   [BlendMode.DstIn] masks the blur by the content alpha (foreground blur).
- `progressiveGradient` — When non-null, renders the backdrop as a multi-level progressive   composite: graduated native Gaussian levels cross-faded along this gradient on the downscaled   layer, with a genuinely sharp full-resolution clear end — the blur strength ramps   continuously from full to pixel-sharp. Requires a matching [progressiveBlur] in [effects] (as   [Modifier.progressiveTextureBlur] wires) — it records the target radii the composite renders;   without one the gradient is ignored and [effects] draws uniformly.
- `enabled` — Whether the backdrop effect is active. When false, content draws normally without   blur. Also gated by [isRuntimeShaderSupported].

**Traps**

- 🟡 The whole node is ANDed with isRuntimeShaderSupported(). The enabled parameter is &&'d with it, so on Android<33 whatever enabled you pass it degrades to a pure pass-through (no layer built, draw calls drawContent directly). So you need not add your own platform check, but do not expect any effect on API<33 either.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:118`)
- 🔴 Passing progressiveGradient alone is ineffective. The KDoc clearly states it requires a matching progressiveBlur in effects -- when there is no progressiveBlur in the effects block the gradient is silently ignored and effects draws a uniform blur, with no error. Either pass the same gradient on both sides, or just use Modifier.progressiveTextureBlur.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:97`)
- 🔴 contentBlendMode is a non-null BlendMode, defaulting to SrcOver (not a nullable null). The sentinel value is SrcOver: drawBackdrop internally checks if (contentBlendMode == BlendMode.SrcOver) to take the plain drawContent(). The docs docs/guide/blur.md:417 write it as BlendMode? / default null; passing null fails to compile.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:113`)
- 🟡 layerBlock is used twice: once as a real Modifier.graphicsLayer applied to this component, and once passed into the node to inverse-transform the backdrop sampling (it only inverts rotationZ/scaleX/scaleY, not translation or rotationX/Y). So do not wrap another graphicsLayer around it doing the same scaling, or it scales twice; 3D rotation also cannot be inverted.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:121`)
- 🟡 onDrawBackdrop is called twice, in two different coordinate spaces: once on the downsampled recording surface (downscaleFactor of 1 or 2), and once on the progressive blur's full-resolution sharp-end overlay (always 1). The hook cannot get downscaleFactor and can only infer it from DrawScope.size, and the downsampled path additionally wraps a translate(scaledPadding) around it. The library's docs/ and example/ have zero usage samples for it.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:110`)
- 🟡 highlight is silently skipped on unsupported platforms rather than degrading to a flat-color stroke. HighlightStyle.color's KDoc promises Tint applied when no createShader is available, and createShader's KDoc says Return null to fall back to a flat color stroke, but drawHighlight, after getting null, does ?: return and draws nothing.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/highlight/HighlightDrawing.kt:36`)
- ⚪ The draw order is fixed: onDrawBehind → blurred background (+ sharp-end overlay) → onDrawSurface → drawContent (per contentBlendMode) → highlight → onDrawFront. The drawBackdrop section of docs/guide/blur.md only covers the four parameters backdrop/shape/effects/highlight, omitting the other 8 and the draw order.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:86`)

**Spec** 

**State** Stateless host. shape is () -> Shape (re-read every frame, the shape can animate), highlight is (BackdropEffectScope.() -> Highlight?)? (evaluated in the scope, can read size/shape/density and can animate with press progress) -- note that on the third-layer preset modifiers these two are simplified to a plain Shape / Highlight?.

**vs Material3** No equivalent. Compose's official Modifier.blur blurs its own content and does not sample the background; third-party libraries like HazeMaterials are the real counterpart.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/liquid/CombinedBackdrop.kt:34`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/CombinedBackdrop.kt#L34) · [`example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt:419`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt#L419)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:103`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt#L103)</sub>

## BackdropEffectScope.effect  ·  blur

> Chains an arbitrary [RenderEffect] onto the backdrop effect pipeline.

```kotlin
import top.yukonga.miuix.kmp.blur.effect

fun BackdropEffectScope.effect(
    effect: RenderEffect,  // required
)
```

- `effect` — The [RenderEffect] to chain onto [BackdropEffectScope.renderEffect].

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/liquid/Lens.kt:19`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/Lens.kt#L19)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt:102`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt#L102)</sub>

## isRuntimeShaderSupported  ·  blur

The single gating check for the whole shader capability set (blur, color blending, squircle fill). Android requires API 33, all other platforms are always true.

> Back-compat re-export.

```kotlin
import top.yukonga.miuix.kmp.blur.isRuntimeShaderSupported

fun isRuntimeShaderSupported(): Boolean
```

**Traps**

- 🟡 On Android it is API 33 (TIRAMISU), not 31. It carries @ChecksSdkIntAtLeast, so accessing API 33 symbols inside an if (isRuntimeShaderSupported()) { ... } block does not trigger the NewApi lint -- but this benefit only exists when importing directly from top.yukonga.miuix.kmp.shader; the same-named back-compat forwarder under the miuix-blur package is a plain common function that has lost this annotation.  (`miuix-shader/src/androidMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.android.kt:18`)
- 🟡 Non-Android platforms return true unconditionally, with no real detection. On Web (js/wasmJs), once WebGL is unavailable or the driver is blacklisted, SkSL compilation failure throws an exception directly rather than falling back -- this side has no failure exit at all (makeForShader has no try/catch and the cache does not cache failures).  (`miuix-shader/src/skikoMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.skiko.kt:18`)
- 🔴 The miuix-blur module's minSdk is hardcoded to 33 (not via BuildConfig.MIN_SDK), so an app with minSdk<33 depending on miuix-blur fails manifest merging and needs tools:overrideLibrary. miuix-squircle / miuix-shader have minSdk 24, and 33 is only a runtime gate for them.  (`miuix-blur/build.gradle.kts:31`)

**Spec** 

**State** Pure function, stateless.

**vs Material3** No equivalent. M3 has no equivalent capability detection; the official Modifier.blur is silently ineffective on unsupported platforms.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:192`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L192) · [`example/shared/src/commonMain/kotlin/LicensePage.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/LicensePage.kt#L54) · [`example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt:44`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt#L44) · [`example/shared/src/commonMain/kotlin/NavigateTestPage.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/NavigateTestPage.kt#L54)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt:31`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt#L31)</sub>

## Modifier.layerBackdrop  ·  blur

Records the content this composable draws into a LayerBackdrop's GraphicsLayer for drawBackdrop to sample. The capture side, which must be paired with rememberLayerBackdrop.

> Captures the content of this composable into the given [LayerBackdrop]'s graphics layer.
> Place this modifier on the container whose content should appear as the blurred background.

```kotlin
import top.yukonga.miuix.kmp.blur.layerBackdrop

fun Modifier.layerBackdrop(
    backdrop: LayerBackdrop,  // required
): Modifier
```

- `backdrop` — The [LayerBackdrop] whose graphics layer records this composable's content.

**Traps**

- 🔴 Draw order is part of correctness, yet the API surface gives no hint. It records only in its own draw phase, and the consumer side just takes the already-recorded layer. The subtree with layerBackdrop must be drawn before the blurred component within the same frame (typical structure: a Scaffold's content before its topBar); a reversed order neither errors nor flashes black, it just samples the previous frame's content -- visible only during scrolling/animation.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdropModifier.kt:58`)
- 🟡 The content is drawn twice: once with drawContent() straight to screen, and once recorded into a GraphicsLayer. This is a fixed per-frame cost, and this modifier has no enabled parameter -- once attached you keep paying. When blur is not needed (user disabled it, platform unsupported) you should branch with an if outside, so that when rememberBlurBackdrop returns null you do not attach it at all.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdropModifier.kt:59`)
- 🔴 If you forget to attach it, or after the node detaches, the drawBackdrop side silently draws nothing: the first thing LayerBackdrop.drawBackdrop does is layerCoordinates ?: return. The symptom is a blank blur region, with no log or exception.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdrop.kt:81`)

**Spec** 

**State** No self-held state; it writes the LayoutCoordinates into the passed-in LayerBackdrop and sets it to null on onDetach. Attaching the same LayerBackdrop in two places at once makes them overwrite each other's coordinates.

**vs Material3** No equivalent.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:141`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L141) · [`example/shared/src/commonMain/kotlin/AppContent.kt:500`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L500) · [`example/shared/src/commonMain/kotlin/ColorPage.kt:92`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L92) · [`example/shared/src/commonMain/kotlin/IconPage.kt:230`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L230)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdropModifier.kt:22`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdropModifier.kt#L22)</sub>

## BackdropEffectScope.noiseDither  ·  blur

Anti-banding noise dithering. It builds no RenderEffect and only writes noiseCoefficient to the scope; the actual application is decided by the draw path.

> Registers a noise dither pass with the given [coefficient]. Non-positive values are ignored.
> Noise is applied at full resolution after upscaling so each screen pixel gets independent
> dithering, which prevents banding visible at low blur radii.

```kotlin
import top.yukonga.miuix.kmp.blur.noiseDither

fun BackdropEffectScope.noiseDither(
    coefficient: Float,  // required
)
```

- `coefficient` — The noise dithering strength stored in [BackdropEffectScope.noiseCoefficient].   Values at or below 0 are ignored.

**Traps**

- ⚪ When coefficient <= 0 the whole call is ignored (it does not even write the field). To turn off noise on a chain, passing 0 is enough, no conditional branch needed.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:246`)
- 🟡 0.005 is a semantic boundary (NOISE_GRAIN_THRESHOLD): below it, noise is treated as pure anti-banding and folding it into the downsampled stack (capped at 0.009) is enough, skipping the full-resolution round trip; above it, it is treated as deliberate visible grain and runs a full-resolution noise pass. The default 0.0045f falls just below the threshold -- raising it to 0.006 adds an entire full-resolution draw.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:72`)

**Spec** threshold NOISE_GRAIN_THRESHOLD = 0.005f; STACK_DITHER_MAX = 0.009f · default BlurDefaults.NoiseCoefficient = 0.0045f (uniform blur); BlurDefaults.ProgressiveNoiseCoefficient = 0f (progressive blur)

**State** Stateless; only writes scope.noiseCoefficient.

**vs Material3** No equivalent.

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:245`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt#L245)</sub>

## BackdropEffectScope.progressiveBlur  ·  blur

A variable-radius progressive blur. It works alone, but the clear end is only a soft transition of the downsampled layer; only with drawBackdrop(progressiveGradient=) do you get a genuinely pixel-sharp end.

> Chains a separable **progressive** (gradient) Blur into the scope's
> [BackdropEffectScope.renderEffect]: a true variable-radius blur whose radius ramps continuously
> from full to zero along [gradient]. It uses the same adaptive downscale as [blur], so it never
> blocks/aliases at large radii — but that single downscale also means the `intensity → 0` end
> samples the downscaled backdrop (soft, not pixel-sharp).
> 
> Paired with `drawBackdrop`'s `progressiveGradient` (as [Modifier.progressiveTextureBlur] wires),
> the draw path renders the multi-level composite instead — a downscaled level stack plus a
> genuinely sharp full-resolution clear end — and this call only records the target radii and
> downscale for it.

```kotlin
import top.yukonga.miuix.kmp.blur.progressiveBlur

fun BackdropEffectScope.progressiveBlur(
    radiusX: Float,  // required
    radiusY: Float = radiusX,
    gradient: ProgressiveBlur = ProgressiveBlur.Top,
)
```

- `radiusX` — Horizontal blur radius in pixels at full strength.
- `radiusY` — Vertical blur radius in pixels at full strength. Defaults to [radiusX].
- `gradient` — Direction and band controlling where the blur is full vs zero.

**Traps**

- 🔴 The radius is likewise in pixels (radiusX/radiusY), and gradient defaults to ProgressiveBlur.Top. As with blur, you must multiply by density yourself.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:122`)
- 🔴 When called alone (drawBackdrop was not passed a progressiveGradient), the KDoc clearly states that the intensity→0 end samples the downscaled backdrop (soft, not pixel-sharp) -- visually the clear end goes soft rather than erroring. For true sharpness you must pass the same gradient on both sides.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:114`)
- 🟡 In composite mode (drawBackdrop was passed a progressiveGradient) this call only registers the target radius and downsampling and does not actually chain a RenderEffect -- and a blendColors immediately after it is also folded into the stack's ramp pass rather than the normal chain. Inserting a custom effect between them behaves counterintuitively.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:133`)

**Spec** 

**State** Stateless; it writes the scope's padding / downscaleFactor and internal progressive record fields.

**vs Material3** No equivalent.

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:126`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt#L126)</sub>

## Modifier.progressiveTextureBlur  ·  blur

Gradient blur: the radius transitions continuously from full to zero along the direction ProgressiveBlur specifies, and the clear end is genuinely full-resolution sharp. Use it for fading frosted-glass top/bottom bars.

> Applies a **progressive (gradient) backdrop blur**: the blur strength ramps from full to zero
> along [gradient]'s direction — a genuine medium blur in the middle of the ramp, a pixel-sharp
> full-resolution clear end. Ideal for navigation bars and edge fades. Same color / blend / noise /
> highlight pipeline as [textureBlur], applied so the effects fade out with the blur.
> 
> Costs more than [textureBlur]: on top of the downscaled level stack, the pixel-sharp clear end
> adds a full-resolution overlay pass per frame. Prefer it for bars and edge bands over large
> fills.

```kotlin
import top.yukonga.miuix.kmp.blur.progressiveTextureBlur

fun Modifier.progressiveTextureBlur(
    backdrop: Backdrop,  // required
    shape: Shape,  // required
    blurRadius: Float = BlurDefaults.BlurRadius,
    gradient: ProgressiveBlur = ProgressiveBlur.Top,
    noiseCoefficient: Float = BlurDefaults.ProgressiveNoiseCoefficient,
    colors: BlurColors = BlurColors(),
    highlight: Highlight? = null,
    contentBlendMode: ComposeBlendMode = ComposeBlendMode.SrcOver,
    enabled: Boolean = true,
): Modifier
```

- `backdrop` — The [Backdrop] providing the background content to blur.
- `shape` — The shape provider for the blur region clipping.
- `blurRadius` — The blur radius in dp at full strength. Internally converted to pixels using   display density. Clamped to [0, [BlurDefaults.MaxBlurRadius]].
- `gradient` — Direction and band controlling where the blur is full vs zero. Defaults to   [ProgressiveBlur.Top].
- `noiseCoefficient` — Noise dithering coefficient for anti-banding. 0 (the default) disables noise.
- `colors` — Color adjustments and blend layers applied after blur.
- `highlight` — Optional edge highlight painted on top of the content. `null` skips drawing.
- `contentBlendMode` — Optional [ComposeBlendMode] for compositing content over the blur.
- `enabled` — Whether blur is active. When false, the effect is skipped and content draws normally.

**Traps**

- 🔴 It passes the gradient to both the progressiveTextureBlurEffect in the effects block and drawBackdrop's progressiveGradient -- neither can be omitted. When hand-rolling with drawBackdrop and you miss either side: passing only progressiveGradient makes the gradient silently ignored and draws a uniform blur; calling only progressiveBlur makes the clear end sample the downsampled layer, so it is soft rather than pixel-sharp.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:249`)
- 🟡 noiseCoefficient defaults to ProgressiveNoiseCoefficient = 0f (noise off), unlike textureBlur's 0.0045f. When switching over from textureBlur, if you rely on noise to de-band, pass it explicitly.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:240`)
- ⚪ The ProgressiveBlur.Top/Bottom/Left/Right preset names refer to the end where blur is strongest (Top = top edge blurriest, clearing downward), not the gradient direction. The semantics of angle: 0 degrees fades out left→right, 90 degrees fades out top→bottom.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/ProgressiveBlur.kt:31`)
- 🟡 The clear end's color-grading behavior changes abruptly with radius. The intermediate sigma = max(rX,rY)×0.45×0.4, and when it falls below BOUNDARY_SIGMA[0]=3.5496 exp==0, in which case the whole stack runs at full resolution and the clear end binds directly to the source that has already gone through the pre chain (i.e. colorControls), with the sharp-end overlay skipped; a bit larger and exp>0, so the clear end is instead handled by drawSharpOverlay recording the raw backdrop and only applying the overlay effect, with the pre chain not participating. That works out to a threshold of about 19.7px (about 6.6dp at density 3) -- animating the radius from 6.5dp to 7dp makes the clear end's brightness/contrast/saturation suddenly disappear.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/DrawBackdropModifier.kt:874`)

**Spec** gradient_default ProgressiveBlur.Top (angle=90, startFraction=0, endFraction=1, curve=1)

**State** Stateless. gradient is an @Immutable data class, and you can animate its startFraction/endFraction/curve directly.

**vs Material3** No equivalent.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/BlurSection.kt:144`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BlurSection.kt#L144) · [`example/shared/src/commonMain/kotlin/utils/PageUtils.kt:157`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/PageUtils.kt#L157)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:195`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt#L195)</sub>

## Modifier.progressiveTextureBlur  ·  blur

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Applies a progressive (gradient) backdrop blur with independent horizontal and vertical radii.

```kotlin
import top.yukonga.miuix.kmp.blur.progressiveTextureBlur

fun Modifier.progressiveTextureBlur(
    backdrop: Backdrop,  // required
    shape: Shape,  // required
    blurRadiusX: Float,  // required
    blurRadiusY: Float,  // required
    gradient: ProgressiveBlur = ProgressiveBlur.Top,
    noiseCoefficient: Float = BlurDefaults.ProgressiveNoiseCoefficient,
    colors: BlurColors = BlurColors(),
    highlight: Highlight? = null,
    contentBlendMode: ComposeBlendMode = ComposeBlendMode.SrcOver,
    enabled: Boolean = true,
): Modifier
```

- `backdrop` — The [Backdrop] providing the background content to blur.
- `shape` — The shape provider for the blur region clipping.
- `blurRadiusX` — The horizontal blur radius in dp at full strength. Clamped to   [0, [BlurDefaults.MaxBlurRadius]].
- `blurRadiusY` — The vertical blur radius in dp at full strength. Clamped to   [0, [BlurDefaults.MaxBlurRadius]].
- `gradient` — Direction and band controlling where the blur is full vs zero.
- `noiseCoefficient` — Noise dithering coefficient for anti-banding. 0 (the default) disables noise.
- `colors` — Color adjustments and blend layers applied after blur.
- `highlight` — Optional edge highlight painted on top of the content. `null` skips drawing.
- `contentBlendMode` — Optional [ComposeBlendMode] for compositing content over the blur.
- `enabled` — Whether blur is active. When false, the effect is skipped and content draws normally.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/BlurSection.kt:144`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BlurSection.kt#L144) · [`example/shared/src/commonMain/kotlin/utils/PageUtils.kt:157`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/PageUtils.kt#L157)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:234`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt#L234)</sub>

## BackdropEffectScope.progressiveTextureBlurEffect  ·  blur

> Runs the progressive (gradient) texture-blur preset chain inside a custom [drawBackdrop] effect
> block: like [textureBlurEffect] but with [progressiveBlur] in place of [blur], so the blur radius
> ramps from full to zero along [gradient].
> 
> Pair this with `drawBackdrop`'s `progressiveGradient` (same [gradient]) so the draw path renders
> the multi-level composite with a genuinely sharp full-resolution clear end —
> [Modifier.progressiveTextureBlur] wires both together.

```kotlin
import top.yukonga.miuix.kmp.blur.progressiveTextureBlurEffect

fun BackdropEffectScope.progressiveTextureBlurEffect(
    blurRadiusX: Float,  // required
    blurRadiusY: Float = blurRadiusX,
    gradient: ProgressiveBlur = ProgressiveBlur.Top,
    noiseCoefficient: Float = BlurDefaults.ProgressiveNoiseCoefficient,
    colors: BlurColors = BlurColors(),
)
```

- `blurRadiusX` — Horizontal blur radius in dp at full strength.
- `blurRadiusY` — Vertical blur radius in dp at full strength. Defaults to [blurRadiusX].
- `gradient` — Direction and band controlling where the blur is full vs zero.
- `noiseCoefficient` — Noise dithering coefficient. 0 (the default) disables noise.
- `colors` — Color adjustments and blend layers applied after blur.

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:418`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt#L418)</sub>

## rememberDeviceTilt  ·  sensor

Reads the device rotation sensor to feed parallax effects like rememberTiltLight. Only Android has real data.

> Returns a live [DeviceTilt] driven by the platform's rotation sensor; on platforms
> without sensor support (Desktop / Web / iOS / macOS), returns [DeviceTilt.Zero].

```kotlin
import top.yukonga.miuix.kmp.blur.sensor.rememberDeviceTilt

@Composable
expect fun rememberDeviceTilt(
    smoothing: Float = 0.15f,
): State<DeviceTilt>
```

Platform impls: androidMain, commonMain, skikoMain

- `smoothing` — Low-pass alpha applied to each sensor sample (0 < a ≤ 1).  1.0 = no smoothing (raw samples), 0.1 = heavy smoothing. Default 0.15.

**Traps**

- 🔴 On Desktop / iOS / macOS / Web it always returns DeviceTilt.Zero -- the skiko-side actual is just remember { mutableStateOf(DeviceTilt.Zero) }, one line. The supposed iOS implementation does not exist; it goes through exactly the same skikoMain as Desktop. Any tilt-dependent visual is static on these platforms, with no error.  (`miuix-blur/src/skikoMain/kotlin/top/yukonga/miuix/kmp/blur/sensor/DeviceTilt.skiko.kt:12`)
- 🟡 On Android, when the device has no GAME_ROTATION_VECTOR / ROTATION_VECTOR sensor it also silently stays at Zero (directly return@DisposableEffect onDispose {}), with no fallback to the accelerometer and no queryable availability flag.  (`miuix-blur/src/androidMain/kotlin/top/yukonga/miuix/kmp/blur/sensor/DeviceTilt.android.kt:31`)
- 🟡 smoothing is the key of the DisposableEffect -- animating it with something like animateFloatAsState repeatedly unregisters/re-registers the sensor and clears the smoothing state (initialized=false), reconverging from scratch each time. To adjust smoothing dynamically, interpolate the State value yourself outside.  (`miuix-blur/src/androidMain/kotlin/top/yukonga/miuix/kmp/blur/sensor/DeviceTilt.android.kt:27`)
- 🟡 Each call site registers its own SensorEventListener, with no sharing. N tilt-using components on a page means N SENSOR_DELAY_GAME listeners. To reuse, call it once higher up and pass the State down.  (`miuix-blur/src/androidMain/kotlin/top/yukonga/miuix/kmp/blur/sensor/DeviceTilt.android.kt:77`)

**Spec** smoothing Default 0.15f (low-pass alpha; 1.0 = no smoothing) · sensor Prefers TYPE_GAME_ROTATION_VECTOR, falls back to TYPE_ROTATION_VECTOR, sampling rate SENSOR_DELAY_GAME

**State** Returns State<DeviceTilt>. The listener registers and unregisters with Lifecycle ON_START/ON_STOP; each unregister resets the smoothing accumulator. pitch/roll are Euler angles (radians), gravityX/gravityY are gravity's projection onto the screen plane (the information Euler angles lose when rotating about the screen normal).

**vs Material3** No equivalent.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt:146`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt#L146)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/sensor/DeviceTilt.kt:44`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/sensor/DeviceTilt.kt#L44)</sub>

## rememberLayerBackdrop  ·  blur

Creates and remembers a LayerBackdrop (a GraphicsLayer snapshot-style background source). The only implementation of the library's Backdrop interface.

> Creates and remembers a [LayerBackdrop] that captures content from a [GraphicsLayer].
> 
> Use [Modifier.layerBackdrop][layerBackdrop] on the content container to capture its
> rendered output, then pass this [LayerBackdrop] to blur modifiers.
> 
> The instance is keyed only on [graphicsLayer]; [onDraw] is read via [rememberUpdatedState]
> so a fresh lambda each frame does not rebuild the backdrop and reset its layer coordinates.

```kotlin
import top.yukonga.miuix.kmp.blur.rememberLayerBackdrop

@Composable
fun rememberLayerBackdrop(
    graphicsLayer: GraphicsLayer = rememberGraphicsLayer(),
    onDraw: ContentDrawScope.() -> Unit = DefaultOnDraw,
): LayerBackdrop
```

- `graphicsLayer` — The graphics layer to record content into.
- `onDraw` — Custom draw logic for the layer content.

**Traps**

- 🔴 The default onDraw is just { drawContent() } -- in the recorded layer, wherever the subtree did not draw is transparent. Blur spreads color into the transparent region, producing a visible halo at the edges. The standard practice is to pass onDraw = { drawRect(surfaceColor); drawContent() } to lay down an opaque base color first.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdrop.kt:26`)
- ⚪ remember keys only on graphicsLayer, and onDraw goes through rememberUpdatedState. So creating a new onDraw lambda each frame does not rebuild the backdrop (this is intentional), but it also means changing onDraw does not trigger a redraw -- rely on the State it reads internally to invalidate itself.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdrop.kt:46`)
- 🟡 It has no enabled/fallback of its own. When blur is unsupported you should return null at the call site (if (!isRuntimeShaderSupported()) return null) and branch layerBackdrop out with null, otherwise you pay the capture layer's double-draw cost for nothing.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdrop.kt:41`)

**Spec** 

**State** An @Stable class that internally holds layerCoordinates (mutableStateOf) and offsetResidualX/Y. isCoordinatesDependent is hardcoded to true -- no implementation in the library takes the interface's false branch, and a custom Backdrop that wrongly declares false gets null coordinates and then silently draws nothing.

**vs Material3** No equivalent.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/BlurSection.kt:118`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BlurSection.kt#L118) · [`example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt:211`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt#L211)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdrop.kt:41`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/LayerBackdrop.kt#L41)</sub>

## rememberTiltLight  ·  highlight

Maps device tilt to a Highlight's light-source position, producing an edge-glow parallax that follows the phone's posture.

> Returns a [LightSource] whose UV position shifts with the live device tilt, producing
> a parallax-like edge bloom that "follows" the device orientation. On platforms without
> tilt sensors the returned light stays anchored at [basePosition].

```kotlin
import top.yukonga.miuix.kmp.blur.highlight.rememberTiltLight

@Composable
fun rememberTiltLight(
    basePosition: LightPosition,  // required
    color: Color = Color.White,
    intensity: Float = 1f,
    sensitivity: Float = 0.1f,
): LightSource
```

- `basePosition` — Position at zero tilt, in normalized UV (see [LightPosition]).
- `color` — Light color. Alpha is folded into the contribution weight.
- `intensity` — Overall scale on the light's contribution.
- `sensitivity` — UV offset applied per radian of tilt. Higher = more dramatic  parallax. `0.1f` shifts the light by 10% of the highlight bounds at 1 rad of tilt.

**Traps**

- 🔴 It memoizes with remember(tilt, ...), and tilt changes with every sensor sample -- so the composable calling it recomposes at the sensor sampling rate (Android SENSOR_DELAY_GAME, roughly 50Hz and up). Placed high in the page it recomposes the entire subtree with it; it should be pushed down into the smallest leaf composable.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/highlight/TiltLight.kt:32`)
- ⚪ Internally it calls the no-arg rememberDeviceTilt() with the default smoothing=0.15f, with no pass-through. To change the smoothing you can only write this yourself (read rememberDeviceTilt(smoothing) then construct the LightSource).  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/highlight/TiltLight.kt:31`)
- ⚪ It uses only tilt.roll / tilt.pitch, not gravityX / gravityY at all -- when the device rotates about the screen normal (spinning flat on a table) the light source does not move.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/highlight/TiltLight.kt:35`)
- 🟡 On sensorless platforms tilt is always Zero, so the light source stays at basePosition, with no error and no fallback notice.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/highlight/TiltLight.kt:16`)

**Spec** sensitivity Default 0.1f -- each radian of tilt moves the light source by 0.1 in normalized UV · intensity Default 1f; color defaults to Color.White, and alpha is folded into the contribution weight

**State** No self-held state, purely derived.

**vs Material3** No equivalent.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/highlight/ContainerHighlight.kt:32`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/highlight/ContainerHighlight.kt#L32)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/highlight/TiltLight.kt:25`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/highlight/TiltLight.kt#L25)</sub>

## RuntimeShader  ·  blur

> Back-compat re-export.

```kotlin
import top.yukonga.miuix.kmp.blur.RuntimeShader

fun RuntimeShader(
    shaderString: String,  // required
): RuntimeShader
```

- `shaderString` — The AGSL/SkSL shader source code to compile into the [RuntimeShader].

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt:41`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt#L41) · [`example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt:18`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt#L18)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt:22`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShader.kt#L22)</sub>

## BackdropEffectScope.runtimeShaderEffect  ·  blur

> Applies a custom runtime shader effect to the backdrop.
> 
> **Pixel-space uniforms must be scaled by [BackdropEffectScope.downscaleFactor].** When chained
> after [blur] (or any effect that raises [BackdropEffectScope.downscaleFactor]), the backdrop
> layer is recorded at `1 / downscaleFactor` resolution, and the shader receives `coord` values
> in the downscaled layer's pixel space. Any uniform that describes a pixel-space distance
> (size, padding/offset, corner radii, refraction band, …) must be divided by
> [BackdropEffectScope.downscaleFactor] inside [block], otherwise the geometry will sit far
> outside the downscaled layer's bounds and every sample will land on transparent black.

```kotlin
import top.yukonga.miuix.kmp.blur.runtimeShaderEffect

fun BackdropEffectScope.runtimeShaderEffect(
    key: String,  // required
    shaderString: String,  // required
    uniformShaderName: String,  // required
    block: RuntimeShader.() -> Unit,  // required
)
```

- `key` — Cache key for the compiled shader.
- `shaderString` — The AGSL/SkSL shader source code.
- `uniformShaderName` — The name of the shader uniform that receives the input image.
- `block` — Lambda to set uniforms on the shader before rendering.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/liquid/Lens.kt:55`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/Lens.kt#L55)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt:122`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt#L122)</sub>

## Modifier.textureBlur  ·  blur

A one-line HyperOS frosted-glass preset: the fixed recipe noiseDither → colorControls → blur → blendColors. It is enough for the vast majority of cases.

> Applies background blur to the content behind this composable.
> 
> Blend colors support both standard SkBlendMode (0-29, GPU hardware) and
> custom modes (100-121, 200-203, runtime shader). See [BlurBlendMode].

```kotlin
import top.yukonga.miuix.kmp.blur.textureBlur

fun Modifier.textureBlur(
    backdrop: Backdrop,  // required
    shape: Shape,  // required
    blurRadius: Float = BlurDefaults.BlurRadius,
    noiseCoefficient: Float = BlurDefaults.NoiseCoefficient,
    colors: BlurColors = BlurColors(),
    highlight: Highlight? = null,
    contentBlendMode: ComposeBlendMode = ComposeBlendMode.SrcOver,
    enabled: Boolean = true,
): Modifier
```

- `backdrop` — The [Backdrop] providing the background content to blur.
- `shape` — The shape provider for the blur region clipping.
- `blurRadius` — The blur radius in dp. Internally converted to pixels using display density.   Clamped to [0, [BlurDefaults.MaxBlurRadius]].
- `noiseCoefficient` — Noise dithering coefficient for anti-banding. 0 disables noise.
- `colors` — Color adjustments and blend layers applied after blur.
- `highlight` — Optional edge highlight painted on top of the content. `null` skips drawing.
- `contentBlendMode` — Optional [ComposeBlendMode] for compositing content over the blur.   Use [ComposeBlendMode.DstIn] for foreground blur (content alpha masks the blur).   null means content draws normally on top.
- `enabled` — Whether blur is active. When false, the effect is skipped and content draws normally.

**Traps**

- 🔴 blurRadius is in dp (internally multiplied by density to pixels), whereas the lower-level BackdropEffectScope.blur is in pixels. Mixing the two makes the radius off by a factor of density (3x on a 3x screen).  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:54`)
- 🔴 contentBlendMode is a non-null ComposeBlendMode, defaulting to SrcOver. The KDoc of all six overloads says Optional ... null means content draws normally on top (TextureEffect.kt:24/26, 61/63, 99/101, 138/140, 192, 231), and the docs docs/guide/blur.md:417 copied it as BlendMode? / null -- passing null fails to compile. For a foreground blur (content alpha as mask) pass ComposeBlendMode.DstIn.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:26`)
- ⚪ The radius is silently clamped to [0, BlurDefaults.MaxBlurRadius] (150dp). Passing a larger value does not error, it just does not get blurrier.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:395`)
- 🟡 BlurColors is marked @Immutable but contains a List<BlendColorEntry>, and Compose treats List as unstable -- constructing BlurColors(...) directly invalidates the caller on every recomposition. The KDoc itself states you should use the remembered BlurDefaults.blurColors factory.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BlurDefaults.kt:15`)

**Spec** blur_radius BlurDefaults.BlurRadius = 20f (dp) · noise BlurDefaults.NoiseCoefficient = 0.0045f; the progressive version defaults to ProgressiveNoiseCoefficient = 0f · max_radius BlurDefaults.MaxBlurRadius = 150f (dp)

**State** Stateless. At this layer shape is a plain Shape (not () -> Shape) and highlight is a plain Highlight? (not a scope lambda) -- if you need shape/highlight to animate you must drop down to drawBackdrop.

**vs Material3** No equivalent.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:267`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L267) · [`example/shared/src/commonMain/kotlin/AppContent.kt:541`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L541) · [`example/shared/src/commonMain/kotlin/component/BlurSection.kt:292`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BlurSection.kt#L292) · [`example/shared/src/commonMain/kotlin/utils/PageUtils.kt:138`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/PageUtils.kt#L138)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:29`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt#L29)</sub>

## Modifier.textureBlur  ·  blur

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Applies background blur with independent horizontal and vertical radii.

```kotlin
import top.yukonga.miuix.kmp.blur.textureBlur

fun Modifier.textureBlur(
    backdrop: Backdrop,  // required
    shape: Shape,  // required
    blurRadiusX: Float,  // required
    blurRadiusY: Float,  // required
    noiseCoefficient: Float = BlurDefaults.NoiseCoefficient,
    colors: BlurColors = BlurColors(),
    highlight: Highlight? = null,
    contentBlendMode: ComposeBlendMode = ComposeBlendMode.SrcOver,
    enabled: Boolean = true,
): Modifier
```

- `backdrop` — The [Backdrop] providing the background content to blur.
- `shape` — The shape provider for the blur region clipping.
- `blurRadiusX` — The horizontal blur radius in dp. Internally converted to pixels using display density.   Clamped to [0, [BlurDefaults.MaxBlurRadius]].
- `blurRadiusY` — The vertical blur radius in dp. Internally converted to pixels using display density.   Clamped to [0, [BlurDefaults.MaxBlurRadius]].
- `noiseCoefficient` — Noise dithering coefficient for anti-banding. 0 disables noise.
- `colors` — Color adjustments and blend layers applied after blur.
- `highlight` — Optional edge highlight painted on top of the content. `null` skips drawing.
- `contentBlendMode` — Optional [ComposeBlendMode] for compositing content over the blur.   Use [ComposeBlendMode.DstIn] for foreground blur (content alpha masks the blur).   null means content draws normally on top.
- `enabled` — Whether blur is active. When false, the effect is skipped and content draws normally.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:267`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L267) · [`example/shared/src/commonMain/kotlin/AppContent.kt:541`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L541) · [`example/shared/src/commonMain/kotlin/component/BlurSection.kt:292`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BlurSection.kt#L292) · [`example/shared/src/commonMain/kotlin/utils/PageUtils.kt:138`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/PageUtils.kt#L138)

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:66`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt#L66)</sub>

## BackdropEffectScope.textureBlurEffect  ·  blur

> Runs the standard texture-blur preset chain inside a custom [drawBackdrop] effect block.
> 
> Equivalent to what [Modifier.textureBlur] applies internally:
> 1. [noiseDither] for anti-banding
> 2. [colorControls] for brightness/contrast/saturation in linear (gamma 2.2) space
> 3. [blur] with the given radii in dp (multiplied by [BackdropEffectScope.density])
> 4. [blendColors] for the layered tinting
> 
> Use this to compose the standard preset with additional custom effects:
> ```
> Modifier.drawBackdrop(backdrop, shape = { shape }, effects = {
>     textureBlurEffect(blurRadius = 30f, colors = colors)
>     // ...then chain your own effect on top
> })
> ```

```kotlin
import top.yukonga.miuix.kmp.blur.textureBlurEffect

fun BackdropEffectScope.textureBlurEffect(
    blurRadiusX: Float,  // required
    blurRadiusY: Float = blurRadiusX,
    noiseCoefficient: Float = BlurDefaults.NoiseCoefficient,
    colors: BlurColors = BlurColors(),
)
```

- `blurRadiusX` — Horizontal blur radius in dp.
- `blurRadiusY` — Vertical blur radius in dp. Defaults to [blurRadiusX].
- `noiseCoefficient` — Noise dithering coefficient. 0 disables noise.
- `colors` — Color adjustments and blend layers applied after blur.

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt:389`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffects.kt#L389)</sub>

## Modifier.textureEffect  ·  blur

The per-axis radius version of textureBlur (blurRadiusX/blurRadiusY independent); all four textureBlur/textureEffect overloads ultimately land on it.

> Applies the complete texture effect: backdrop blur + color blending
> (with all custom blend modes).

```kotlin
import top.yukonga.miuix.kmp.blur.textureEffect

fun Modifier.textureEffect(
    backdrop: Backdrop,  // required
    shape: Shape,  // required
    blurRadius: Float = BlurDefaults.BlurRadius,
    noiseCoefficient: Float = BlurDefaults.NoiseCoefficient,
    colors: BlurColors = BlurColors(),
    highlight: Highlight? = null,
    contentBlendMode: ComposeBlendMode = ComposeBlendMode.SrcOver,
    enabled: Boolean = true,
): Modifier
```

- `backdrop` — The [Backdrop] providing the background content to blur.
- `shape` — Shape provider for the blur region clipping.
- `blurRadius` — The blur radius in dp. Internally converted to pixels using display density.   Clamped to [0, [BlurDefaults.MaxBlurRadius]].
- `noiseCoefficient` — Noise dithering coefficient for anti-banding.
- `colors` — Color adjustments and blend layers applied after blur.
- `highlight` — Optional edge highlight painted on top of the content. `null` skips drawing.
- `contentBlendMode` — Optional [ComposeBlendMode] for compositing content over the blur.   Use [ComposeBlendMode.DstIn] for foreground blur (content alpha masks the blur).   null means content draws normally on top.
- `enabled` — Whether the effect is active. When false, the effect is skipped and content draws normally.

**Traps**

- ⚪ TextureEffect.kt contains no logic at all; all 265 lines are overload forwarding. So textureEffect and textureBlur have exactly the same pitfalls (dp units, non-null contentBlendMode, radius clamped to 150dp, BlurColors unstable). To change the recipe order or add a custom pass, you must drop down to drawBackdrop + textureBlurEffect.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:151`)

**Spec** 

**State** Same as textureBlur.

**vs Material3** No equivalent.

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:104`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt#L104)</sub>

## Modifier.textureEffect  ·  blur

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Applies the complete texture effect with independent horizontal and vertical
> blur radii: backdrop blur + color blending (with all custom blend modes).

```kotlin
import top.yukonga.miuix.kmp.blur.textureEffect

fun Modifier.textureEffect(
    backdrop: Backdrop,  // required
    shape: Shape,  // required
    blurRadiusX: Float,  // required
    blurRadiusY: Float,  // required
    noiseCoefficient: Float = BlurDefaults.NoiseCoefficient,
    colors: BlurColors = BlurColors(),
    highlight: Highlight? = null,
    contentBlendMode: ComposeBlendMode = ComposeBlendMode.SrcOver,
    enabled: Boolean = true,
): Modifier
```

- `backdrop` — The [Backdrop] providing the background content to blur.
- `shape` — Shape provider for the blur region clipping.
- `blurRadiusX` — The horizontal blur radius in dp. Internally converted to pixels using display density.   Clamped to [0, [BlurDefaults.MaxBlurRadius]].
- `blurRadiusY` — The vertical blur radius in dp. Internally converted to pixels using display density.   Clamped to [0, [BlurDefaults.MaxBlurRadius]].
- `noiseCoefficient` — Noise dithering coefficient for anti-banding.
- `colors` — Color adjustments and blend layers applied after blur.
- `highlight` — Optional edge highlight painted on top of the content. `null` skips drawing.
- `contentBlendMode` — Optional [ComposeBlendMode] for compositing content over the blur.   Use [ComposeBlendMode.DstIn] for foreground blur (content alpha masks the blur).   null means content draws normally on top.
- `enabled` — Whether the effect is active. When false, the effect is skipped and content draws normally.

<sub>Source [`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt:143`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/TextureEffect.kt#L143)</sub>

## Top-level properties & CompositionLocals (1)

- `LocalRuntimeShaderCache = staticCompositionLocalOf<RuntimeShaderCache> { … }`  <sub>[`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShaderCache.kt:32`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/RuntimeShaderCache.kt#L32)</sub>

## Public types in this topic (14)

- `Backdrop` **interface** · `import top.yukonga.miuix.kmp.blur.Backdrop`
- `BackdropEffectScope` **interface** · `import top.yukonga.miuix.kmp.blur.BackdropEffectScope`
- `BlendColorEntry(color: Color, mode: BlurBlendMode)` **data class** (required: color) · `import top.yukonga.miuix.kmp.blur.BlendColorEntry`
- `BloomStroke(color: Color, blendMode: BlendMode, innerBlurRadius: Dp, primaryLight: LightSource, secondaryLight: LightSource, dualPeak: Boolean)` **data class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.blur.highlight.BloomStroke`
- `BlurBlendMode(value: Int)` **value class** (required: value) · `import top.yukonga.miuix.kmp.blur.BlurBlendMode`
- `BlurDefaults` **object** · `import top.yukonga.miuix.kmp.blur.BlurDefaults`
- `DeviceTilt(pitch: Float, roll: Float, gravityX: Float, gravityY: Float)` **data class** (required: pitch, roll) · `import top.yukonga.miuix.kmp.blur.sensor.DeviceTilt`
- `Highlight(width: Dp, style: HighlightStyle)` **data class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.blur.highlight.Highlight`
- `HighlightStyle` **interface** · `import top.yukonga.miuix.kmp.blur.highlight.HighlightStyle`
- `LayerBackdrop` **class** · `import top.yukonga.miuix.kmp.blur.LayerBackdrop`
- `LightPosition(x: Float, y: Float, z: Float)` **data class** (required: x, y, z) · `import top.yukonga.miuix.kmp.blur.highlight.LightPosition`
- `LightSource(position: LightPosition, color: Color)` **data class** (required: position) · `import top.yukonga.miuix.kmp.blur.highlight.LightSource`
- `ProgressiveBlur(angle: Float, startFraction: Float, endFraction: Float, curve: Float)` **data class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.blur.ProgressiveBlur`
- `RuntimeShaderCache` **interface** · `import top.yukonga.miuix.kmp.blur.RuntimeShaderCache`

