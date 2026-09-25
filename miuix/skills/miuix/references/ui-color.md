# Color picking

The ColorPicker family, ColorPalette, color-space types. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## ColorPalette  ·  basic component

An HSV swatch grid (default 7 rows × 12 hue columns + 1 gray column) plus a built-in Alpha slider, drawn on a single Canvas, select-on-press, drag-to-select continuously. Good for 'picking one from preset colors', not for precise color selection —— it can only produce the discrete colors in the grid.

> A color palette component that allows users to select colors from a grid of HSV values.

```kotlin
import top.yukonga.miuix.kmp.basic.ColorPalette

@Composable
fun ColorPalette(
    color: Color,  // required
    onColorChanged: (Color) -> Unit,  // required
    modifier: Modifier = Modifier,
    rows: Int = 7,
    hueColumns: Int = 12,
    includeGrayColumn: Boolean = true,
    showPreview: Boolean = true,
    cornerRadius: Dp = 16.dp,
    indicatorRadius: Dp = 10.dp,
)
```

- `color` — The color to display in the palette.
- `onColorChanged` — Callback invoked when the selected color changes.
- `modifier` — Modifier for styling the palette.
- `rows` — Number of rows in the color grid.
- `hueColumns` — Number of columns for hue variations.
- `includeGrayColumn` — Whether to include a gray column in the palette.
- `showPreview` — Whether to show a preview of the selected color.
- `cornerRadius` — Corner radius for the palette's shape.
- `indicatorRadius` — Radius of the selection indicator circle.

**Traps**

- 🔴 It is snap-based: the color you pass isn't displayed as-is but decomposed into HSV and snapped to the nearest cell. In the default rows=7 S/V table, when s=1 the highest v is only 0.85, so there is no pure color anywhere in the swatch —— pass Color.Red and the indicator ring lands on the Hsv(0,100,85) cell (about #D90000), while the top preview bar on first render still shows the pure red you passed; the two don't match; only tapping that cell makes onColorChanged emit #D90000. The first composition doesn't proactively fire the callback, so 'parent state == highlighted cell' never holds until the user's first tap.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:104-113`)
- 🟡 The nearest-rounding of hue columns doesn't handle wraparound. col is obtained by rounding (h%360)/360*hueColumns and then coerceIn(0, hueColumns-1); with hueColumns=12, h≥345° is computed as 12 and clamped back to 11 (i.e. the 330° cell), whereas the truly nearest is the 0° cell. That is, colors in the 345°–360° magenta-toward-red segment are snapped to the wrong column.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:97-103`)
- 🟡 rows=7 uses a hand-tuned hardcoded S/V table, while other rows use a different formula. Changing rows from 7 to 8 is not 'one more row' but swaps the entire saturation/value distribution to a different algorithm, and the swatch's appearance changes abruptly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:338-359`)
- 🟡 Passing 0 for rows or totalColumns crashes with an index out-of-bounds: the indicator reads cell edges via rowEdges[selectedRow+1] / colEdges[selectedCol+1], the array lengths are rows+1 / totalColumns+1, and there is no input validation. hueColumns=0 with includeGrayColumn=false is the same landmine.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:236-241`)
- ⚪ External color changes have a tolerance window of 1.5° hue / 0.02 saturation and value: an external color falling within the window only updates alpha and doesn't move the indicator ring. This is to avoid fighting the user's drag, but it also means programmatically nudging the color a tiny bit 'won't take'.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:85-95`)
- ⚪ The built-in Alpha slider can't be hidden (showPreview only governs the top preview bar), and ColorPalette has no hapticEffect parameter —— the internal HsvAlphaSlider uses the default haptics, which is not configurable and is inconsistent with ColorPicker.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:163-175`)
- ⚪ cornerRadius goes through Miuix's squircleClip rather than RoundedCornerShape, so the corner shape is a superellipse and doesn't line up with adjacent elements you build with RoundedCornerShape yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:199-202`)

**Spec** grid fillMaxWidth × 180.dp (hardcoded; modifier only affects the outermost Column, so the height can't be adjusted) · preview fillMaxWidth × 26.dp, squircleBackground with 13.dp corners · indicator diameter = indicatorRadius×2 (default 20.dp), a 6.dp white stroke ring + a 2.dp black 25% outer glow · corner cornerRadius default 16.dp, squircleClip (superellipse), not RoundedCornerShape · layout Column + Arrangement.spacedBy(12.dp): preview bar / grid / Alpha slider

**State** Self-holding state: internally it stores only three values, selectedRow / selectedCol / alpha, and the color is computed live from the cell coordinates. The external color is reverse-solved into row/column via LaunchedEffect(color, rows, hueColumns, includeGrayColumn), with the tolerance short-circuit described above. The top preview shows lastEmittedColor ?: color, so before the first interaction it shows the external color and afterward always shows the color it emitted itself.

**vs Material3** No counterpart.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ColorPaletteDemo.kt:41`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ColorPaletteDemo.kt#L41) · [`example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt:82`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt#L82)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt:64`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPalette.kt#L64)</sub>

## ColorPicker  ·  basic component

The unified entry point for the color picker; it dispatches by colorSpace to one of the four implementations HsvColorPicker / OkHsvColorPicker / OkLabColorPicker / OkLchColorPicker; it contains no UI logic itself, just a when dispatcher. When you want to fix a specific color space, using the concrete implementation directly saves a layer.

> A [ColorPicker] component with Miuix style that supports multiple color spaces.

```kotlin
import top.yukonga.miuix.kmp.basic.ColorPicker

@Composable
fun ColorPicker(
    color: Color,  // required
    onColorChanged: (Color) -> Unit,  // required
    modifier: Modifier = Modifier,
    showPreview: Boolean = true,
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
    colorSpace: ColorSpace = ColorSpace.HSV,
)
```

- `color` — The color of the picker.
- `onColorChanged` — The callback to be called when the color changes.
- `modifier` — The modifier to be applied to the color picker.
- `showPreview` — Whether to show a preview of the selected color.
- `hapticEffect` — The haptic effect of the [ColorSlider].
- `colorSpace` — The color space to use for the picker.

**Traps**

