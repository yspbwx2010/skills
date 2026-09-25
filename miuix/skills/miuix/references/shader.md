# Shader

miuix-shader. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## RuntimeShader.asAndroidRuntimeShader  ·  shader

> Returns the underlying [android.graphics.RuntimeShader] for interop with native render-effect APIs.

```kotlin
import top.yukonga.miuix.kmp.shader.asAndroidRuntimeShader

fun RuntimeShader.asAndroidRuntimeShader(): android.graphics.RuntimeShader
```

<sub>Source [`miuix-shader/src/androidMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.android.kt:34`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-shader/src/androidMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.android.kt#L34)</sub>

## RuntimeShader.asBrush  ·  shader

> Wraps this [RuntimeShader] as a [ShaderBrush]. On Android the underlying
> shader is mutable, so a cached [ShaderBrush] is returned; on Skiko
> [asComposeShader] produces an immutable snapshot, so a fresh [ShaderBrush]
> is created on every call to ensure uniform updates are visible.

```kotlin
import top.yukonga.miuix.kmp.shader.asBrush

expect fun RuntimeShader.asBrush(): ShaderBrush
```

Platform impls: androidMain, commonMain, skikoMain

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt#L62) · [`example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt:23`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt#L23)

<sub>Source [`miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt:141`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt#L141)</sub>

## RuntimeShader.asComposeShader  ·  shader

> Returns the [RuntimeShader] as a Compose [Shader] suitable for use with Paint.

```kotlin
import top.yukonga.miuix.kmp.shader.asComposeShader

expect fun RuntimeShader.asComposeShader(): Shader
```

Platform impls: androidMain, commonMain, skikoMain

<sub>Source [`miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt:133`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt#L133)</sub>

## RuntimeShader.asSkikoRuntimeShader  ·  shader

> Returns the underlying Skia [RuntimeShaderBuilder] for interop with native shader APIs.

```kotlin
import top.yukonga.miuix.kmp.shader.asSkikoRuntimeShader

fun RuntimeShader.asSkikoRuntimeShader(): RuntimeShaderBuilder
```

<sub>Source [`miuix-shader/src/skikoMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.skiko.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-shader/src/skikoMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.skiko.kt#L42)</sub>

## isRenderEffectSupported  ·  shader

RenderEffect capability detection (Android API 31). A published public API, but with zero call sites in the library.

> True if the current platform supports [androidx.compose.ui.graphics.RenderEffect]-based effects.

```kotlin
import top.yukonga.miuix.kmp.shader.isRenderEffectSupported

expect fun isRenderEffectSupported(): Boolean
```

Platform impls: androidMain, commonMain, skikoMain

**Traps**

- 🟡 It is dead code: the whole repo has only an expect declaration and two actuals, with no call sites. And structurally no one can use it -- the only possible consumer, miuix-blur, has minSdk 33 itself (higher than 31), and every main path of miuix-squircle needs RuntimeShader (33), so there is no tier in between that needs only RenderEffect.  (`miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RenderEffect.kt:7`)
- 🟡 On Android it checks Build.VERSION_CODES.S, i.e. API 31, while the docs docs/guide/blur.md:60 and docs/zh_CN/guide/blur.md:56 both write True on API 32+, off by one level.  (`miuix-shader/src/androidMain/kotlin/top/yukonga/miuix/kmp/shader/RenderEffect.android.kt:12`)
- 🔴 The docs' claim of it as a fallback is entirely hollow: docs/guide/blur.md:61 says on API 32 you can also chain a colorFilter(...), but BackdropEffectScope has no colorFilter extension at all (the 9 extensions are colorControls / effect / runtimeShaderEffect / blur / progressiveBlur / noiseDither / blendColors / textureBlurEffect / progressiveTextureBlurEffect). The Chinese mirror docs/zh_CN/guide/blur.md:56-57, 377 has the same error.  (`miuix-blur/src/commonMain/kotlin/top/yukonga/miuix/kmp/blur/BackdropEffectScope.kt:102`)

**Spec** 

**State** Pure function, stateless.

**vs Material3** No equivalent.

<sub>Source [`miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RenderEffect.kt:7`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RenderEffect.kt#L7)</sub>

## isRuntimeShaderSupported  ·  shader

The single gating check for the whole shader capability set (blur, color blending, squircle fill). Android requires API 33, all other platforms are always true.

> True on Android API 33+ and on every Skia backend.

```kotlin
import top.yukonga.miuix.kmp.shader.isRuntimeShaderSupported

expect fun isRuntimeShaderSupported(): Boolean
```

Platform impls: androidMain, commonMain, skikoMain

**Traps**

- 🟡 On Android it is API 33 (TIRAMISU), not 31. It carries @ChecksSdkIntAtLeast, so accessing API 33 symbols inside an if (isRuntimeShaderSupported()) { ... } block does not trigger the NewApi lint -- but this benefit only exists when importing directly from top.yukonga.miuix.kmp.shader; the same-named back-compat forwarder under the miuix-blur package is a plain common function that has lost this annotation.  (`miuix-shader/src/androidMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.android.kt:18`)
- 🟡 Non-Android platforms return true unconditionally, with no real detection. On Web (js/wasmJs), once WebGL is unavailable or the driver is blacklisted, SkSL compilation failure throws an exception directly rather than falling back -- this side has no failure exit at all (makeForShader has no try/catch and the cache does not cache failures).  (`miuix-shader/src/skikoMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.skiko.kt:18`)
- 🔴 The miuix-blur module's minSdk is hardcoded to 33 (not via BuildConfig.MIN_SDK), so an app with minSdk<33 depending on miuix-blur fails manifest merging and needs tools:overrideLibrary. miuix-squircle / miuix-shader have minSdk 24, and 33 is only a runtime gate for them.  (`miuix-blur/build.gradle.kts:31`)

**Spec** 

**State** Pure function, stateless.

**vs Material3** No equivalent. M3 has no equivalent capability detection; the official Modifier.blur is silently ineffective on unsupported platforms.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:192`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L192) · [`example/shared/src/commonMain/kotlin/LicensePage.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/LicensePage.kt#L54) · [`example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt:44`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt#L44) · [`example/shared/src/commonMain/kotlin/NavigateTestPage.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/NavigateTestPage.kt#L54)

<sub>Source [`miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt:123`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt#L123)</sub>

## RuntimeShader  ·  shader

> Creates a platform-specific [RuntimeShader] from an AGSL/SkSL shader string.

```kotlin
import top.yukonga.miuix.kmp.shader.RuntimeShader

expect fun RuntimeShader(
    shaderString: String,  // required
): RuntimeShader
```

Platform impls: androidMain, commonMain, skikoMain

- `shaderString` — The AGSL (Android) or SkSL (Skia) shader source to compile.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt:41`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/animation/InteractiveHighlight.kt#L41) · [`example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt:18`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/effect/BgEffectPainter.kt#L18)

<sub>Source [`miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt:130`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-shader/src/commonMain/kotlin/top/yukonga/miuix/kmp/shader/RuntimeShader.kt#L130)</sub>

## Public types in this topic (1)

- `RuntimeShader` **interface** · `import top.yukonga.miuix.kmp.shader.RuntimeShader`