- 🔴 It is not a purely controlled component. The child Picker stores the internal H/S/V in a keyless remember, and only reflows when the external color differs from both 'the last synced external value' and 'the current internal value'. A typical failure: after the user drags, you store color (internal value == external value, so no sync and lastApplied isn't updated either), then tapping 'reset' changes color back to the initial value —— at this point externalArgb == lastAppliedExternalColorArgb, the condition short-circuits, and the sliders and preview don't budge. To truly reset you must swap the Picker's key to force a rebuild.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:161-176`)
- 🟡 Conversely, when onColorChanged does nothing (or hardcodes color to a constant), the Picker can still be dragged and change color —— because the state is internal. It looks 'usable', but the color you receive is always stale.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:142-146`)
- 🟡 Switching colorSpace at runtime discards the internal state being edited. The four branches are different groups of the when, so switching away destroys it and switching back re-initializes via remember from the current color. Only when you actually write the value from onColorChanged back to color is the switch lossless; otherwise a single switch returns to the original color. The official example opens a separate card for each of the four color spaces, each holding its own state, rather than switching a single Picker.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:78-118`)
- 🟡 colorSpace is of type top.yukonga.miuix.kmp.basic.ColorSpace, which shares its name with androidx.compose.ui.graphics.colorspace.ColorSpace. IDE auto-import very easily picks the wrong one, and when it does the error is a type mismatch rather than 'symbol not found'. The docs' Import section doesn't give this line either.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1298-1303`)
- ⚪ In the when, HSV takes the else fallback rather than an explicit ColorSpace.HSV branch; behaviorally equivalent, but it means any future enum value silently falls to HSV instead of a compile error.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:109-117`)

**Spec** layout Column + Arrangement.spacedBy(12.dp), a preview bar + 4 sliders, 5 rows total · preview fillMaxWidth × 26.dp, clipped to CircleShape, the whole block disappears when showPreview=false (and loses 12.dp of spacing too) · modifier modifier only affects the outermost Column; the slider height, preview height, and row spacing are all hardcoded and unchangeable

**State** Self-holding state (uncontrolled with sync). Internally it stores the decomposed channel values in a remember{} plus a lastAppliedExternalColorArgb watermark, and does a one-way weak sync in a SideEffect. onColorChanged is required and non-null, and fires only when the new color's toArgb() differs from the passed color's toArgb() (the same ARGB won't call back twice). You must remember a Color state yourself and write it back in the callback, or the external and internal will drift apart permanently.

**vs Material3** There is no color picker in androidx.compose.material3, so there is no counterpart. The only analogy is M3's Slider —— but M3 Slider is purely controlled (value/onValueChange), while this Miuix set is self-holding state, and that difference is the easiest one to trip over when migrating.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ColorPickerDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ColorPickerDemo.kt#L42) · [`example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt:34`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt#L34)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:69`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L69)</sub>

## Modifier.drawCheckerboard  ·  basic component

A top-level public Modifier extension that draws a 'transparency' checkerboard behind the node; it's what the four Alpha sliders use. Zero documentation coverage, but it is the only part in this set that can be reused independently on your own components —— to back your own transparent-color preview block with a checkerboard, use it directly, don't write your own. It lives in the top.yukonga.miuix.kmp.basic package (the file is ColorPicker.kt).

```kotlin
import top.yukonga.miuix.kmp.basic.drawCheckerboard

fun Modifier.drawCheckerboard(
    cellSizeDp: Dp = 3.dp,
    lightColor: Color = Color(0xFFCCCCCC),
    darkColor: Color = Color(0xFFAAAAAA),
): Modifier
```

**Traps**

- 🟡 It first lays down an opaque lightColor full-area rectangle and then overlays the dark cells, so it covers up earlier drawBehind content in the chain. It must be placed before the gradient/content drawing (closer to the head of the chain), and it doesn't clip itself —— when used alone you must clip first, or the checkerboard fills the whole node's bounding box rather than the rounded interior.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1141-1144`)
- 🟡 The default colors #CCCCCC / #AAAAAA are hardcoded light gray and don't read the theme. In a dark theme you must explicitly pass lightColor / darkColor, or it will be a glaring bright-gray block.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1113-1116`)
- 🟡 The cells are constructed all at once as a single Path inside drawWithCache, with a rectangle count of about area/(2×cell²). The default 3.dp cell is designed for a 26.dp-tall slider bar; spread over a full-screen-sized area it builds a Path of tens of thousands of rectangles (though it only rebuilds when the size/density changes). For large areas, increase cellSizeDp.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1118-1139`)
- ⚪ cellSizeDp is coerceAtLeast(1f)'d to at least 1 physical pixel, so passing 0.dp won't infinite-loop, but on low-density devices 1.dp and 0.5.dp render as the same 1px cell.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1119`)

**Spec** cell cellSizeDp default 3.dp (clamped to a minimum of 1px) · colors lightColor default Color(0xFFCCCCCC), darkColor default Color(0xFFAAAAAA), both hardcoded and theme-independent · order even rows start drawing dark from the 2nd cell, odd rows from the 1st cell (a standard checkerboard); the dark cells are drawn with a single drawPath on one Path

**State** Stateless, a pure drawing modifier. It draws in the onDrawBehind phase (beneath the content).

**vs Material3** No counterpart. Neither Compose proper nor material3 has a checkerboard modifier; the usual approach is to write your own drawBehind or use a ShaderBrush + TileMode.Repeated bitmap shader —— the latter is much faster than this Path implementation over large areas.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1113`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L1113)</sub>

## HsvAlphaSlider  ·  basic component

HSV alpha slider, backed by a Modifier.drawCheckerboard() checkerboard. You must pass all three H/S/V channels for it to draw the correct 'current color from transparent to opaque' gradient. This is also the one ColorPalette reuses internally.

> A [HsvAlphaSlider] component for selecting the alpha of a color.

```kotlin
import top.yukonga.miuix.kmp.basic.HsvAlphaSlider

@Composable
fun HsvAlphaSlider(
    currentHue: Float,  // required
    currentSaturation: Float,  // required
    currentValue: Float,  // required
    currentAlpha: Float,  // required
    onAlphaChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentHue` — The current hue value.
- `currentSaturation` — The current saturation value.
- `currentValue` — The current value value.
- `currentAlpha` — The current alpha value.
- `onAlphaChanged` — The callback to be called when the alpha changes.
- `hapticEffect` — The haptic effect of the [HsvAlphaSlider].

**Traps**

- 🔴 currentHue is 0..360, and the other three parameters and the callback are all 0..1. All three side channels are required, and missing one fails to compile (there are no defaults).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:344-355`)
- 🟡 The checkerboard base is a hardcoded #CCCCCC/#AAAAAA light gray that doesn't follow MiuixTheme's light/dark. In a dark theme this slider is the only bright-gray block on screen, visually jarring, and the component exposes no parameter to change it (drawCheckerboard's color parameters are the hardcoded defaults here).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:361-364`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:344-350`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track baseColor(alpha=0) → baseColor(alpha=1), with a 3.dp checkerboard #CCCCCC / #AAAAAA underneath

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:344`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L344)</sub>

## HsvColorPicker  ·  basic component

The implementation behind ColorPicker(colorSpace = ColorSpace.HSV); it can also be called directly to bypass dispatch. The classic four HSV sliders (hue / saturation / value / alpha), the most intuitive and least perceptually uniform option; use it for 'just pick a color' scenarios.

> A [HsvColorPicker] component with Miuix style using HSV color space.

```kotlin
import top.yukonga.miuix.kmp.basic.HsvColorPicker

@Composable
fun HsvColorPicker(
    color: Color,  // required
    onColorChanged: (Color) -> Unit,  // required
    modifier: Modifier = Modifier,
    showPreview: Boolean = true,
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `color` — The color of the picker.
- `onColorChanged` — The callback to be called when the color changes.
- `modifier` — The modifier to be applied to the color picker.
- `showPreview` — Whether to show a preview of the selected color.
- `hapticEffect` — The haptic effect of the [ColorSlider].

**Traps**

- 🔴 Same as ColorPicker: self-holding state + SideEffect weak sync; when the external side changes color back to the last synced value it won't roll back.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:161-176`)
- 🟡 The hue of grayscale colors (black / white / any gray) is undefined in HSV, and at initialization colorToHsv returns h=0. Pass Color.White in and the hue slider sits at the far left (red), so as soon as the user moves saturation it jumps straight to the red family, looking like the component 'messes with the color'.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:153-158`)
- ⚪ The initial value goes through 8-bit quantization: Color.toHsv() internally multiplies red/green/blue by 255 and rounds before computing HSV, so a non-8-bit-aligned float color (e.g. a Color from interpolation/animation) drifts on the order of 1/255 in and out.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:170-179`)

**Spec** layout Column spacedBy 12.dp: preview bar 26.dp (CircleShape) + four 26.dp sliders for hue / saturation / value / alpha · order H → S → V → A

**State** Same as ColorPicker: remember four Floats (hue stored as 0..360, s/v/alpha stored as 0..1) + lastAppliedExternalColorArgb, and selectedColor is computed live with derivedStateOf.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:131`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L131)</sub>

## HsvHueSlider  ·  basic component

A standalone HSV hue slider; its background is a 36-segment full-saturation, full-value rainbow gradient. It is the only one of the four Hsv* sliders that needs only its own hue value and no side channels.

> A [HsvHueSlider] component for selecting the hue of a color using pure HSV colors.

```kotlin
import top.yukonga.miuix.kmp.basic.HsvHueSlider

@Composable
fun HsvHueSlider(
    currentHue: Float,  // required
    onHueChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentHue` — The current hue value (0-360).
- `onHueChanged` — The callback to be called when the hue changes (0-1).
- `hapticEffect` — The haptic effect of the [HsvHueSlider].

**Traps**

- 🔴 The input and output units are asymmetric, the easiest thing in the whole set to get wrong: currentHue takes a 0..360 angle, while the onHueChanged callback gives you a 0..1 normalized value. If you write onHueChanged = { hue = it } per 'take it back and store it directly', the hue is compressed into the tiny 0..1 degree range and the slider appears stuck at the far left. The correct form is hue = it * 360f (the official docs example is correct, but nothing outside the KDoc warns you).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:256-271`)
- 🟡 There is no modifier parameter. Internally it hardcodes Modifier.fillMaxWidth() wrapped in a fixed 26.dp height, so you can neither change the dimensions nor add padding/click area —— to leave whitespace you must wrap it in a Box outside. All 16 sliders are like this.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:265-271`)
- 🟡 Only a draggable gesture, no tap gesture. Clicking the slider bar won't jump the thumb to the click position; you must drag past the touch slop for it to respond (the drag jumps to the finger position as soon as it begins, so it's 'jumps on drag' rather than 'no response and no jump on tap'). The ColorPalette on the same page uses awaitFirstDown and selects on a single tap —— the two have inconsistent interaction feel.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1198-1218`)
- ⚪ The passed-in value isn't clamped. A currentHue outside 0..360 (e.g. if you accumulate it yourself without taking the modulo) sends the indicator ring outside the track and it won't be clamped.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1240-1246`)

**Spec** size fillMaxWidth × 26.dp (fixed, no modifier parameter) · corner CircleShape pill · track 36-segment Hsv(h,100,100) gradient; the gradient's start and end are inset by half the height (13.dp), so the 13.dp at each end is a solid-color plateau, aligned with the indicator ring's travel range · indicator 20.dp, a 6.dp white stroke ring + a 2.dp black 25% outer glow · border 0.5.dp stroke at Color.Gray 10% opacity

**State** Purely controlled, no internal state. currentHue in (degrees), 0..1 out; you must multiply by 360 yourself to store it back.

**vs Material3** No counterpart; M3 has only a generic Slider, and it is symmetric value/onValueChange.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:256`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L256)</sub>

## HsvSaturationSlider  ·  basic component

HSV saturation slider. The background gradient varies with currentHue (from that hue's white to that hue's full saturation), so you must pass the current hue in as well.

> A [HsvSaturationSlider] component for selecting the saturation of a color.

```kotlin
import top.yukonga.miuix.kmp.basic.HsvSaturationSlider

@Composable
fun HsvSaturationSlider(
    currentHue: Float,  // required
    currentSaturation: Float,  // required
    onSaturationChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentHue` — The current hue value.
- `currentSaturation` — The current saturation value.
- `onSaturationChanged` — The callback to be called when the saturation changes.
- `hapticEffect` — The haptic effect of the [HsvSaturationSlider].

**Traps**

- 🔴 Here currentHue takes a 0..360 angle (the same unit as HsvHueSlider's input), while currentSaturation and the callback are 0..1. With two units mixed within the same slider set, when copying code it's very easy to feed in the 0..1 value from HsvHueSlider's callback directly, and the whole gradient then stays stuck at red forever.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:283-301`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture. Same as HsvHueSlider.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:283-288`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track two-stop gradient Hsv(h,0,100) → Hsv(h,100,100); note value is locked at 100 and doesn't vary with currentValue —— so for dark colors the gradient bar is brighter than the actual result

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:283`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L283)</sub>

## HsvValueSlider  ·  basic component

HSV value slider; the gradient runs from pure black to the color at 'the current hue + current saturation, value maxed'. You must pass both hue and saturation.

> A [HsvValueSlider] component for selecting the value/brightness of a color.

```kotlin
import top.yukonga.miuix.kmp.basic.HsvValueSlider

@Composable
fun HsvValueSlider(
    currentHue: Float,  // required
    currentSaturation: Float,  // required
    currentValue: Float,  // required
    onValueChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentHue` — The current hue value.
- `currentSaturation` — The current saturation value.
- `currentValue` — The current value value.
- `onValueChanged` — The callback to be called when the value changes.
- `hapticEffect` — The haptic effect of the [HsvValueSlider].

**Traps**

- 🔴 currentHue is 0..360, while currentSaturation / currentValue / the callback are all 0..1. The unit mixing is as above.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:314-330`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:314-319`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track Color.Black → Hsv(h, s*100, 100)

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:314`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L314)</sub>

## OkHsvAlphaSlider  ·  basic component

OkHSV alpha slider, with a drawCheckerboard checkerboard base. It needs the three H/S/V side channels to compute the current color.

> A [OkHsvAlphaSlider] component for selecting the alpha of a color using OkHSV.

```kotlin
import top.yukonga.miuix.kmp.basic.OkHsvAlphaSlider

@Composable
fun OkHsvAlphaSlider(
    currentH: Float,  // required
    currentS: Float,  // required
    currentV: Float,  // required
    currentAlpha: Float,  // required
    onAlphaChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentH` — The current hue value.
- `currentS` — The current saturation value.
- `currentV` — The current value value.
- `currentAlpha` — The current alpha value.
- `onAlphaChanged` — The callback to be called when the alpha changes.
- `hapticEffect` — The haptic effect of the [OkHsvAlphaSlider].

**Traps**

- 🔴 The parameter names are currentH / currentS / currentV / currentAlpha, all 0..1, all required with no defaults.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:597-607`)
- 🟡 The checkerboard color is a hardcoded light gray that doesn't follow the theme's light/dark, and can't be configured here.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:614-617`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:597-603`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track baseColor(alpha=0) → baseColor(alpha=1), with a 3.dp checkerboard underneath

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:597`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L597)</sub>

## OkHsvColorPicker  ·  basic component

The implementation behind ColorPicker(colorSpace = ColorSpace.OKHSV). Based on Ottosson OkHSV, with perceptual-lightness correction and gamut-cusp reparameterization, so the hue bar has no HSV-style 'bright yellow-green, dark blue-purple' light/dark banding. It is the most mathematically complete of the four color spaces and the only one that takes the correct sRGB linearization path.

> A [OkHsvColorPicker] component with Miuix style using OkHSV color space based on OkLab.
> OkHSV provides better perceptual uniformity than traditional HSV.

```kotlin
import top.yukonga.miuix.kmp.basic.OkHsvColorPicker

@Composable
fun OkHsvColorPicker(
    color: Color,  // required
    onColorChanged: (Color) -> Unit,  // required
    modifier: Modifier = Modifier,
    showPreview: Boolean = true,
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `color` — The color of the picker.
- `onColorChanged` — The callback to be called when the color changes.
- `modifier` — The modifier to be applied to the color picker.
- `showPreview` — Whether to show a preview of the selected color.
- `hapticEffect` — The haptic effect of the [ColorSlider].

**Traps**

- 🔴 Passing pure black (Color.Black / any r=g=b=0 color) as the initial value turns the internal state into NaN. When c=0, srgbToOkhsv takes the hue direction vector as a=b=0 (Transforms.kt:193-194), and in computeMaxSaturation(0,0) f1 and f2 happen to both be 0, so s -= (f*f1)/(f1*f1 - 0.5f*f*f2) is 0/0 = NaN (Transforms.kt:413-419); the NaN spreads through findCusp/getSTMax into tMax, and in the end both s and v are NaN (h is still 0). Consequences: the value and alpha bar gradients all become black-to-black, the two sliders' indicator-ring positions are undefined, and the SideEffect can never rescue it (the selectedColor computed from NaN happens to also be black, so externalArgb == internalArgb and the sync condition short-circuits). Because s and v are both broken, dragging just one slider is still black; you must drag both saturation and value to recover. Before passing pure black, offset it a little (e.g. Color(0.004f,0.004f,0.004f)).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:413-419`)
- 🔴 Same as ColorPicker: self-holding state + SideEffect weak sync; when the external side changes color back to the last synced value it won't roll back.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:409-424`)
- 🔴 The public OkHsv data class's own KDoc is wrong, and following it will necessarily fail. The KDoc declares h as 0..360 degrees and s/v as 0..100 percent, but toColor() merely forwards the three fields as-is to Transforms.okhsvToColor, which wants three 0..1 values. In testing, OkHsv(180f, 50f, 50f).toColor() (supposedly 'a medium-saturation cyan') returns pure red #FF0000; OkHsv(0f, 100f, 100f) is also #FF0000. The correct usage is OkHsv(0.5f, 0.5f, 0.5f). The library's own OkHsvColorPicker uses 0..1, contrary to the KDoc.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/space/OkHsv.kt:9-17`)
- 🟡 OkHSV is the only one of the four spaces without a Color.toOkHsv() extension —— to convert yourself outside the Picker you can only call Transforms.colorToOkhsv(color) directly, which returns a FloatArray rather than the OkHsv data class, with all three components 0..1.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:12-37`)
- ⚪ When OkHSV's v is dragged to 0, inside okhsvToSrgb c = (c*lNew)/l is 0/0 and all three channels compute to NaN; Compose's Color(Float,...) turns NaN into 0, so the result lands as opaque black rather than a crash, but any code on this path that catches the intermediate values itself must guard against NaN.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:246-254`)

**Spec** layout Column spacedBy 12.dp: preview bar 26.dp (CircleShape) + four 26.dp sliders · order H → S → V → A

**State** Same as ColorPicker. All three internal channels are stored as 0..1 (unlike the HSV set which stores 0..360), and the initial value comes from Transforms.colorToOkhsv().

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:379`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L379)</sub>

## OkHsvHueSlider  ·  basic component

OkHSV hue slider; its background is a perceptually uniform rainbow bar of 36 segments of okhsvToColor(h,1,1) —— placed next to HsvHueSlider you can directly see the latter's light/dark banding.

> A [OkHsvHueSlider] component for selecting the hue of a color using OkHSV color space.

```kotlin
import top.yukonga.miuix.kmp.basic.OkHsvHueSlider

@Composable
fun OkHsvHueSlider(
    currentH: Float,  // required
    onHueChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentH` — The current hue value (0-1).
- `onHueChanged` — The callback to be called when the hue changes.
- `hapticEffect` — The haptic effect of the [OkHsvHueSlider].

**Traps**

- 🔴 currentH is 0..1, not an angle —— exactly the opposite of HsvHueSlider's 0..360, while the callbacks on both are 0..1. Across the whole set 'hue' has three units in all: HsvHueSlider's input uses degrees, OkHsvHueSlider / OkLchHueSlider inputs use 0..1, and the h fields of the three data classes Hsv/OkHsv/OkLch are all in degrees. Always check when copying code across families.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:497-519`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:504-508`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track 36 segments of Transforms.okhsvToColor(h, 1f, 1f), recomputed on each composition (no cache, but the call site is inside a remember)

**State** Purely controlled, no internal state, both input and output 0..1.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:504`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L504)</sub>

## OkHsvSaturationSlider  ·  basic component

OkHSV saturation slider; the gradient endpoints are computed from the actual OkHSV colors at s=0 and s=1 for the current hue, closer to the real result after dragging than the HSV version.

> A [OkHsvSaturationSlider] component for selecting the saturation of a color using OkHSV.

```kotlin
import top.yukonga.miuix.kmp.basic.OkHsvSaturationSlider

@Composable
fun OkHsvSaturationSlider(
    currentH: Float,  // required
    currentS: Float,  // required
    onSaturationChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentH` — The current hue value.
- `currentS` — The current saturation value.
- `onSaturationChanged` — The callback to be called when the saturation changes.
- `hapticEffect` — The haptic effect of the [OkHsvSaturationSlider].

**Traps**

- 🔴 currentH is 0..1 (not degrees); currentS and the callback are also 0..1. The parameter names differ from HsvSaturationSlider (currentH/currentS vs currentHue/currentSaturation), so copying named arguments directly fails to compile.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:531-550`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:531-536`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track okhsvToColor(h,0,1) → okhsvToColor(h,1,1), value locked at 1

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:531`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L531)</sub>

## OkHsvValueSlider  ·  basic component

OkHSV value slider. Unlike HsvValueSlider, both endpoints are computed live by okhsvToColor (the v=0 end is not a hardcoded pure black).

> A [OkHsvValueSlider] component for selecting the value/brightness of a color using OkHSV.

```kotlin
import top.yukonga.miuix.kmp.basic.OkHsvValueSlider

@Composable
fun OkHsvValueSlider(
    currentH: Float,  // required
    currentS: Float,  // required
    currentV: Float,  // required
    onValueChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `currentH` — The current hue value.
- `currentS` — The current saturation value.
- `currentV` — The current value value.
- `onValueChanged` — The callback to be called when the value changes.
- `hapticEffect` — The haptic effect of the [OkHsvValueSlider].

**Traps**

- 🔴 The parameter names are currentH / currentS / currentV (not currentHue / currentSaturation / currentValue), and all are 0..1.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:563-583`)
- ⚪ The gradient's left end okhsvToColor(h, s, 0f) takes exactly the v=0 0/0 branch, computing NaN which Compose folds into opaque black —— looks fine, but if you reuse Transforms.okhsvToColor yourself and inspect the return value, guard against NaN.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:246-254`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:563-569`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track okhsvToColor(h,s,0) → okhsvToColor(h,s,1)

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:563`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L563)</sub>

## OkLabAChannelSlider  ·  basic component

OkLab a channel (green←→red) slider. The track covers a ∈ [-0.3, 0.3], with 9 sample points.

> A [OkLabAChannelSlider] component for selecting the A channel (green-red axis) of a color in OkLab space.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLabAChannelSlider

@Composable
fun OkLabAChannelSlider(
    currentL: Float,  // required
    currentA: Float,  // required
    currentB: Float,  // required
    onAChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🟡 The track covers only ±0.3, while the OkLab data class allows ±0.4 and the a range actually reachable within sRGB is [-0.234, +0.276]. Although the a axis happens to fall within ±0.3, it shares the same set of constants as OkLabBChannelSlider, and the b axis does go out of bounds (see that item). Don't treat this slider's ±0.3 as OkLab a's domain.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1023-1044`)
- 🔴 Both currentA and onAChanged use the ±0.3 internal scale, not 0..1 and not the OkLab data class's ±100. Internally it converts to a slider position (currentA+0.3)/0.6 and computes back v*0.6-0.3 in the callback. Passing the wrong scale raises no error, it just sends the indicator ring outside the track.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1036-1040`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1016-1022`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track 9 sample points (steps=8), a from -0.3 to +0.3, L and b fixed

**State** Purely controlled, no internal state, both input and output the ±0.3 internal scale.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1016`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L1016)</sub>

## OkLabAlphaSlider  ·  basic component

OkLab alpha slider, with a checkerboard base. It needs the three L/a/b side channels to compute the base color.

> A [OkLabAlphaSlider] component for selecting the alpha of a color in OkLab space.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLabAlphaSlider

@Composable
fun OkLabAlphaSlider(
    currentL: Float,  // required
    currentA: Float,  // required
    currentB: Float,  // required
    currentAlpha: Float,  // required
    onAlphaChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🔴 currentL is 0..1, currentA / currentB are the ±0.4 internal scale (internally converted back to the OkLab data class's ±100 via (v/0.4f)*100f), and currentAlpha is 0..1. Three scales in the same parameter list.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1094-1101`)
- 🟡 The checkerboard color is a hardcoded light gray that doesn't follow the theme's light/dark, and can't be configured here.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1107-1108`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1086-1092`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track baseColor(alpha=0) → baseColor(alpha=1), with a 3.dp checkerboard underneath

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1086`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L1086)</sub>

## OkLabBChannelSlider  ·  basic component

OkLab b channel (blue←→yellow) slider, symmetric with the A channel, its track likewise covering only [-0.3, 0.3].

> A [OkLabBChannelSlider] component for selecting the B channel (blue-yellow axis) of a color in OkLab space.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLabBChannelSlider

@Composable
fun OkLabBChannelSlider(
    currentL: Float,  // required
    currentA: Float,  // required
    currentB: Float,  // required
    onBChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🔴 The track's ±0.3 range can't fit sRGB's b axis: pure blue #0000FF has b = -0.3115 under this OkLab, below the slider's lower bound. There are two consequences —— ① when initializing OkLabColorPicker with Color.Blue, this slider's normalized value computes to -0.019 (negative, and SliderIndicator does no clamping), so the indicator ring hangs off the left end of the track; ② once you touch this slider, b is clamped into [-0.3, 0.3] and pure blue can never be dragged back.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1058-1075`)
- 🔴 currentB and onBChanged use the ±0.3 internal scale, same as the A channel.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1071-1075`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1051-1057`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track 9 sample points (steps=8), b from -0.3 to +0.3, L and a fixed

**State** Purely controlled, no internal state, both input and output the ±0.3 internal scale.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:1051`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L1051)</sub>

## OkLabColorPicker  ·  basic component

The implementation behind ColorPicker(colorSpace = ColorSpace.OKLAB), with three Cartesian sliders (L / a green-red axis / b blue-yellow axis) plus Alpha. Good for axis-oriented tuning like 'nudge a bit toward green', not for picking a hue. Note the OkLab it uses is not standard OkLab (see below).

> A [OkLabColorPicker] component with Miuix style using OkLab color space.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLabColorPicker

@Composable
fun OkLabColorPicker(
    color: Color,  // required
    onColorChanged: (Color) -> Unit,  // required
    modifier: Modifier = Modifier,
    showPreview: Boolean = true,
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `color` — The color of the picker.
- `onColorChanged` — The callback to be called when the color changes.
- `modifier` — The modifier to be applied to the color picker.
- `showPreview` — Whether to show a preview of the selected color.
- `hapticEffect` — The haptic effect of the [ColorSlider].

**Traps**

- 🔴 The OkLab on this path skips sRGB linearization and is not the same thing as standard OkLab. Transforms contains two transforms with identical coefficients: rgbToOkLab/okLabToRgb eat the gamma-encoded sRGB components directly, while the private linearSrgbToOklab/oklabToLinearSrgb are the correct versions that linearize first. Color.toOkLab(), OkLab.toColor(), and this Picker all take the former; the OkHSV panel takes the latter. How much they differ: #808080's standard OkLab L is 0.600, computed here as 0.795 (primary-color endpoints like #FF0000 happen to agree because 0/1 are fixed points of the transfer function; the midtones differ most). The consequence is that Color → OkLab → Color round-trips consistently and works functionally, but ① the L axis is not perceptually linear, and the value slider's midpoint is not perceptual mid-gray; ② the numbers you get don't match CSS oklab() / culori / any other implementation, so don't store them in a cross-platform data format.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:30-40`)
- 🔴 a/b have only two numeric scales, but the slider-track window is a third confusing number: the OkLab data class's a/b fields are a ±100 'human scale', converted to and from the internal ±0.4 absolute values via (v/0.4f)*100f; the Picker's internal state and OkLabAChannelSlider/OkLabBChannelSlider's inputs and callbacks all use the same ±0.4 internal values, and the Picker does no conversion when passing them to the sliders. (currentA+0.3f)/0.6f merely maps the internal value to a 0..1 position on the track, with the side effect that the track covers only ±0.3 and the callback output is also clamped within ±0.3. To assemble these sliders yourself, just distinguish the two numbers '±100 data class' and '±0.4 internal value', and don't add a conversion between state and slider.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:642-659`)
- 🟡 Out-of-gamut combinations get no gamut mapping and are hard-clipped per channel with coerceIn(0,1) inside okLabToRgb. Clipping changes both lightness and hue, so pushing a or b to extremes makes the displayed color 'turn a corner' rather than simply darken/desaturate. The file actually implements full cusp/gamut-boundary computation (findCusp/getSTMax), but uses it only on the OkHSV path.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:56-60`)
- 🔴 Same as ColorPicker: self-holding state + SideEffect weak sync; when the external side changes color back to the last synced value it won't roll back.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:661-676`)

**Spec** layout Column spacedBy 12.dp: preview bar 26.dp (CircleShape) + four 26.dp sliders · order L → a → b → Alpha

**State** Same as ColorPicker. Internally it stores currentL (0..1), currentA / currentB (±0.4 internal scale, but the sliders only reach ±0.3), and currentAlpha (0..1).

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:631`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L631)</sub>

## OkLabLightnessSlider  ·  basic component

OkLab lightness slider; the gradient uses 8 sample points (steps=7) to sweep L=0..1 at the current a/b.

> A [OkLabLightnessSlider] component for selecting the lightness (L) of a color in OkLab space.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLabLightnessSlider

@Composable
fun OkLabLightnessSlider(
    currentL: Float,  // required
    currentA: Float,  // required
    currentB: Float,  // required
    onLightnessChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🔴 currentL is 0..1, and currentA / currentB are the ±0.4 internal scale, not the OkLab data class's ±100 —— passing color.toOkLab().a in directly is off by 250×, turning the whole gradient into clipped dead colors. The values OkLabAChannelSlider/OkLabBChannelSlider give you in their callbacks are exactly this internal scale (just clamped within ±0.3) and can be passed straight through.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:985-1002`)
- 🟡 The L axis is not perceptually linear (see OkLabColorPicker's first item). The gradient has only 8 sample points with sRGB linear interpolation between them, so the gradient bar itself is only an approximation.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:30-40`)
- 🟡 No modifier parameter, size hardcoded; only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:985-991`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track 8 sample points (steps=7), L from 0 to 1, a/b fixed

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:985`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L985)</sub>

## OkLchAlphaSlider  ·  basic component

OkLch alpha slider, with a checkerboard base; the base color is computed from the three L/C/H side channels.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLchAlphaSlider

@Composable
fun OkLchAlphaSlider(
    currentL: Float,  // required
    currentC: Float,  // required
    currentH: Float,  // required
    currentAlpha: Float,  // required
    onAlphaChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🔴 currentL / currentC / currentH are all 0..1 (currentC is a fraction of 0.4, currentH is a fraction of 360°, and internally it multiplies by the coefficients itself).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:953-968`)
- ⚪ The transparent end is reconstructed with Color(r,g,b,0f) rather than baseColor.copy(alpha=0f) —— the two are equivalent here, but it's inconsistent with the other three families' style, so don't assume it has any special meaning when editing the code.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:964-968`)
- 🟡 The checkerboard color is a hardcoded light gray that doesn't follow the theme's light/dark; no KDoc, no modifier parameter, size hardcoded, only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:970-978`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track transparent → opaque current OkLch color, with a 3.dp checkerboard underneath

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:954`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L954)</sub>

## OkLchChromaSlider  ·  basic component

OkLch chroma slider, a two-point gradient from gray (C=0) to C=0.4.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLchChromaSlider

@Composable
fun OkLchChromaSlider(
    currentL: Float,  // required
    currentC: Float,  // required
    currentH: Float,  // required
    onChromaChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🔴 currentL / currentC / currentH are all 0..1 (currentH is a fraction, not degrees). The onChromaChanged callback also gives a 0..1 fraction, not the 0..0.4 absolute chroma.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:907-929`)
- 🟡 The right endpoint uses an absolute chroma of 0.4, beyond sRGB's reachable ~0.3225, so the rightmost segment of the track's gradient is already clipped color, and dragging to the end may look about the same as dragging to 80%.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:916-921`)
- 🟡 No KDoc, no modifier parameter, size hardcoded, only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:907-914`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track two-point gradient oklchToColor(L, 0, h*360) → oklchToColor(L, 0.4, h*360)

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:908`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L908)</sub>

## OkLchColorPicker  ·  basic component

The implementation behind ColorPicker(colorSpace = ColorSpace.OKLCH), the polar form of OkLab: lightness / chroma / hue / alpha. Use this when you want to 'keep lightness fixed and only change hue'; it is the handiest of the four spaces for deriving theme colors. The slider order is H → L → C → A, different from the other three spaces.

> A [OkLchColorPicker] component with Miuix style using OkLch color space.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLchColorPicker

@Composable
fun OkLchColorPicker(
    color: Color,  // required
    onColorChanged: (Color) -> Unit,  // required
    modifier: Modifier = Modifier,
    showPreview: Boolean = true,
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

- `color` — The color of the picker.
- `onColorChanged` — The callback to be called when the color changes.
- `modifier` — The modifier to be applied to the color picker.
- `showPreview` — Whether to show a preview of the selected color.
- `hapticEffect` — The haptic effect of the [ColorSlider].

**Traps**

- 🔴 The underlying OkLab likewise skips sRGB linearization (sharing colorToOkLab/okLabToRgb with OkLabColorPicker), so the L and C here are not standard OkLch values and don't match CSS oklch(). Don't store the result of Color.toOkLch() as interoperable numbers.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:30-40`)
- 🟡 The chroma cap is hardcoded to 0.4, but the maximum chroma actually reachable in sRGB is only about 0.3225 (at pure magenta). That means the rightmost ~19% of the chroma slider's travel is entirely out of gamut, and dragging into it only triggers per-channel clipping —— the color no longer gets more vivid, and instead the lightness and hue both distort.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:483-490`)
- 🔴 Same as ColorPicker: self-holding state + SideEffect weak sync; when the external side changes color back to the last synced value it won't roll back.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:791-806`)
- ⚪ The slider order has hue on top, then lightness, then chroma, unlike HSV/OkHSV's H→S→V and OkLab's L→a→b. When building a UI with four tabs side by side, the row positions don't line up.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:830-877`)

**Spec** layout Column spacedBy 12.dp: preview bar 26.dp (CircleShape) + four 26.dp sliders · order H → L → C → Alpha

**State** Same as ColorPicker. All three internal channels are normalized to 0..1: currentL is L/100, currentC is the chroma as a fraction of 0.4, and currentH is angle/360. Note these are three different numbers from the OkLch data class (l 0..100, c 0..100, h 0..360 degrees).

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:761`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L761)</sub>

## OkLchHueSlider  ·  basic component

OkLch hue slider; its background sweeps 36 hue sample points at the current lightness/chroma —— so its rainbow bar varies with L and C, and at low chroma the whole bar approaches gray. The only slider in the whole set with a global cache.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLchHueSlider

@Composable
fun OkLchHueSlider(
    currentL: Float,  // required
    currentC: Float,  // required
    currentH: Float,  // required
    onHueChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🔴 currentH is a 0..1 fraction (not degrees), and currentL / currentC are also 0..1. The callback is likewise 0..1.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:932-950`)
- 🟡 The background is generated by Transforms.generateOkLchHueColors, a public function that internally carries a never-cleared, non-thread-safe global mutableMapOf cache, keyed on a string built from L and C each multiplied by 100 and rounded. Dragging the L/C sliders keeps stuffing entries in (upper bound about 101×101 combinations × 36 Colors). Of the three hue-generation functions only this one added a cache; the other two recompute every time.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:461-481`)
- ⚪ The cache key quantizes L and C to 1/100, so while dragging L/C the hue bar's background changes in discrete steps (only every time it crosses 1%), not as a continuous transition.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:470-478`)
- 🟡 No KDoc, no modifier parameter, size hardcoded, only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:932-939`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track 36 segments of oklchToColor(L, C*0.4, i/36*360), varying with the current L/C

**State** Purely controlled, no internal state.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:933`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L933)</sub>

## OkLchLightnessSlider  ·  basic component

OkLch lightness slider; the gradient is a two-point linear gradient of L from 0 to 1 at the current chroma/hue.

```kotlin
import top.yukonga.miuix.kmp.basic.OkLchLightnessSlider

@Composable
fun OkLchLightnessSlider(
    currentL: Float,  // required
    currentC: Float,  // required
    currentH: Float,  // required
    onLightnessChanged: (Float) -> Unit,  // required
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
)
```

**Traps**

- 🔴 All three inputs are 0..1: currentL is the lightness fraction, currentC is the chroma as a fraction of 0.4 (not the 0..0.4 absolute value; internally it multiplies by 0.4), and currentH is the hue as a fraction of 360° (not degrees). None of the OkLch data class's three fields (0..100 / 0..100 / 0..360) can be passed in directly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:882-905`)
- 🟡 The gradient has only two endpoints (L=0 and L=1) with sRGB linear interpolation, not OkLch interpolation, in between, so the color in the middle of the gradient bar doesn't match the color you actually get by dragging to that position (the chroma comes out lower).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:891-896`)
- 🟡 None of the OkLch family's four sliders have KDoc (unlike the Hsv/OkHsv families), and none have a modifier parameter; the size is hardcoded, and there is only a drag gesture, no tap gesture.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:881-888`)

**Spec** size fillMaxWidth × 26.dp (fixed) · track two-point gradient oklchToColor(0, c*0.4, h*360) → oklchToColor(1, c*0.4, h*360)

**State** Purely controlled, no internal state, the three inputs and the callback are all 0..1.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt:882`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ColorPicker.kt#L882)</sub>

## Color.toHsv  ·  api

Converts a Compose Color to human-scale HSV (h 0..360, s/v 0..100), with Hsv.toColor(alpha) to convert back. The whole top.yukonga.miuix.kmp.color package has zero coverage in the official docs.

> Convert Compose Color to Hvs.

```kotlin
import top.yukonga.miuix.kmp.color.api.toHsv

fun Color.toHsv(): Hsv
```

**Traps**

- 🟡 The two scales differ by a factor of 100. The extension function Color.toHsv() returns s/v as 0..100, while the underlying Transforms.colorToHsv() returns 0..1; feeding Transforms' output into the Hsv(...) constructor gives an almost fully black color, and the reverse gets clamped to 100 by coerceIn. Confirm the scale before mixing the two layers.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:25`)
- 🟡 Before conversion the channels are truncated to 8-bit integers using (color.red * 255).toInt() (floor, not rounding), so color.toHsv().toColor() does not round-trip exactly, off by at most 1/255. For a lossless round-trip do not take this path.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:173`)
- 🟡 alpha is completely discarded: toHsv() does not read color.alpha, and Hsv.toColor()'s alpha defaults to 1f. A semi-transparent color becomes opaque after a round-trip, so you must pass the alpha back yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/space/Hsv.kt:16`)
- 🟡 The related OkHsv has no Color.toOkHsv() extension function (you can only call Transforms yourself), and OkHsv.toColor() forwards h/s/v as-is to Transforms.okhsvToColor -- which expects a 0..1 scale, inconsistent with the convention of the three classes Hsv/OkLab/OkLch that all divide by 100 first. Filling OkHsv per the KDoc's 0..360/0..100 gives the wrong color.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/space/OkHsv.kt:16`)

**State** A pure function, stateless. Hsv is a data class with equals, so it can safely be used as a remember key or placed in State.

**vs Material3** No counterpart. material3 provides no color-space conversion; the platform's android.graphics.Color.colorToHSV exists only on Android and uses a 0..1 scale for s/v, so it cannot be substituted directly.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:22`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt#L22)</sub>

## Color.toOkLab  ·  api

Converts a Compose Color to human-scale OkLab (l 0..100, a/b -100..100), used for perceptually uniform lightness/chroma adjustments, then converted back with OkLab.toColor().

> Convert Compose Color to user-friendly OkLab.

```kotlin
import top.yukonga.miuix.kmp.color.api.toOkLab

fun Color.toOkLab(): OkLab
```

**Traps**

- 🟡 The scale is custom: a/b's -100..100 maps to OkLab's native -0.4..0.4, and Transforms.colorToOkLab() is what returns the native scale. Mixing the two layers is off by a factor of 250.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:16`)
- 🟡 All three components l/a/b are hard-clamped by coerceIn. Colors outside the typical sRGB range (a/b absolute value over 0.4) are silently clamped, do not round-trip faithfully, and give no information about "how far out of range" they were.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:17`)
- 🟡 alpha discarded: toOkLab() does not read color.alpha, and OkLab.toColor() defaults alpha = 1f. A semi-transparent color becomes opaque after a round-trip.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/space/OkLab.kt:16`)
- ⚪ The input is unconditionally treated as sRGB: the underlying code takes color.red/green/blue directly for the matrix transform without any color-space conversion. Passing a Color with a non-sRGB ColorSpace (such as DisplayP3) gives a wrong result without erroring.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:117`)

**State** A pure function, stateless. OkLab is a data class.

**vs Material3** No counterpart. material3 internally uses HCT (via MaterialKolor's Hct), a different perceptual color space from OkLab, and the values are not interchangeable.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:13`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt#L13)</sub>

## Color.toOkLch  ·  api

Converts a Compose Color to human-scale OkLCh (l 0..100, c 0..100, h 0..360 degrees), used for operations like "keep lightness, only shift hue"; converted back with OkLch.toColor().

> Convert Compose Color to user-friendly OkLch.

```kotlin
import top.yukonga.miuix.kmp.color.api.toOkLch

fun Color.toOkLch(): OkLch
```

**Traps**

- 🟡 chroma is clamped twice. The underlying Transforms.colorToOklch first clamps c into 0..0.4, then the extension function multiplies by 100/0.4 -- so any highly saturated color whose native chroma exceeds 0.4 comes out as c == 100, and different highly saturated colors get the same c value, indistinguishable.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/core/Transforms.kt:126`)
- 🟡 The scales are inconsistent, and the conversion factors of the two components differ: the extension function returns l/c both as 0..100, while Transforms.colorToOklch returns l as 0..1 (off by 100x, `lch[0] * 100f`) and c as 0..0.4 (off by 250x, `lch[1] / 0.4f * 100f`). Feeding Transforms' raw output directly into OkLch(...) gives an almost fully black and colorless color.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:33`)
- 🟡 alpha discarded: toOkLch() does not read color.alpha, and OkLch.toColor() defaults alpha = 1f.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/space/OkLch.kt:16`)
- ⚪ h has already been %360'd and negative-corrected in Transforms, and OkLch.toColor() does it again -- so passing an h over 360 or negative is safe and does not error, but do not expect it to preserve turn-count information (e.g. crossing 360 jumps abruptly during a hue-interpolation animation).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/space/OkLch.kt:19`)

**State** A pure function, stateless. OkLch is a data class.

**vs Material3** No counterpart, for the same reason as Color.toOkLab.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt:31`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/color/api/Extensions.kt#L31)</sub>

## Public types in this topic (6)

- `ColorSpace` **enum** — HSV, OKHSV, OKLAB, OKLCH · `import top.yukonga.miuix.kmp.basic.ColorSpace`
- `Hsv(h: Float, s: Float, v: Float)` **data class** (required: h, s, v) · `import top.yukonga.miuix.kmp.color.space.Hsv`
- `OkHsv(h: Float, s: Float, v: Float)` **data class** (required: h, s, v) · `import top.yukonga.miuix.kmp.color.space.OkHsv`
- `OkLab(l: Float, a: Float, b: Float)` **data class** (required: l, a, b) · `import top.yukonga.miuix.kmp.color.space.OkLab`
- `OkLch(l: Float, c: Float, h: Float)` **data class** (required: l, c, h) · `import top.yukonga.miuix.kmp.color.space.OkLch`
- `Transforms` **object** · `import top.yukonga.miuix.kmp.color.core.Transforms`

